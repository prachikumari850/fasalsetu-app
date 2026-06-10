import { useState } from 'react';
import { Bars3Icon, BellIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../hooks/useAuth';
import { Avatar } from '../ui/Avatar';

interface NavbarProps {
  onMenuClick: () => void;
  title: string;
}

export function Navbar({ onMenuClick, title }: NavbarProps) {
  const { user } = useAuth();

  return (
    <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-4 flex-shrink-0">
      {/* Left */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-1.5 rounded-lg text-ink-secondary hover:bg-muted"
          aria-label="Open menu"
        >
          <Bars3Icon className="h-5 w-5" />
        </button>
        <h1 className="text-base font-semibold text-ink truncate">{title}</h1>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        <button className="relative p-1.5 rounded-lg text-ink-secondary hover:bg-muted">
          <BellIcon className="h-5 w-5" />
        </button>
        {user && <Avatar name={user.full_name} size="sm" />}
      </div>
    </header>
  );
}