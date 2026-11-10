import React, { useState } from 'react';
import { AlertTriangle, X, ShieldAlert } from 'lucide-react';

export default function MedicalDisclaimer() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-amber-50/90 border-b border-amber-200/80 px-4 py-2.5 text-xs text-amber-900 transition-all">
      <div className="max-w-5xl mx-auto flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold uppercase tracking-wider text-[11px] text-amber-800 mr-1.5">
              Medical Disclaimer:
            </span>
            <span>
              CareFlow NLP is an academic educational system demonstrating Retrieval-Augmented Generation (RAG). 
              It does not diagnose medical conditions, recommend specific medication dosages, or substitute professional healthcare judgment. 
              <strong> If you are experiencing acute medical distress (such as crushing chest pain or severe breathlessness), please contact emergency medical services immediately.</strong>
            </span>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-amber-700 hover:text-amber-900 p-0.5 rounded hover:bg-amber-100 transition-colors shrink-0"
          title="Dismiss notice"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

