import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type FormData = z.infer<typeof schema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? '/';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    await login(data.email, data.password);
    navigate(from, { replace: true });
  };

  return (
    <div className="p-7">
      <h2 className="text-xl font-bold text-ink mb-1">Welcome back</h2>
      <p className="text-sm text-ink-secondary mb-6">Sign in to your portal</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <Input
          label="Email Address"
          type="email"
          placeholder="officer@fasalsetu.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          error={errors.password?.message}
          {...register('password')}
        />
        <Button
          type="submit"
          fullWidth
          isLoading={isSubmitting}
          className="mt-2"
        >
          Sign In
        </Button>
      </form>

      <p className="text-xs text-ink-hint text-center mt-6">
        FasalSetu — PMFBY Smart Verification Platform
      </p>
    </div>
  );
}