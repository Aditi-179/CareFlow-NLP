import React from 'react';
import { Activity, ShieldCheck, Trash2, Cpu, Database } from 'lucide-react';

export default function Header({ health, onClearChat, messageCount }) {
  const isHealthy = health && health.status === 'healthy';
  const totalDocs = health?.knowledge_base?.total_documents || 5;
  const totalChunks = health?.knowledge_base?.total_chunks || 0;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-5xl mx-auto px-4 py-3 sm:px-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
            <Activity className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-900">CareFlow <span className="text-sky-600 font-extrabold">NLP</span></h1>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
                Unit 6 LLM
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Healthcare Query Understanding & Intelligent Response System</p>
          </div>
        </div>

        {/* Status badges & controls */}
        <div className="flex items-center gap-2.5 flex-wrap self-end sm:self-center">
          {/* Engine indicator */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200/80">
            <Cpu className="w-3.5 h-3.5 text-sky-600" />
            <span className="hidden md:inline text-slate-500">Model:</span>
            <span className="font-semibold text-slate-800">{health?.llm_model || 'Groq LLaMA 3.3'}</span>
          </div>

          {/* Knowledge base stats */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200/80">
            <Database className="w-3.5 h-3.5 text-teal-600" />
            <span>{totalDocs} docs</span>
            {totalChunks > 0 && <span className="text-slate-400">({totalChunks} chunks)</span>}
          </div>

          {/* Connection status */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border bg-slate-50">
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
            <span className={isHealthy ? 'text-emerald-700' : 'text-amber-700'}>
              {isHealthy ? 'Online' : 'Connecting...'}
            </span>
          </div>

          {/* Clear conversation button */}
          {messageCount > 0 && (
            <button
              onClick={onClearChat}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition-colors"
              title="Clear active conversation"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

