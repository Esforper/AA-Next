// src/components/buttons/FloatingActionButton.tsx
// Flutter FloatingActionButton (FAB) benzeri

import React from 'react';
import clsx from 'clsx';

export interface FloatingActionButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  size?: 'md' | 'lg';
  variant?: 'primary' | 'secondary';
  extended?: boolean;
  label?: string;
  className?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  icon,
  onClick,
  size = 'md',
  variant = 'primary',
  extended = false,
  label,
  className,
  position = 'bottom-right',
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        // Base styles
        'inline-flex items-center justify-center gap-2',
        'font-semibold shadow-lg',
        'transition-all duration-300 ease-out',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'hover:shadow-2xl active:scale-95',
        
        // Shape
        {
          'rounded-full': !extended,
          'rounded-2xl': extended,
        },
        
        // Variant styles
        {
          'bg-aa-blue text-white hover:bg-aa-blue-dark focus:ring-aa-blue':
            variant === 'primary',
          'bg-gray-700 text-white hover:bg-gray-800 focus:ring-gray-500':
            variant === 'secondary',
        },
        
        // Size styles
        {
          'w-14 h-14 text-xl': size === 'md' && !extended,
          'w-16 h-16 text-2xl': size === 'lg' && !extended,
          'px-6 py-4 text-base': extended,
        },
        
        // Position (if used as fixed positioned)
        position && {
          'fixed z-50': true,
          'bottom-6 right-6': position === 'bottom-right',
          'bottom-6 left-6': position === 'bottom-left',
          'top-6 right-6': position === 'top-right',
          'top-6 left-6': position === 'top-left',
        },
        
        className
      )}
    >
      {icon}
      {extended && label && (
        <span>{label}</span>
      )}
    </button>
  );
};

