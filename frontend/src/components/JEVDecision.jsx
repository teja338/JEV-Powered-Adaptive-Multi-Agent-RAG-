import React from 'react';

export default function JEVDecision({ decision, reDecisions = [] }) {
  if (!decision) return null;

  const getAgentBadgeColor = (agent) => {
    switch (agent) {
      case 'rag': return 'bg-blue-600 text-blue-100 border-blue-400';
      case 'web': return 'bg-emerald-600 text-emerald-100 border-emerald-400';
      case 'code': return 'bg-purple-600 text-purple-100 border-purple-400';
      default: return 'bg-gray-600 text-gray-100';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 shadow-lg text-slate-100 mb-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
          <h3 className="font-semibold text-cyan-300 tracking-wide text-sm uppercase">JEV DECISION PANEL</h3>
        </div>
        {decision.is_fallback ? (
          <span className="text-xs bg-amber-900/60 text-amber-300 px-2 py-0.5 rounded border border-amber-700">
            Decision Source: Fallback Router (JEV Unavailable)
          </span>
        ) : (
          <span className="text-xs bg-cyan-900/60 text-cyan-300 px-2 py-0.5 rounded border border-cyan-700">
            Decision Source: OpenRouter JEV Model
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-medium">Selected Agent</div>
          <div className="flex items-center gap-2 mt-1">
            <span className={`px-2.5 py-1 text-xs font-bold uppercase rounded border ${getAgentBadgeColor(decision.agent)}`}>
              {decision.agent} Agent
            </span>
          </div>
        </div>

        <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-medium">JEV Confidence</div>
          {decision.is_fallback ? (
            <div className="text-sm font-semibold text-amber-400 mt-1">N/A (Fallback Used)</div>
          ) : (
            <div className="text-lg font-bold text-cyan-400 mt-0.5">{(decision.confidence * 100).toFixed(1)}%</div>
          )}
        </div>

        <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-medium">Decision Rationale</div>
          <div className="text-xs text-slate-300 mt-1 line-clamp-2">
            {decision.reasoning || "JEV structured decision evaluation"}
          </div>
        </div>
      </div>

      {reDecisions.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-800">
          <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
            ⚠ JEV Re-Decisions Triggered
          </div>
          <div className="space-y-2">
            {reDecisions.map((rd, idx) => (
              <div key={idx} className="bg-amber-950/40 border border-amber-800/60 rounded-lg p-2.5 text-xs flex justify-between items-center">
                <div>
                  <span className="text-amber-200 font-medium">Re-Decision #{idx + 1}:</span> Switch to{' '}
                  <span className="font-bold text-amber-300 uppercase">{rd.agent} Agent</span>
                </div>
                <div className="text-amber-400 font-mono">
                  {rd.is_fallback ? "Fallback Router" : `${(rd.confidence * 100).toFixed(1)}% JEV confidence`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
