import React from 'react';

export default function AgentCard({ selectedAgent }) {
  const agents = [
    { id: 'rag', name: 'RAG Agent', desc: 'Adaptive RAG inside RAG Agent: Dense + BM25, Reranking, Rewrite' },
    { id: 'web', name: 'Web Agent', desc: 'Current web research, source extraction, synthesis' },
    { id: 'code', name: 'Code Agent', desc: 'Python coding, algorithm design, AST syntax verification' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      {agents.map((ag) => {
        const isActive = selectedAgent === ag.id;
        return (
          <div
            key={ag.id}
            className={`p-3 rounded-xl border transition-all ${
              isActive
                ? 'bg-cyan-950/40 border-cyan-500 shadow-lg shadow-cyan-950/50 scale-[1.02]'
                : 'bg-slate-900 border-slate-800 opacity-60'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-xs uppercase tracking-wider text-slate-200">{ag.name}</span>
              {isActive && (
                <span className="text-[10px] bg-cyan-400 text-slate-950 font-bold px-2 py-0.5 rounded uppercase">
                  ACTIVE
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">{ag.desc}</p>
          </div>
        );
      })}
    </div>
  );
}
