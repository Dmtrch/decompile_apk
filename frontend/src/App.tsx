import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Shield, Zap, FileText, CheckCircle, AlertTriangle, Loader2, Download, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = "http://localhost:8000/api/v1";

interface Scorecard {
  summary: {
    security_score: number;
    total_findings: number;
    high_risks: number;
    warnings: number;
    generated_at: string;
  };
  findings: Array<{
    source: string;
    severity: string;
    message: string;
    location: string;
  }>;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [report, setReport] = useState<Scorecard | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState<number | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<Record<number, any>>({});

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const { data } = await axios.post(`${API_BASE}/upload`, formData);
      setJobId(data.job_id);
      setStatus('processing');
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Make sure backend is running.");
    }
    setLoading(false);
  };

  const handleAIExplain = async (idx: number, finding: any) => {
    setAiLoading(idx);
    try {
      const { data } = await axios.post(`${API_BASE}/ai/explain`, {
        code_snippet: "/* Code context from decompiler would go here */",
        issue_description: finding.message
      });
      setAiAnalysis(prev => ({ ...prev, [idx]: data }));
    } catch (e) {
      alert("AI Service unreachable. Make sure Ollama is running.");
    }
    setAiLoading(null);
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (jobId && status === 'processing') {
      interval = setInterval(async () => {
        try {
          const { data } = await axios.get(`${API_BASE}/report/${jobId}`);
          if (data.summary) {
            setReport(data);
            setStatus('completed');
            clearInterval(interval);
          }
        } catch (e) {
          // Still processing
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  return (
    <div className="min-h-screen bg-background text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-12">
          <div className="flex items-center gap-3">
            <div className="bg-primary p-2 rounded-lg">
              <Shield className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Decompile & Audit APK</h1>
          </div>
          <div className="text-slate-400 text-sm">v1.0.0 Prototype</div>
        </header>

        {/* Upload Section */}
        {!report && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-slate-700 rounded-2xl p-12 text-center"
          >
            <div className="mb-6 flex justify-center">
              <div className="bg-slate-800 p-6 rounded-full">
                <Upload className="w-12 h-12 text-primary" />
              </div>
            </div>
            <h2 className="text-2xl font-semibold mb-4">Start New APK Analysis</h2>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">
              Upload an Android APK file for deep decompilation and security auditing in a zero-trust sandbox.
            </p>
            
            <div className="flex flex-col items-center gap-4">
              <input 
                type="file" 
                accept=".apk"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-slate-800 file:text-slate-300
                  hover:file:bg-slate-700 cursor-pointer"
              />
              
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className={`mt-4 px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all
                  ${!file || loading ? 'bg-slate-800 text-slate-500' : 'bg-primary hover:bg-primary-dark shadow-lg shadow-primary/20'}`}
              >
                {loading ? <Loader2 className="animate-spin" /> : <Zap />}
                {loading ? 'Uploading...' : 'Analyze APK'}
              </button>
            </div>

            {status === 'processing' && (
              <div className="mt-8 p-4 bg-slate-800/50 rounded-lg flex items-center justify-center gap-3 text-primary">
                <Loader2 className="animate-spin w-5 h-5" />
                <span>Decompiling & Auditing in Sandbox... ID: {jobId?.slice(0,8)}</span>
              </div>
            )}
          </motion.div>
        )}

        {/* Report Section */}
        {report && (
          <AnimatePresence>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-8"
            >
              {/* Summary Scorecard */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-card border border-slate-700 p-6 rounded-2xl col-span-1 md:col-span-2 flex items-center justify-between">
                  <div>
                    <h3 className="text-slate-400 text-sm font-medium mb-1">Security Score</h3>
                    <div className="text-5xl font-bold text-white">{report.summary.security_score}/100</div>
                  </div>
                  <div className={`w-24 h-24 rounded-full border-8 flex items-center justify-center text-xl font-bold
                    ${report.summary.security_score > 70 ? 'border-green-500 text-green-500' : 
                      report.summary.security_score > 40 ? 'border-yellow-500 text-yellow-500' : 'border-red-500 text-red-500'}`}>
                    {report.summary.security_score}%
                  </div>
                </div>
                
                <div className="bg-card border border-slate-700 p-6 rounded-2xl text-center">
                  <div className="text-red-500 mb-2"><AlertTriangle className="mx-auto" /></div>
                  <div className="text-2xl font-bold">{report.summary.high_risks}</div>
                  <div className="text-slate-400 text-xs uppercase tracking-wider mt-1">High Risks</div>
                </div>

                <div className="bg-card border border-slate-700 p-6 rounded-2xl text-center">
                  <div className="text-yellow-500 mb-2"><Zap className="mx-auto" /></div>
                  <div className="text-2xl font-bold">{report.summary.warnings}</div>
                  <div className="text-slate-400 text-xs uppercase tracking-wider mt-1">Warnings</div>
                </div>
              </div>

              {/* Detailed Findings */}
              <div className="bg-card border border-slate-700 rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-700 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">Security Audit Findings</h3>
                </div>
                <div className="divide-y divide-slate-700">
                  {report.findings.map((finding, idx) => (
                    <div key={idx} className="p-6 flex items-start gap-4 hover:bg-slate-800/30 transition-colors">
                      <div className={`mt-1 ${finding.severity === 'HIGH' ? 'text-red-500' : 
                        finding.severity === 'WARNING' ? 'text-yellow-500' : 'text-blue-500'}`}>
                        {finding.severity === 'HIGH' ? <AlertTriangle /> : <CheckCircle />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-3">
                            <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase
                              ${finding.severity === 'HIGH' ? 'bg-red-500/10 text-red-500' : 
                                finding.severity === 'WARNING' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-blue-500/10 text-blue-500'}`}>
                              {finding.severity}
                            </span>
                            <span className="text-slate-500 text-xs font-mono">{finding.source} • {finding.location}</span>
                          </div>
                          
                          <button 
                            onClick={() => handleAIExplain(idx, finding)}
                            className="text-xs flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-primary px-2 py-1 rounded transition-colors"
                          >
                            {aiLoading === idx ? <Loader2 className="animate-spin w-3 h-3" /> : <Bot className="w-3 h-3" />}
                            Ask AI
                          </button>
                        </div>
                        <p className="text-slate-200 leading-relaxed">{finding.message}</p>
                        
                        {/* AI Response Display */}
                        {aiAnalysis[idx] && (
                          <motion.div 
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="mt-4 p-4 bg-slate-900 rounded-lg border-l-4 border-primary overflow-hidden"
                          >
                            <div className="text-primary text-xs font-bold mb-2 flex items-center gap-2">
                              <Bot className="w-4 h-4" /> AI ANALYST (Ollama: Qwen 3.6)
                            </div>
                            <p className="text-slate-300 text-sm mb-3 whitespace-pre-wrap">{aiAnalysis[idx].explanation}</p>
                            {aiAnalysis[idx].patch && (
                              <div className="bg-black/40 p-3 rounded font-mono text-xs text-green-400 overflow-x-auto">
                                <div className="text-slate-500 mb-1">// Suggested Patch</div>
                                {aiAnalysis[idx].patch}
                              </div>
                            )}
                          </motion.div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-center">
                <button 
                  onClick={() => window.location.reload()}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-6 py-2 rounded-lg transition-colors border border-slate-700"
                >
                  Start New Analysis
                </button>
              </div>
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

export default App;
