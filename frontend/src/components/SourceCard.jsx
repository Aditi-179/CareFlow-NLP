import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, FileText, CheckCircle2 } from 'lucide-react';

export default function SourceCard({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return (
      <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600 flex items-center gap-1.5 italic">
        <span>No matching documents retrieved in knowledge base. Response generated with standard clinical guidance.</span>
      </div>
    );
  }

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-xs font-semibold text-slate-600 hover:text-sky-700 transition-colors py-1 group"
      >
        <div className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-teal-600" />
          <span>Retrieved Evidence ({sources.length} clinical source chunk{sources.length > 1 ? 's' : ''})</span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-slate-600 group-hover:text-sky-600">
          <span>{expanded ? 'Hide Excerpts' : 'View Context'}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Pill summary of sources */}
      <div className="flex flex-wrap gap-1.5 mt-1.5">
        {sources.map((src, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-teal-50 text-teal-800 border border-teal-200/80 font-medium"
          >
            <FileText className="w-3 h-3 text-teal-600" />
            <span>{src.document}</span>
            <span className="text-[10px] text-teal-600 font-bold ml-0.5">
              ({Math.round(src.score * 100)}% match)
            </span>
          </span>
        ))}
      </div>

      {/* Detailed collapsible chunks */}
      {expanded && (
        <div className="mt-2.5 space-y-2">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="text-xs p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 font-mono leading-relaxed"
            >
              <div className="flex items-center justify-between font-sans font-semibold text-slate-800 pb-1 mb-1 border-b border-slate-200/60">
                <span className="text-[11px] text-teal-700">{src.document} → {src.section}</span>
                <span className="text-[10px] px-1.5 py-0.2 bg-teal-100/70 text-teal-800 rounded font-bold">
                  Score: {src.score}
                </span>
              </div>
              <p className="text-[11px] whitespace-pre-line text-slate-600 font-sans">
                {src.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

