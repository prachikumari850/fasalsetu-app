import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
export function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <p className="text-5xl font-bold text-ink">404</p>
      <p className="text-ink-secondary">Page not found.</p>
      <Button onClick={() => navigate('/')} variant="outlined" fullWidth={false}>Go Home</Button>
    </div>
  );
}