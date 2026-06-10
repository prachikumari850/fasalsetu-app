import { cn } from '../../utils/cn';

interface AvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizes = {
  sm: 'h-7 w-7 text-xs',
  md: 'h-9 w-9 text-sm',
  lg: 'h-11 w-11 text-base',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

function getColor(name: string): string {
  const colors = [
    'bg-primary-100 text-primary-800',
    'bg-amber-100 text-amber-800',
    'bg-blue-100 text-blue-800',
    'bg-purple-100 text-purple-800',
    'bg-rose-100 text-rose-800',
  ];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

export function Avatar({ name, size = 'md', className }: AvatarProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full font-semibold flex-shrink-0',
        sizes[size],
        getColor(name),
        className
      )}
      aria-label={name}
    >
      {getInitials(name)}
    </div>
  );
}