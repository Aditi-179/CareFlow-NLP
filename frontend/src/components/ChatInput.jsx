import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Globe, Paperclip, FileText, X } from 'lucide-react';

export default function ChatInput({
  onSendMessage,
  onUploadReport,
  webSearchEnabled,
  onToggleWebSearch,
  disabled
}) {
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (disabled) return;

    if (selectedFile) {
      onUploadReport(selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    if (!text.trim()) return;
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

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  return (
    <div className="relative">
      {/* File Preview Badge if file selected */}
      {selectedFile && (
        <div className="mb-2 p-2 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-between text-xs text-teal-900 shadow-2xs">
          <div className="flex items-center gap-2 truncate">
            <FileText className="w-4 h-4 text-teal-600 shrink-0" />
            <span className="font-semibold truncate">{selectedFile.name}</span>
            <span className="text-[11px] text-teal-600">({Math.round(selectedFile.size / 1024)} KB)</span>
          </div>
          <button
            onClick={handleRemoveFile}
            className="p-1 hover:bg-teal-100 rounded text-teal-700 transition-colors"
            title="Remove report"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative rounded-2xl bg-white border border-slate-300 shadow-sm focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-500/20 transition-all flex flex-col p-2">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || selectedFile !== null}
          placeholder={
            selectedFile
              ? "Report attached! Click Send to extract biomarkers & analyze findings..."
              : "Ask a healthcare question (e.g. 'What are the symptoms of Type 2 diabetes?')..."
          }
          rows={1}
          className="w-full resize-none bg-transparent px-2.5 py-1.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-32 disabled:opacity-70"
        />

        {/* Toolbar Footer */}
        <div className="flex items-center justify-between pt-1.5 border-t border-slate-100 mt-1">
          <div className="flex items-center gap-1.5">
            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.csv,.md"
              onChange={handleFileChange}
              className="hidden"
            />

            {/* Upload Report Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-slate-600 hover:text-teal-700 hover:bg-teal-50 border border-slate-200/90 transition-all"
              title="Upload Medical Report (.pdf, .txt, .csv)"
            >
              <Paperclip className="w-3.5 h-3.5 text-teal-600" />
              <span>Upload Report</span>
            </button>

            {/* Web Search Toggle Button */}
            <button
              type="button"
              onClick={onToggleWebSearch}
              disabled={disabled}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all ${
                webSearchEnabled
                  ? 'bg-sky-50 text-sky-700 border-sky-300 font-semibold shadow-2xs'
                  : 'bg-white text-slate-600 hover:text-sky-600 hover:bg-slate-50 border-slate-200/90'
              }`}
              title="Toggle Live Web Search augmentation"
            >
              <Globe className={`w-3.5 h-3.5 ${webSearchEnabled ? 'text-sky-600' : 'text-slate-400'}`} />
              <span>Web Search: {webSearchEnabled ? 'ON' : 'OFF'}</span>
            </button>
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={(!text.trim() && !selectedFile) || disabled}
            className="shrink-0 px-3.5 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white disabled:opacity-40 disabled:hover:bg-sky-600 transition-all shadow-xs cursor-pointer disabled:cursor-not-allowed flex items-center gap-1.5 text-xs font-semibold"
          >
            {disabled ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{selectedFile ? 'Analyze Report' : 'Send'}</span>
                <Send className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </form>

      <div className="flex items-center justify-between px-3 mt-1.5 text-[11px] text-slate-600">
        <span>Press <kbd className="font-mono bg-slate-100 px-1 py-0.5 rounded border border-slate-200">Enter</kbd> to submit</span>
        <span>RAG grounded on verified medical docs & live research</span>
      </div>
    </div>
  );
}
