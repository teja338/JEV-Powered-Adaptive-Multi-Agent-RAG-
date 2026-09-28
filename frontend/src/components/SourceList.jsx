import React from 'react';

export default function SourceList({ sources = [] }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 mb-4 text-slate-100">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
        Retrieved Context & Grounding Sources ({sources.length})
      </h4>
      <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
        {sources.map((src, idx) => (
          <div key={idx} className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="font-semibold text-cyan-300 truncate max-w-[250px]">{src.title || src.url_or_file}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                src.source_type === 'document' ? 'bg-blue-900/60 text-blue-300' : 'bg-emerald-900/60 text-emerald-300'
              }`}>
                {src.source_type}
              </span>
            </div>
            <p className="text-slate-300 line-clamp-3 font-mono text-[11px] bg-slate-950 p-2 rounded mt-1">
              {src.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
