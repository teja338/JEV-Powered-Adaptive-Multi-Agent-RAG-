import React from 'react';

export default function ExecutionTrace({ execution = [] }) {
  if (!execution || execution.length === 0) return null;

  const getStepStatusBadge = (status) => {
    switch (status) {
      case 'completed':
      case 'passed':
        return <span className="text-emerald-400 font-bold">✓</span>;
      case 'failed':
      case 'warning':
        return <span className="text-amber-400 font-bold">⚠</span>;
      case 'running':
        return <span className="text-cyan-400 animate-spin">⏳</span>;
      default:
        return <span className="text-slate-500">•</span>;
    }
  };

  const formatStepName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-100 mb-4">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
        Dynamic Execution Graph & Trace
      </h4>
      <div className="space-y-2">
        {execution.map((item, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 p-2 rounded bg-slate-800/40 border border-slate-700/30 text-xs"
          >
            <div className="mt-0.5">{getStepStatusBadge(item.status)}</div>
            <div className="flex-1">
              <span className="font-semibold text-slate-200">{formatStepName(item.step)}</span>
              {item.details && (
                <div className="text-slate-400 mt-1 font-mono text-[11px] bg-slate-950 p-1.5 rounded border border-slate-800">
                  {JSON.stringify(item.details)}
                </div>
              )}
            </div>
            <span className="text-[10px] text-slate-500 uppercase font-mono">{item.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
