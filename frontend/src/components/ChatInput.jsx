import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative rounded-2xl bg-white border border-slate-300 shadow-sm focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-500/20 transition-all flex items-end p-1.5">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask a healthcare question (e.g., 'What are the symptoms of Type 2 diabetes?')..."
          rows={1}
          className="w-full resize-none bg-transparent px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-32 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="shrink-0 p-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white disabled:opacity-40 disabled:hover:bg-sky-600 transition-all shadow-xs cursor-pointer disabled:cursor-not-allowed"
          title="Send query"
        >
          {disabled ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>
      <div className="flex items-center justify-between px-3 mt-1.5 text-[11px] text-slate-600">
        <span>Press <kbd className="font-mono bg-slate-100 px-1 py-0.5 rounded border border-slate-200">Enter</kbd> to submit, <kbd className="font-mono bg-slate-100 px-1 py-0.5 rounded border border-slate-200">Shift+Enter</kbd> for newline</span>
        <span>RAG grounded on verified medical docs</span>
      </div>
    </form>
  );
}

