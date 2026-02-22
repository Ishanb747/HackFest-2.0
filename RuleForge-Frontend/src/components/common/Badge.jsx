import React from 'react';
import './Badge.css';

function Badge({ children, variant = 'default', size = 'sm' }) {
  return (
    <span className={`badge ${variant} ${size}`}>
      {children}
    </span>
  );
}

export default Badge;
