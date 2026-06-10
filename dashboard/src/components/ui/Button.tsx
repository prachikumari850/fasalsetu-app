import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '../../utils/cn';
import { Spinner } from './Spinner';

type Variant = 'primary' | 'secondary' | 'outlined' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

const variants: Record<Variant, string> = {
  primary:   'bg-primary-700 text-white hover:bg-primary-800 active:bg-primary-900 disabled:bg-primary-300',
  secondary: 'bg-secondary text-white hover:bg-secondary-dark active:bg-secondary-dark disabled:opacity-50',
  outlined:  'border border-primary-700 text-primary-700 hover:bg-primary-50 active:bg-primary-100 disabled:opacity-50',
  ghost:     'text-ink-secondary hover:bg-muted active:bg-border disabled:opacity-50',
  danger:    'bg-danger text-white hover:bg-red-700 active:bg-red-800 disabled:opacity-50',
};

const sizes: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs rounded-lg gap-1.5',
  md: 'px-4 py-2 text-sm rounded-lg gap-2',
  lg: 'px-6 py-3 text-base rounded-xl gap-2',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      className,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-700 focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed',
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {isLoading ? (
          <Spinner size="sm" className="border-current border-t-transparent" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = 'Button';