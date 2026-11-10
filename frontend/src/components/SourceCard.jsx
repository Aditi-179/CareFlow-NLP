import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, FileText, Globe, ExternalLink } from 'lucide-react';

export default function SourceCard({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const localSources = sources.filter(s => s.source_type !== 'web');
  const webSources = sources.filter(s => s.source_type === 'web');

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-xs font-semibold text-slate-600 hover:text-sky-700 transition-colors py-1 group"
      >
        <div className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-teal-600" />
          <span>
            Retrieved Evidence ({sources.length} clinical reference{sources.length > 1 ? 's' : ''})
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-slate-500 group-hover:text-sky-600">
          <span>{expanded ? 'Hide Details' : 'Inspect Evidence'}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Pill summary of sources */}
      <div className="flex flex-wrap gap-1.5 mt-2">
        {localSources.map((src, i) => (
          <span
            key={`local-${i}`}
            className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-teal-50 text-teal-800 border border-teal-200/80 font-medium"
          >
            <FileText className="w-3 h-3 text-teal-600" />
            <span>{src.document}</span>
            <span className="text-[10px] text-teal-600 font-bold ml-0.5">
              ({Math.round(src.score * 100)}%)
            </span>
          </span>
        ))}

        {webSources.map((src, i) => (
          <a
            key={`web-${i}`}
            href={src.url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200/80 font-medium hover:bg-sky-100 transition-colors"
          >
            <Globe className="w-3 h-3 text-sky-600" />
            <span className="truncate max-w-[150px]">{src.document}</span>
            <ExternalLink className="w-2.5 h-2.5 text-sky-500 ml-0.5" />
          </a>
        ))}
      </div>

      {/* Detailed collapsible chunks */}
      {expanded && (
        <div className="mt-3 space-y-2">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="text-xs p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed"
            >
              <div className="flex items-center justify-between font-medium text-slate-800 pb-1 mb-1.5 border-b border-slate-200/60">
                <div className="flex items-center gap-1.5">
                  {src.source_type === 'web' ? (
                    <Globe className="w-3.5 h-3.5 text-sky-600" />
                  ) : (
                    <FileText className="w-3.5 h-3.5 text-teal-600" />
                  )}
                  <span className="text-[11px] font-semibold text-slate-800">
                    {src.document} {src.section ? `→ ${src.section}` : ''}
                  </span>
                </div>
                {src.url ? (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] text-sky-600 hover:underline flex items-center gap-0.5"
                  >
                    <span>Visit source</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                ) : (
                  <span className="text-[10px] px-1.5 py-0.2 bg-teal-100 text-teal-800 rounded font-bold">
                    Relevance: {src.score}
                  </span>
                )}
              </div>
              <p className="text-[11.5px] whitespace-pre-line text-slate-600 font-sans">
                {src.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
