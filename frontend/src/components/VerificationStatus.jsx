import React from 'react';

export default function VerificationStatus({ verification }) {
  if (!verification || Object.keys(verification).length === 0) return null;

  const isSufficient = verification.sufficient;

  return (
    <div className={`border rounded-xl p-4 mb-4 text-slate-100 ${
      isSufficient ? 'bg-emerald-950/30 border-emerald-800' : 'bg-rose-950/30 border-rose-800'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Agent Evidence Verification
        </h4>
        <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
          isSufficient ? 'bg-emerald-900 text-emerald-200 border border-emerald-700' : 'bg-rose-900 text-rose-200 border border-rose-700'
        }`}>
          {isSufficient ? 'VERIFIED SUFFICIENT' : 'INSUFFICIENT EVIDENCE'}
        </span>
      </div>

      <div className="text-xs space-y-2">
        {verification.coverage !== undefined && (
          <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded border border-slate-800">
            <span className="text-slate-400">Context Coverage Score:</span>
            <span className="font-bold text-cyan-400 font-mono">{(verification.coverage * 100).toFixed(1)}%</span>
          </div>
        )}

        {verification.reason && (
          <div className="text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-800">
            <span className="text-slate-400 block mb-0.5">Verification Analysis:</span>
            {verification.reason}
          </div>
        )}

        {verification.missing_information && verification.missing_information.length > 0 && (
          <div className="bg-rose-900/40 p-2 rounded border border-rose-800">
            <span className="text-rose-300 font-semibold block mb-1">Missing Evidence Items:</span>
            <ul className="list-disc list-inside text-rose-200 space-y-0.5">
              {verification.missing_information.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
