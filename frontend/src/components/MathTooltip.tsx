'use client';

import React, { useState } from 'react';

interface CalculationTrace {
  formula: string;
  variables: Record<string, string>;
  source: string;
}

interface MathTooltipProps {
  trace: CalculationTrace | null | undefined;
  children: React.ReactNode;
}

export function MathTooltip({ trace, children }: MathTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  if (!trace) {
    return <>{children}</>;
  }

  return (
    <div
      className="relative inline-flex items-center gap-1 cursor-pointer group"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onClick={() => setIsVisible(true)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
      tabIndex={0}
      role="button"
      aria-expanded={isVisible}
      aria-label="View calculation details"
    >
      {children}
      <span className="opacity-50 hover:opacity-100 transition-opacity ml-0.5">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 16v-4"></path>
          <path d="M12 8h.01"></path>
        </svg>
      </span>

      {isVisible && (
        <div 
          className="absolute z-50 w-72 max-w-[85vw] p-4 mt-2 bg-white border border-gray-200 rounded-xl shadow-2xl top-full left-0 cursor-auto"
          style={{
            color: '#111827',
            fontSize: '14px',
            lineHeight: '1.5',
            letterSpacing: 'normal',
            fontWeight: '400',
            fontFamily: 'ui-sans-serif, system-ui, sans-serif',
            textAlign: 'left',
            textTransform: 'none',
            whiteSpace: 'normal',
            wordSpacing: 'normal',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-3">
            <h4 className="font-semibold text-gray-900 mb-1" style={{ fontSize: '14px', margin: '0 0 4px 0' }}>Deterministic Calculation</h4>
            <div 
              className="p-2 bg-gray-50 rounded border border-gray-100"
              style={{
                fontSize: '12px',
                lineHeight: '1.4',
                fontFamily: 'ui-monospace, monospace',
                wordBreak: 'break-word',
                color: '#374151'
              }}
            >
              {trace.formula}
            </div>
          </div>

          <div className="mb-3">
            <h4 className="font-semibold text-gray-900 mb-1" style={{ fontSize: '14px', margin: '0 0 4px 0' }}>Variables</h4>
            <ul className="space-y-1" style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {Object.entries(trace.variables).map(([key, val]) => (
                <li key={key} style={{ fontSize: '12px', lineHeight: '1.4', color: '#4b5563', margin: '4px 0' }}>
                  <span className="font-semibold text-gray-800" style={{ fontFamily: 'ui-monospace, monospace' }}>{key}:</span> {val}
                </li>
              ))}
            </ul>
          </div>

          <div className="border-t border-gray-100 pt-2 mt-2" style={{ fontSize: '11px', color: '#6b7280', lineHeight: '1.4' }}>
            <strong className="font-semibold">Source:</strong> {trace.source}
          </div>
        </div>
      )}
    </div>
  );
}
