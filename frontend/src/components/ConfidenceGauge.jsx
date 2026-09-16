import React, { useEffect, useState } from 'react';

export default function ConfidenceGauge({ value, size = 120 }) {
  const [offset, setOffset] = useState(0);
  
  const strokeWidth = 10;
  const radius = (size / 2) - strokeWidth;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.round(value * 100);
  
  useEffect(() => {
    // Initial animation
    const timeout = setTimeout(() => {
      setOffset(circumference - (value * circumference));
    }, 100);
    return () => clearTimeout(timeout);
  }, [value, circumference]);
  
  // Determine color based on value
  let color = '#ef4444'; // red-500
  if (value >= 0.8) color = '#22c55e'; // green-500
  else if (value >= 0.5) color = '#eab308'; // yellow-500

  return (
    <div className="relative inline-flex items-center justify-center flex-col">
      <svg 
        width={size} 
        height={size} 
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#f3f4f6"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Foreground arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset || circumference}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold" style={{ color }}>
          {percentage}%
        </span>
        <span className="text-xs text-gray-500 font-medium">Точность</span>
      </div>
    </div>
  );
}
