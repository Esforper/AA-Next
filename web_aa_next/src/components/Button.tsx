// src/components/Button.tsx
// Enhanced Button component inspired by Flutter Material Design

import React from 'react';
import clsx from 'clsx';

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'text';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className,
  type = 'button',
  icon,
  iconPosition = 'left',
  fullWidth = false,
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={clsx(
        // Base styles - Flutter Material Design inspired
        'inline-flex items-center justify-center gap-2',
        'font-semibold rounded-xl',
        'transition-all duration-200 ease-out',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'active:scale-[0.98]',
        
        // Variant styles
        {
          // Primary - AA Blue (Flutter primary color)
          'bg-aa-blue text-white hover:bg-aa-blue-dark focus:ring-aa-blue shadow-sm hover:shadow-md': 
            variant === 'primary',
          
          // Secondary - Gray (Flutter secondary color)
          'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 shadow-sm hover:shadow-md': 
            variant === 'secondary',
          
          // Outline - Border style (Flutter OutlinedButton)
          'border-2 border-aa-blue text-aa-blue hover:bg-aa-blue/5 focus:ring-aa-blue': 
            variant === 'outline',
          
          // Ghost - Minimal style (Flutter TextButton)
          'text-aa-blue hover:bg-aa-blue/10 focus:ring-aa-blue': 
            variant === 'ghost',
          
          // Text - Pure text button
          'text-gray-700 hover:bg-gray-100 focus:ring-gray-400': 
            variant === 'text',
        },
        
        // Size styles (Flutter padding values)
        {
          'px-3 py-1.5 text-sm min-h-[36px]': size === 'sm',
          'px-6 py-3 text-base min-h-[44px]': size === 'md',
          'px-8 py-4 text-lg min-h-[52px]': size === 'lg',
        },
        
        // Width
        {
          'w-full': fullWidth,
        },
        
        // Disabled styles
        {
          'opacity-50 cursor-not-allowed pointer-events-none': isDisabled,
        },
        
        className
      )}
    >
      {/* Loading spinner */}
      {loading && (
        <svg
          className="animate-spin h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      
      {/* Icon left */}
      {!loading && icon && iconPosition === 'left' && (
        <span className="flex-shrink-0">{icon}</span>
      )}
      
      {/* Text content */}
      <span>{children}</span>
      
      {/* Icon right */}
      {!loading && icon && iconPosition === 'right' && (
        <span className="flex-shrink-0">{icon}</span>
      )}
    </button>
  );
};