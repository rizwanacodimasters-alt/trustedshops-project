import React from 'react';
import { AlertCircle } from 'lucide-react';

export const FormError = ({ message }) => {
  if (!message) return null;
  
  return (
    <div className="flex items-center gap-2 text-red-600 text-sm mt-1">
      <AlertCircle className="w-4 h-4" />
      <span>{message}</span>
    </div>
  );
};

export const FormSuccess = ({ message }) => {
  if (!message) return null;
  
  return (
    <div className="flex items-center gap-2 text-green-600 text-sm mt-1">
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
      <span>{message}</span>
    </div>
  );
};

export const PasswordStrengthIndicator = ({ strength }) => {
  if (!strength) return null;
  
  const colors = {
    weak: 'bg-red-500',
    medium: 'bg-yellow-500',
    strong: 'bg-green-500'
  };
  
  const widths = {
    weak: 'w-1/3',
    medium: 'w-2/3',
    strong: 'w-full'
  };
  
  return (
    <div className="mt-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-600">Passwortstärke:</span>
        <span className={`text-xs font-medium ${
          strength.level === 'weak' ? 'text-red-600' :
          strength.level === 'medium' ? 'text-yellow-600' :
          'text-green-600'
        }`}>{strength.label}</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full ${colors[strength.level]} ${widths[strength.level]} transition-all duration-300`}></div>
      </div>
    </div>
  );
};
