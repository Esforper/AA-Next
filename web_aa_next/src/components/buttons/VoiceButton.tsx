// src/components/buttons/VoiceButton.tsx
// Flutter VoiceButton'a benzer - Audio toggle butonu

import React from 'react';
import clsx from 'clsx';

export interface VoiceButtonProps {
  speaking: boolean;
  onToggle: () => void;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  speaking,
  onToggle,
  size = 'md',
  className,
}) => {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={speaking ? 'Sesi Kapat' : 'Sesi Aç'}
      className={clsx(
        // Base styles - circular button with semi-transparent background
        'inline-flex items-center justify-center rounded-full',
        'bg-black/45 backdrop-blur-sm',
        'transition-all duration-200 ease-in-out',
        'hover:bg-black/60 active:scale-95',
        'focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-transparent',
        
        // Size styles
        {
          'w-10 h-10 p-2': size === 'sm',
          'w-12 h-12 p-3': size === 'md',
          'w-14 h-14 p-3.5': size === 'lg',
        },
        
        className
      )}
    >
      {speaking ? (
        // Volume Off Icon
        <svg
          className="w-7 h-7 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
          />
        </svg>
      ) : (
        // Volume Up Icon
        <svg
          className="w-7 h-7 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
          />
        </svg>
      )}
    </button>
  );
};

