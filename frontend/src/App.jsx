import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import MedicalDisclaimer from './components/MedicalDisclaimer';
import SuggestedQuestions from './components/SuggestedQuestions';
import MessageBubble from './components/MessageBubble';
import ChatInput from './components/ChatInput';
import { sendHealthcareQuery, fetchHealthStatus } from './services/api';
import { Bot, AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  // Poll backend health status on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    const data = await fetchHealthStatus();
    setHealth(data);
  };

  // Auto-scroll chat smoothly
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (userText) => {
    if (!userText.trim() || loading) return;

    setError(null);
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append user message immediately
    const userMsg = {
      role: 'user',
      content: userText,
      timestamp
    };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      const response = await sendHealthcareQuery(userText, updatedMessages);
      
      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        category: response.category,
        category_confidence: response.category_confidence,
        matched_keywords: response.matched_keywords,
        has_negation: response.has_negation,
        negations_found: response.negations_found,
        sources: response.sources || [],
        disclaimer: response.disclaimer,
        model_used: response.model_used,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Error querying backend:', err);
      setError(err.message || 'Unable to connect to the healthcare NLP server.');
      // Append error message from assistant
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error: ${err.message || 'The server could not process this request.'} Please ensure the FastAPI backend is running and the Groq API key is valid.`,
          category: 'System Alert',
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Header */}
      <Header
        health={health}
        onClearChat={handleClearChat}
        messageCount={messages.length}
      />

      {/* Medical Safety Disclaimer banner */}
      <MedicalDisclaimer />

      {/* Main Chat Conversation Container */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 flex flex-col justify-between">
        <div className="flex-1 overflow-y-auto pb-4">
          {/* Welcome view when chat is empty */}
          {messages.length === 0 ? (
            <div className="py-8 sm:py-12 flex flex-col items-center text-center max-w-2xl mx-auto space-y-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-500 to-teal-400 text-white flex items-center justify-center shadow-lg shadow-sky-500/25">
                <Bot className="w-9 h-9 stroke-[1.8]" />
              </div>
              
              <div className="space-y-2">
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Healthcare Clinical Intelligence
                </h2>
                <p className="text-sm text-slate-600 max-w-lg leading-relaxed">
                  CareFlow NLP combines dense vector semantic search (<span className="font-semibold text-slate-800">Sentence Transformers + FAISS</span>) 
                  with Groq LLM inference to provide factual, grounded answers from a curated clinical knowledge base.
                </p>
              </div>

              {/* Syllabus feature pills */}
              <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] font-medium text-slate-600">
                <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 shadow-2xs">Tokenization & Cleaning</span>
                <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 shadow-2xs">Medical Negation Retention</span>
                <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 shadow-2xs">Intent Classification</span>
                <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 shadow-2xs">384-d FAISS Vectors</span>
                <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 shadow-2xs">Grounded Groq RAG</span>
              </div>

              {/* Suggested starter questions */}
              <div className="w-full pt-4 text-left">
                <SuggestedQuestions
                  onSelectQuestion={handleSendMessage}
                  disabled={loading}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <MessageBubble key={index} message={msg} />
              ))}

              {loading && (
                <div className="flex items-start gap-2.5 my-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-600 to-teal-500 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Bot className="w-4 h-4 animate-pulse" />
                  </div>
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-xs text-xs text-slate-500 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-sky-500 animate-ping" />
                    <span>Searching FAISS vector index & generating grounded response...</span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Floating / Bottom Input Area */}
        <div className="sticky bottom-0 bg-slate-50 pt-3 pb-2 z-20">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={loading}
          />
        </div>
      </main>
    </div>
  );
}

