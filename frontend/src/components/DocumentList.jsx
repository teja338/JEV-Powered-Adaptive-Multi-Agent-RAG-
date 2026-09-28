import React, { useState, useEffect } from 'react';
import { uploadDocument, getDocuments, deleteDocument } from '../services/api';

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDocs = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      await fetchDocs();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id);
      await fetchDocs();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 text-slate-100 shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100">Document Dashboard</h2>
          <p className="text-xs text-slate-400">Upload PDFs for RAG Knowledge Base</p>
        </div>
        <label className="cursor-pointer bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs px-4 py-2 rounded-lg transition-colors shadow">
          {uploading ? 'Processing PDF...' : '+ Upload PDF Document'}
          <input type="file" accept=".pdf" onChange={handleFileUpload} disabled={uploading} className="hidden" />
        </label>
      </div>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs p-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
            No PDF documents indexed yet. Upload a document to start RAG retrieval.
          </div>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex justify-between items-center">
              <div>
                <div className="font-semibold text-sm text-slate-200">{doc.filename}</div>
                <div className="text-xs text-slate-400 mt-0.5 flex gap-3">
                  <span>Chunks: <strong className="text-cyan-400">{doc.chunk_count}</strong></span>
                  <span>Status: <span className="text-emerald-400 font-medium uppercase">{doc.status}</span></span>
                </div>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-xs text-rose-400 hover:text-rose-300 bg-rose-950/40 hover:bg-rose-900/60 px-3 py-1.5 rounded border border-rose-800 transition"
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
