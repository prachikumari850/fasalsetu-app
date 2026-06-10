import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import type { User, AuthContextValue } from '../types/auth';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = 'fs_token';
const USER_KEY = 'fs_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? (JSON.parse(stored) as User) : null;
  });
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem(TOKEN_KEY)
  );
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Verify token on mount
  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await authService.getMe();
        // Only officers and admins can access the dashboard
        if (me.role === 'farmer') {
          toast.error('Farmer accounts cannot access this dashboard.');
          logout();
          return;
        }
        setUser(me);
        localStorage.setItem(USER_KEY, JSON.stringify(me));
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    };
    verify();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

 const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login(email, password);
      const { access_token, user: loggedInUser } = response;

      if (loggedInUser.role === 'farmer') {
        toast.error('Farmer accounts cannot access this dashboard.');
        return;
      }

      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(loggedInUser));
      setToken(access_token);
      setUser(loggedInUser);
      toast.success(`Welcome back, ${loggedInUser.full_name}!`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const value: AuthContextValue = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated: !!token && !!user,
    isOfficer: user?.role === 'officer',
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
}