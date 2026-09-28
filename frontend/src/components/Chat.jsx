import React, { useState } from 'react';
import { sendChatMessage } from '../services/api';
import JEVDecision from '../components/JEVDecision';
import ExecutionTrace from '../components/ExecutionTrace';
import VerificationStatus from '../components/VerificationStatus';
import SourceList from '../components/SourceList';
import AgentCard from '../components/AgentCard';

export default function Chat() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await sendChatMessage(query);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Agent Visualization */}
      <AgentCard selectedAgent={result?.decision?.agent} />

      {/* Query Form */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question (e.g. 'According to my uploaded PDF, explain Self-RAG', 'What are the latest developments in LangChain?', 'Write Python code for binary search')"
          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3.5 pr-28 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 shadow-inner"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 top-2 bottom-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 font-bold px-5 rounded-lg text-xs uppercase tracking-wider transition shadow"
        >
          {loading ? 'Routing...' : 'Execute'}
        </button>
      </form>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs p-3 rounded-xl">
          {error}
        </div>
      )}

      {/* Structured Output Dashboard */}
      {result && (
        <div className="space-y-4">
          <JEVDecision decision={result.decision} reDecisions={result.re_decisions} />
          
          <ExecutionTrace execution={result.execution} />

          <VerificationStatus verification={result.verification} />

          <SourceList sources={result.sources} />

          {/* Generated Answer */}
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 shadow-lg">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Final Grounded Answer
            </h3>
            <div className="prose prose-invert max-w-none text-slate-200 text-sm whitespace-pre-wrap leading-relaxed">
              {result.answer || "No response generated."}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
