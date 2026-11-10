import React from 'react';
import { Sparkles } from 'lucide-react';

const SUGGESTIONS = [
  { text: "What are the common symptoms of diabetes?", category: "Diabetes" },
  { text: "What is hypertension and how is it classified?", category: "Hypertension" },
  { text: "Explain the difference between Type 1 and Type 2 diabetes.", category: "Diabetes" },
  { text: "What lifestyle changes can help manage high blood pressure?", category: "Hypertension" },
  { text: "What are the common risk factors associated with cardiovascular diseases?", category: "Cardiovascular Health" },
  { text: "What is the importance of regular blood glucose monitoring?", category: "Diabetes" },
  { text: "What is the role of dietary fiber and the DASH diet in nutrition?", category: "Nutrition" },
  { text: "What are the red-flag symptoms requiring emergency medical evaluation?", category: "Symptoms" }
];

export default function SuggestedQuestions({ onSelectQuestion, disabled }) {
  return (
    <div className="w-full">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2.5">
        <Sparkles className="w-3.5 h-3.5 text-sky-500" />
        <span>Try asking clinical questions</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            disabled={disabled}
            onClick={() => onSelectQuestion(item.text)}
            className="text-left text-xs p-2.5 rounded-xl border border-slate-200/90 bg-white hover:bg-sky-50/70 hover:border-sky-300 transition-all text-slate-700 shadow-xs hover:shadow-sm group flex flex-col justify-between gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="font-medium group-hover:text-sky-900 leading-snug">{item.text}</span>
            <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider bg-slate-100 group-hover:bg-sky-100 group-hover:text-sky-700 px-1.5 py-0.5 rounded self-start">
              {item.category}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

