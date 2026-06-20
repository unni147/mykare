import React from 'react';

interface ActivityPanelProps {
  logs: string[];
}

export default function ActivityPanel({ logs }: ActivityPanelProps) {
  return (
    <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col h-96">
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-100">
        <h3 className="font-semibold text-slate-700">Tool Activity</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {logs.length === 0 ? (
          <p className="text-slate-400 text-center italic text-sm mt-10">No activity yet...</p>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0"></div>
              <p className="text-slate-600">{log}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
