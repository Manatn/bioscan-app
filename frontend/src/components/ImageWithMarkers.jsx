import React, { useRef, useState, useEffect } from 'react';

export default function ImageWithMarkers({ imageSrc, markers = [], severity }) {
  const containerRef = useRef(null);
  const imgRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!containerRef.current || !imgRef.current) return;
    
    const updateDimensions = () => {
      if (imgRef.current) {
        setDimensions({
          width: imgRef.current.clientWidth,
          height: imgRef.current.clientHeight
        });
      }
    };
    
    const observer = new ResizeObserver(() => {
      updateDimensions();
    });
    
    observer.observe(containerRef.current);
    imgRef.current.addEventListener('load', updateDimensions);
    
    updateDimensions();
    
    return () => {
      observer.disconnect();
      if (imgRef.current) {
        imgRef.current.removeEventListener('load', updateDimensions);
      }
    };
  }, [imageSrc]);

  const getColorBySeverity = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'жоғары': return '#ef4444';
      case 'орташа': return '#f97316';
      case 'төмен': return '#eab308';
      case 'сау': return '#22c55e';
      default: return '#3b82f6';
    }
  };

  const markerColor = getColorBySeverity(severity);

  return (
    <div ref={containerRef} className="relative inline-block max-w-full">
      <img 
        ref={imgRef}
        src={imageSrc} 
        alt="Талданған өсімдік" 
        className="max-w-full rounded-xl block"
      />
      {dimensions.width > 0 && dimensions.height > 0 && markers.length > 0 && (
        <svg 
          style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%',
            pointerEvents: 'none'
          }}
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
        >
          {markers.map((marker, index) => {
            const [ymin, xmin, ymax, xmax] = marker.box_2d;
            const width = xmax - xmin;
            const height = ymax - ymin;
            
            return (
              <g key={index}>
                <rect
                  x={xmin}
                  y={ymin}
                  width={width}
                  height={height}
                  fill={`${markerColor}33`}
                  stroke={markerColor}
                  strokeWidth="3"
                  rx="4"
                />
                {marker.label && (
                  <text
                    x={xmin}
                    y={Math.max(20, ymin - 10)}
                    fill="white"
                    fontSize="24"
                    fontWeight="bold"
                    filter="url(#solid-bg)"
                    paintOrder="stroke"
                    stroke={markerColor}
                    strokeWidth="8"
                    strokeLinejoin="round"
                  >
                    {marker.label}
                  </text>
                )}
              </g>
            );
          })}
          <defs>
            <filter id="solid-bg" x="0" y="0" width="1" height="1">
              <feFlood floodColor={markerColor} />
              <feComposite in="SourceGraphic" in2="flood" operator="over" />
            </filter>
          </defs>
        </svg>
      )}
    </div>
  );
}
