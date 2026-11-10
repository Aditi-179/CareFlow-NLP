import React from 'react';
import { User, Activity, Tag, Check, AlertCircle } from 'lucide-react';
import SourceCard from './SourceCard';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-2.5 my-3">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-xs bg-sky-600 text-white px-4 py-3 shadow-xs">
          <p className="text-sm font-normal leading-relaxed whitespace-pre-wrap">{message.content}</p>
          <div className="flex items-center justify-end gap-1 mt-1 text-[10px] text-sky-200">
            <span>{message.timestamp || 'Just now'}</span>
          </div>
        </div>
        <div className="w-8 h-8 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center shrink-0 border border-sky-200 shadow-xs">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  // Assistant Message
  return (
    <div className="flex items-start gap-2.5 my-4">
      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-600 to-teal-500 text-white flex items-center justify-center shrink-0 shadow-xs">
        <Activity className="w-4 h-4 stroke-[2.2]" />
      </div>

      <div className="max-w-[92%] sm:max-w-[85%] rounded-2xl rounded-tl-xs bg-white border border-slate-200/90 p-4 shadow-xs text-slate-800">
        {/* NLP Metadata header (Category, Confidence, Negations) */}
        <div className="flex flex-wrap items-center gap-1.5 pb-2.5 mb-2.5 border-b border-slate-100">
          {message.category && (
            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">
              <Tag className="w-3 h-3 text-sky-600" />
              <span>Category: <strong>{message.category}</strong></span>
              {message.category_confidence && (
                <span className="text-sky-500 font-normal">({Math.round(message.category_confidence * 100)}%)</span>
              )}
            </div>
          )}

          {message.has_negation && message.negations_found?.length > 0 && (
            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span>Negation preserved: <strong>"{message.negations_found.join(', ')}"</strong></span>
            </div>
          )}

          {message.model_used && (
            <span className="text-[10px] text-slate-600 ml-auto font-mono">
              via {message.model_used}
            </span>
          )}
        </div>

        {/* Formatted Answer Body */}
        <div className="text-sm leading-relaxed text-slate-700 whitespace-pre-line space-y-2">
          {message.content}
        </div>

        {/* Source References & Retrieved Context */}
        <SourceCard sources={message.sources} />

        {/* Medical disclaimer note */}
        {message.disclaimer && (
          <p className="mt-2 text-[10px] text-slate-600 border-t border-slate-100 pt-2 italic">
            {message.disclaimer}
          </p>
        )}
      </div>
    </div>
  );
}

