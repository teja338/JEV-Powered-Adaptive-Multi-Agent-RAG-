import React, { useState } from 'react';
import Chat from './components/Chat';
import DocumentList from './components/DocumentList';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500 flex items-center justify-center font-black text-slate-950 text-base shadow-lg shadow-cyan-500/30">
              JEV
            </div>
            <div>
              <h1 className="font-bold text-slate-100 text-sm tracking-wide">
                JEV-Powered Adaptive Multi-Agent RAG
              </h1>
              <p className="text-[11px] text-slate-400">Decision-First AI Agent Router</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'chat'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Agent Workspace & Chat
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'documents'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              PDF Document Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        {activeTab === 'chat' ? <Chat /> : <DocumentList />}
      </main>
    </div>
  );
}
