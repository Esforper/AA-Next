// src/components/buttons/IconButton.tsx
// Flutter IconButton'a benzer circular icon button

import React from 'react';
import clsx from 'clsx';

export interface IconButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  tooltip?: string;
  'aria-label'?: string;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  onClick,
  variant = 'ghost',
  size = 'md',
  disabled = false,
  className,
  tooltip,
  'aria-label': ariaLabel,
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={tooltip}
      aria-label={ariaLabel || tooltip}
      className={clsx(
        // Base styles - circular button
        'inline-flex items-center justify-center rounded-full',
        'transition-all duration-200 ease-in-out',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'active:scale-95',
        
        // Variant styles
        {
          'bg-aa-blue text-white hover:bg-aa-blue-dark focus:ring-aa-blue shadow-sm': 
            variant === 'primary',
          'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-400': 
            variant === 'secondary',
          'text-gray-600 hover:bg-gray-100 focus:ring-gray-400': 
            variant === 'ghost',
          'bg-red-500 text-white hover:bg-red-600 focus:ring-red-400 shadow-sm': 
            variant === 'danger',
        },
        
        // Size styles
        {
          'w-8 h-8 text-sm': size === 'sm',
          'w-10 h-10 text-base': size === 'md',
          'w-12 h-12 text-lg': size === 'lg',
        },
        
        // Disabled styles
        {
          'opacity-50 cursor-not-allowed pointer-events-none': disabled,
        },
        
        className
      )}
    >
      {icon}
    </button>
  );
};

