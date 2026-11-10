import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Activity, Tag, FileSpreadsheet, Globe, FileText, AlertCircle, CheckCircle, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import SourceCard from './SourceCard';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-2.5 my-3">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-xs bg-sky-600 text-white px-4 py-3 shadow-xs">
          {message.isReportUpload && (
            <div className="flex items-center gap-1.5 text-xs font-semibold text-sky-100 pb-1.5 mb-1.5 border-b border-sky-500/50">
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Uploaded Report: {message.filename}</span>
            </div>
          )}
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

      <div className="max-w-[95%] sm:max-w-[85%] rounded-2xl rounded-tl-xs bg-white border border-slate-200 p-4 sm:p-5 shadow-xs text-slate-800">
        {/* NLP Metadata header (Category, Confidence, Negations, Web Search badge) */}
        <div className="flex flex-wrap items-center gap-1.5 pb-2.5 mb-3 border-b border-slate-100">
          {message.category && (
            <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">
              <Tag className="w-3 h-3 text-sky-600" />
              <span>Category: <strong>{message.category}</strong></span>
              {message.category_confidence && (
                <span className="text-sky-500 font-normal">({Math.round(message.category_confidence * 100)}%)</span>
              )}
            </div>
          )}

          {message.web_searched && (
            <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
              <Globe className="w-3 h-3 text-indigo-500" />
              <span>Live Web Grounded</span>
            </div>
          )}

          {message.has_negation && message.negations_found?.length > 0 && (
            <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span>Negation preserved: <strong>"{message.negations_found.join(', ')}"</strong></span>
            </div>
          )}

          {message.model_used && (
            <span className="text-[10px] text-slate-600 ml-auto font-mono">
              via {message.model_used}
            </span>
          )}
        </div>

        {/* Lab Biomarkers Grid (If Medical Report Analysis) */}
        {message.biomarkers && message.biomarkers.length > 0 && (
          <div className="mb-4 p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-2">
              <FileSpreadsheet className="w-4 h-4 text-teal-600" />
              <span>Extracted Lab Biomarkers ({message.biomarkers.length} identified)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.biomarkers.map((b, i) => {
                const isElevated = b.status === 'Elevated';
                const isLow = b.status === 'Low';
                const isNormal = b.status === 'Normal';

                return (
                  <div key={i} className="p-2 rounded-lg bg-white border border-slate-200 flex items-center justify-between gap-2 shadow-2xs">
                    <div>
                      <div className="text-xs font-semibold text-slate-800">{b.name}</div>
                      <div className="text-[11px] text-slate-500">Ref: {b.normal_range}</div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs font-bold text-slate-900">{b.value} <span className="text-[10px] font-normal text-slate-500">{b.unit}</span></div>
                      <span className={`inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                        isElevated ? 'bg-amber-100 text-amber-800' :
                        isLow ? 'bg-sky-100 text-sky-800' :
                        'bg-emerald-100 text-emerald-800'
                      }`}>
                        {isElevated && <ArrowUpCircle className="w-3 h-3 text-amber-600" />}
                        {isLow && <ArrowDownCircle className="w-3 h-3 text-sky-600" />}
                        {isNormal && <CheckCircle className="w-3 h-3 text-emerald-600" />}
                        <span>{b.status}</span>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Natural Markdown Formatted Body */}
        <div className="text-sm leading-relaxed text-slate-700 prose prose-slate max-w-none prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-li:my-0.5">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ node, ...props }) => (
                <div className="overflow-x-auto my-3 rounded-lg border border-slate-200">
                  <table className="w-full text-xs text-left border-collapse" {...props} />
                </div>
              ),
              thead: ({ node, ...props }) => (
                <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200" {...props} />
              ),
              th: ({ node, ...props }) => (
                <th className="px-3 py-2 text-slate-700 font-semibold border-r border-slate-200 last:border-r-0" {...props} />
              ),
              td: ({ node, ...props }) => (
                <td className="px-3 py-2 border-t border-slate-200 border-r border-slate-200 last:border-r-0" {...props} />
              ),
              ul: ({ node, ...props }) => (
                <ul className="list-disc pl-5 space-y-1 my-2" {...props} />
              ),
              ol: ({ node, ...props }) => (
                <ol className="list-decimal pl-5 space-y-1 my-2" {...props} />
              ),
              li: ({ node, ...props }) => (
                <li className="text-slate-700 leading-normal" {...props} />
              ),
              p: ({ node, ...props }) => (
                <p className="my-2 leading-relaxed" {...props} />
              ),
              strong: ({ node, ...props }) => (
                <strong className="font-semibold text-slate-900" {...props} />
              ),
              h2: ({ node, ...props }) => (
                <h2 className="text-base font-bold text-slate-900 mt-3 mb-1.5" {...props} />
              ),
              h3: ({ node, ...props }) => (
                <h3 className="text-sm font-bold text-slate-900 mt-2.5 mb-1" {...props} />
              ),
              a: ({ node, ...props }) => (
                <a className="text-sky-600 hover:text-sky-800 underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />
              )
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Source References & Retrieved Context */}
        <SourceCard sources={message.sources} />

        {/* Medical disclaimer note */}
        {message.disclaimer && (
          <p className="mt-2.5 text-[10px] text-slate-600 border-t border-slate-100 pt-2 italic">
            {message.disclaimer}
          </p>
        )}
      </div>
    </div>
  );
}
