import React from 'react';

const ClaimLayerAudit = ({ data }) => {
  if (!data || !data.validated_evidence) return null;

  const { cl_result, inference, validated_evidence } = data;
  const hasVeto = inference?.accepted === true;

  return (
    <div className="mt-8 glass-panel rounded-xl p-6 overflow-hidden relative">
      {/* Background Accent */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16 blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Evidence Intelligence Audit</h3>
            <p className="text-xs text-gray-400">Deterministic ClaimLayer Resolution Engine</p>
          </div>
        </div>
        <span className="claim-badge claim-badge-deterministic">Validated</span>
      </div>

      {/* Veto Logic Section */}
      {hasVeto && (
        <div className="mb-6 p-4 bg-red-500/5 border border-red-500/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="claim-badge claim-badge-veto">Epistemological Veto</span>
            <span className="text-xs font-medium text-red-400">Conflict Resolved</span>
          </div>
          <p className="text-sm text-gray-300">
            <strong>Inferred Fact:</strong> {inference.inferred_fact}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-red-500" 
                style={{ width: `${(inference.confidence || 0) * 100}%` }}
              ></div>
            </div>
            <span className="text-[10px] text-gray-500">Confidence: {(inference.confidence || 0).toFixed(4)}</span>
          </div>
        </div>
      )}

      {/* Validated Evidence Rows */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Epistemic State (E_t)</h4>
        {validated_evidence.map((evidence, idx) => (
          <div key={idx} className="flex gap-3 items-start p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
            <div className="text-[10px] font-mono text-blue-500 mt-1">[{idx + 1}]</div>
            <div className="text-sm text-gray-300 leading-relaxed">
              {evidence.replace(/^- /, '')}
            </div>
          </div>
        ))}
      </div>

      {/* Mathematical Justification Footer */}
      <div className="mt-6 flex items-center justify-between text-[10px] text-gray-600 italic">
        <span>* Claims resolved via Cosine Similarity thresholding & Semantic Firewall.</span>
        <span>Build: DeepRare-EI 1.0.0</span>
      </div>
    </div>
  );
};

export default ClaimLayerAudit;
