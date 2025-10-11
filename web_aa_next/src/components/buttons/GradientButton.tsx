// src/components/buttons/GradientButton.tsx
// Flutter CategoryBubbleMenu gibi gradient button

import React from 'react';
import clsx from 'clsx';

export interface GradientButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  icon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
  disabled?: boolean;
  className?: string;
  variant?: 'primary' | 'accent' | 'success';
  fullWidth?: boolean;
}

export const GradientButton: React.FC<GradientButtonProps> = ({
  children,
  onClick,
  icon,
  trailingIcon = (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  ),
  disabled = false,
  className,
  variant = 'primary',
  fullWidth = false,
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        // Base styles
        'group relative overflow-hidden rounded-2xl',
        'transition-all duration-300 ease-out',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'active:scale-[0.98]',
        
        // Gradient backgrounds
        {
          'bg-gradient-to-br from-aa-blue to-aa-blue-dark shadow-lg hover:shadow-xl focus:ring-aa-blue':
            variant === 'primary',
          'bg-gradient-to-br from-blue-500 to-blue-700 shadow-lg hover:shadow-xl focus:ring-blue-400':
            variant === 'accent',
          'bg-gradient-to-br from-green-500 to-green-700 shadow-lg hover:shadow-xl focus:ring-green-400':
            variant === 'success',
        },
        
        // Width
        {
          'w-full': fullWidth,
          'w-auto': !fullWidth,
        },
        
        // Disabled styles
        {
          'opacity-50 cursor-not-allowed pointer-events-none': disabled,
        },
        
        className
      )}
    >
      {/* Hover effect overlay */}
      <div className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-colors duration-300" />
      
      {/* Content */}
      <div className="relative flex items-center justify-between gap-3 px-6 py-4">
        {/* Left side */}
        <div className="flex items-center gap-3">
          {icon && (
            <div className="text-white text-xl">
              {icon}
            </div>
          )}
          <span className="text-white font-bold text-base">
            {children}
          </span>
        </div>
        
        {/* Right side - trailing icon */}
        {trailingIcon && (
          <div className="text-white flex-shrink-0">
            {trailingIcon}
          </div>
        )}
      </div>
    </button>
  );
};

