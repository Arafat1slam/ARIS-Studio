import React, { useState, useEffect } from 'react';
import { 
  Film, 
  Zap, 
  Clock, 
  Flame, 
  Sparkles, 
  Play, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Copy, 
  ExternalLink, 
  Radio, 
  Terminal, 
  Monitor, 
  Smartphone, 
  Layers,
  X,
  Share2,
  FileVideo,
  ShieldCheck,
  ShieldAlert,
  Hash,
  TrendingUp,
  Folder,
  Globe,
  Link2,
  Trash2
} from 'lucide-react';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('editor');
  
  // Notification Toast State
  const [toast, setToast] = useState(null); // { type: 'error' | 'warning' | 'success', message: '' }

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => {
      setToast((prev) => (prev?.message === message ? null : prev));
    }, 5000);
  };

  // System Status State
  const [systemData, setSystemData] = useState({
    status: 'connecting',
    port: 8585,
    approved_clips: [],
    broll_clips: [],
    custom_edits: [],
    clean_clips: [],
    recent_records: []
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // After Effects Bridge Status
  const [aeStatus, setAeStatus] = useState({
    online: false,
    port: 7788,
    ae_installed: false,
    message: 'Checking bridge...'
  });

  // Custom AI Video Editor State
  const [videoInput, setVideoInput] = useState('');
  const [editPrompt, setEditPrompt] = useState('');
  const [renderLoading, setRenderLoading] = useState(false);
  const [renderResult, setRenderResult] = useState(null);
  const [renderError, setRenderError] = useState(null);

  // After Effects State
  const [aePrompt, setAePrompt] = useState('');
  const [aeCompType, setAeCompType] = useState('9:16');
  const [aeLoading, setAeLoading] = useState(false);
  const [aeResult, setAeResult] = useState(null);
  const [copiedJsx, setCopiedJsx] = useState(false);

  // Autopilot State
  const [runningSlot, setRunningSlot] = useState(false);
  const [terminalLog, setTerminalLog] = useState('[*] System standby. Select an action above to trigger automated execution...\n');

  // Sourcing State
  const [sourcingLoading, setSourcingLoading] = useState(false);
  const [sourcingLog, setSourcingLog] = useState('[*] Viral pipeline ready. Click below to fetch high-engagement trending clips.\n');

  // Copyright Remover State
  const [cpInputType, setCpInputType] = useState('file'); // 'file' | 'url'
  const [cpInputVideo, setCpInputVideo] = useState('');
  const [cpUrl, setCpUrl] = useState('');
  const [cpWatermark, setCpWatermark] = useState('ARIS');
  const [cpMode, setCpMode] = useState('9:16_short');
  const [cpTempo, setCpTempo] = useState(1.04);
  const [cpAudit, setCpAudit] = useState(null);
  const [cpAuditLoading, setCpAuditLoading] = useState(false);
  const [cpProcessLoading, setCpProcessLoading] = useState(false);
  const [cpResult, setCpResult] = useState(null);
  const [cpError, setCpError] = useState(null);

  // Fetch initial data
  const refreshStatus = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setSystemData(data);
      }
    } catch (e) {
      console.warn('Backend API connection offline:', e);
    }

    try {
      const aeRes = await fetch('/api/ae/status');
      if (aeRes.ok) {
        const data = await aeRes.json();
        setAeStatus(data);
      }
    } catch (e) {
      console.warn('AE bridge connection offline:', e);
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  // 1. Execute Custom AI Video Edit
  const handleRenderVideo = async () => {
    if (!videoInput.trim()) {
      showToast('warning', 'Please select or enter a video source path before rendering.');
      return;
    }
    if (!editPrompt.trim()) {
      showToast('warning', 'Please enter editing instructions or select a preset prompt.');
      return;
    }

    setRenderLoading(true);
    setRenderResult(null);
    setRenderError(null);

    try {
      const res = await fetch('/api/custom_edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_path: videoInput, prompt: editPrompt })
      });
      const data = await res.json();
      if (data.success) {
        setRenderResult(data);
        showToast('success', 'Video rendered successfully! Preview loaded in monitor.');
        refreshStatus();
      } else {
        setRenderError(data.error || 'Failed to render video.');
        showToast('error', data.error || 'Rendering engine encountered an error.');
      }
    } catch (err) {
      setRenderError(err.message);
      showToast('error', `Connection error: ${err.message}`);
    } finally {
      setRenderLoading(false);
    }
  };

  // 2. Generate After Effects ExtendScript JSX
  const handleGenerateAE = async () => {
    if (!aePrompt.trim()) {
      showToast('warning', 'Please enter your animation requirements for Adobe After Effects.');
      return;
    }
    setAeLoading(true);
    setAeResult(null);
    setCopiedJsx(false);

    try {
      const res = await fetch('/api/ae/generate_jsx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: aePrompt, comp_type: aeCompType })
      });
      const data = await res.json();
      if (data.success) {
        setAeResult(data);
        showToast('success', 'ExtendScript (.jsx) generated and saved successfully!');
        refreshStatus();
      } else {
        showToast('error', data.error || 'Failed to generate ExtendScript.');
      }
    } catch (err) {
      showToast('error', `Script generator error: ${err.message}`);
    } finally {
      setAeLoading(false);
    }
  };

  // 3. Trigger Autopilot Run
  const handleTriggerRun = async (target) => {
    setRunningSlot(true);
    const targetLabel = target === 'ch1' ? 'Channel 1 + Instagram' : target === 'ch2' ? 'Channel 2 (ArisVexx)' : 'Scheduled Slot';
    setTerminalLog(prev => `${prev}\n[*] [${new Date().toLocaleTimeString()}] Dispatching ${targetLabel} pipeline in background...\n`);
    try {
      const res = await fetch('/api/run_slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target })
      });
      const data = await res.json();
      setTerminalLog(prev => `${prev}${data.output || '[+] Task execution finished.'}\n`);
      showToast('success', `${targetLabel} execution completed.`);
      refreshStatus();
    } catch (err) {
      setTerminalLog(prev => `${prev}[-] Execution Error: ${err.message}\n`);
      showToast('error', `Execution failed: ${err.message}`);
    } finally {
      setRunningSlot(false);
    }
  };

  // 4. Fetch Viral Anime Clips
  const handleFetchClips = async () => {
    setSourcingLoading(true);
    setSourcingLog(prev => `${prev}\n[*] [${new Date().toLocaleTimeString()}] Searching online repository & downloading 3 viral anime clips...\n`);
    try {
      const res = await fetch('/api/fetch_clips', { method: 'POST' });
      const data = await res.json();
      setSourcingLog(prev => `${prev}${data.output || '[+] Clips sourced and approved.'}\n`);
      showToast('success', 'Fresh viral clips sourced and added to the processing queue.');
      refreshStatus();
    } catch (err) {
      setSourcingLog(prev => `${prev}[-] Sourcing Error: ${err.message}\n`);
      showToast('error', `Sourcing error: ${err.message}`);
    } finally {
      setSourcingLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedJsx(true);
    showToast('success', 'ExtendScript code copied to clipboard!');
    setTimeout(() => setCopiedJsx(false), 2500);
  };

  const copySnippet = (text, label) => {
    navigator.clipboard.writeText(text);
    showToast('success', `${label} copied to clipboard!`);
  };

  const selectClipForEditor = (path) => {
    setVideoInput(path);
    setActiveTab('editor');
    showToast('success', `Selected clip loaded into Editor: ${path}`);
  };

  const selectClipForCopyright = (path) => {
    setCpInputVideo(path);
    setActiveTab('copyright');
    showToast('success', `Loaded clip into Copyright Remover: ${path}`);
  };

  // 5. Copyright Remover: Analyze Risks
  const handleAuditCopyright = async () => {
    const targetVideo = cpInputType === 'url' ? cpUrl.trim() : cpInputVideo.trim();
    if (!targetVideo) {
      showToast('warning', cpInputType === 'url' ? 'Please paste a video URL first.' : 'Please enter or select a video path first.');
      return;
    }
    setCpAuditLoading(true);
    setCpError(null);
    try {
      const res = await fetch('/api/copyright/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_path: targetVideo })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to analyze video');
      setCpAudit(data);
      showToast('success', `Forensic audit complete: Risk Score ${data.risk_score}/100 (${data.risk_level})`);
    } catch (err) {
      setCpError(err.message);
      showToast('error', `Audit failed: ${err.message}`);
    } finally {
      setCpAuditLoading(false);
    }
  };

  // 6. Copyright Remover: Execute Remaster & Neutralize
  const handleProcessCopyright = async () => {
    const targetVideo = cpInputType === 'url' ? cpUrl.trim() : cpInputVideo.trim();
    if (!targetVideo) {
      showToast('warning', cpInputType === 'url' ? 'Please paste a video URL first.' : 'Please enter or select a video path first.');
      return;
    }
    setCpProcessLoading(true);
    setCpError(null);
    try {
      const res = await fetch('/api/copyright/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_path: targetVideo,
          watermark: cpWatermark,
          mode: cpMode,
          tempo: cpTempo
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to process video');
      setCpResult(data);
      if (data.raw_download_deleted) {
        showToast('success', 'Video remastered! Raw online download automatically deleted.');
      } else {
        showToast('success', 'Video successfully remastered & copyright neutralized!');
      }
      refreshStatus();
    } catch (err) {
      setCpError(err.message);
      showToast('error', `Process failed: ${err.message}`);
    } finally {
      setCpProcessLoading(false);
    }
  };

  return (
    <div className="studio-app-layout">
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside className="studio-sidebar">
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="brand-wrapper">
            <div className="brand-icon-box">
              <Sparkles size={22} color="#ffffff" />
            </div>
            <div className="brand-titles">
              <div className="brand-title-row">
                <h1 className="brand-title">ARIS Studio AI</h1>
                <span className="badge-version">v2.4 Pro</span>
              </div>
              <p className="brand-subtitle">Creative Automation Suite</p>
            </div>
          </div>
        </div>

        {/* Workspaces Navigation */}
        <div className="sidebar-nav-container">
          <div className="sidebar-nav-label">WORKSPACES</div>
          <nav className="sidebar-nav">
            <button 
              type="button"
              className={`sidebar-tab-btn ${activeTab === 'editor' ? 'active editor-tab' : ''}`}
              onClick={() => setActiveTab('editor')}
            >
              <div className="tab-btn-icon-wrapper">
                <Film size={18} />
              </div>
              <div className="tab-btn-text">
                <span className="tab-btn-title">AI Video Studio</span>
                <span className="tab-btn-desc">Prompt to Render</span>
              </div>
              {activeTab === 'editor' && <div className="active-indicator" />}
            </button>

            <button 
              type="button"
              className={`sidebar-tab-btn ${activeTab === 'aftereffects' ? 'active ae-tab' : ''}`}
              onClick={() => setActiveTab('aftereffects')}
            >
              <div className="tab-btn-icon-wrapper">
                <Zap size={18} />
              </div>
              <div className="tab-btn-text">
                <span className="tab-btn-title">After Effects Pro</span>
                <span className="tab-btn-desc">ExtendScript Bridge</span>
              </div>
              {activeTab === 'aftereffects' && <div className="active-indicator" />}
            </button>

            <button 
              type="button"
              className={`sidebar-tab-btn ${activeTab === 'autopilot' ? 'active autopilot-tab' : ''}`}
              onClick={() => setActiveTab('autopilot')}
            >
              <div className="tab-btn-icon-wrapper">
                <Clock size={18} />
              </div>
              <div className="tab-btn-text">
                <span className="tab-btn-title">Autopilot Operations</span>
                <span className="tab-btn-desc">24/7 Channel Manager</span>
              </div>
              {activeTab === 'autopilot' && <div className="active-indicator" />}
            </button>

            <button 
              type="button"
              className={`sidebar-tab-btn ${activeTab === 'sourcing' ? 'active sourcing-tab' : ''}`}
              onClick={() => setActiveTab('sourcing')}
            >
              <div className="tab-btn-icon-wrapper">
                <Flame size={18} />
              </div>
              <div className="tab-btn-text">
                <span className="tab-btn-title">Viral Media Queue</span>
                <span className="tab-btn-desc">Anime Clip Inventory</span>
              </div>
              {activeTab === 'sourcing' && <div className="active-indicator" />}
            </button>

            <button 
              type="button"
              className={`sidebar-tab-btn ${activeTab === 'copyright' ? 'active copyright-tab' : ''}`}
              onClick={() => setActiveTab('copyright')}
            >
              <div className="tab-btn-icon-wrapper">
                <ShieldCheck size={18} />
              </div>
              <div className="tab-btn-text">
                <span className="tab-btn-title">Copyright Remover</span>
                <span className="tab-btn-desc">Forensic Risk & Watermark</span>
              </div>
              {activeTab === 'copyright' && <div className="active-indicator" />}
            </button>
          </nav>
        </div>

        {/* Sidebar Footer with Status Diagnostics */}
        <div className="sidebar-footer">
          <div className="sidebar-status-card">
            <div className="sidebar-status-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="status-dot online"></span>
                <span className="status-text">Engine (:8585)</span>
              </div>
              <span className="status-badge-mini online">Active</span>
            </div>
            <div className="sidebar-status-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className={`status-dot ${aeStatus.online ? 'online' : 'offline'}`}></span>
                <span className="status-text">AE Bridge</span>
              </div>
              <span className={`status-badge-mini ${aeStatus.online ? 'online' : 'offline'}`}>
                {aeStatus.online ? ':7788' : 'Standby'}
              </span>
            </div>
          </div>

          <button 
            type="button"
            className="sidebar-refresh-btn" 
            onClick={refreshStatus} 
            disabled={isRefreshing}
            title="Refresh System Status"
          >
            <RefreshCw size={13} className={isRefreshing ? 'spin-icon' : ''} />
            <span>Sync System Status</span>
          </button>
        </div>
      </aside>

      {/* RIGHT MAIN CONTENT AREA */}
      <main className="studio-main-content">
        {/* Top Header / Breadcrumb Bar */}
        <header className="main-content-topbar">
          <div className="workspace-breadcrumb">
            <span className="breadcrumb-sub">Workspace /</span>
            <h2 className="breadcrumb-current">
              {activeTab === 'editor' && <>🎬 AI Video Studio</>}
              {activeTab === 'aftereffects' && <>⚡ After Effects Pro</>}
              {activeTab === 'autopilot' && <>🤖 Autopilot Operations</>}
              {activeTab === 'sourcing' && <>🔥 Viral Media Queue</>}
              {activeTab === 'copyright' && <>🛡️ AI Copyright Remover & Forensic Shield</>}
            </h2>
          </div>

          <div className="topbar-actions">
            <span className="pill-badge online">
              <span className="status-dot online"></span>
              <span>Port :8585</span>
            </span>
            <button 
              className="btn-secondary" 
              onClick={refreshStatus} 
              disabled={isRefreshing}
              title="Refresh"
            >
              <RefreshCw size={13} className={isRefreshing ? 'spin-icon' : ''} />
              <span>Refresh</span>
            </button>
          </div>
        </header>

        {/* Toast Notification Banner */}
        {toast && (
          <div className={`toast-banner ${toast.type}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {toast.type === 'error' && <AlertCircle size={17} />}
              {toast.type === 'warning' && <AlertCircle size={17} />}
              {toast.type === 'success' && <CheckCircle2 size={17} />}
              <span>{toast.message}</span>
            </div>
            <button 
              onClick={() => setToast(null)} 
              style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer', padding: '2px' }}
            >
              <X size={15} />
            </button>
          </div>
        )}

      {/* ========================================================================= */}
      {/* TAB 1: AI VIDEO STUDIO (PROMPT TO RENDER)                                 */}
      {/* ========================================================================= */}
      {activeTab === 'editor' && (
        <div className="studio-grid">
          {/* Controls Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <Film size={18} color="#818cf8" />
                <h2 className="card-title">Prompt-to-Video Engine</h2>
              </div>
              <span className="pill-badge info">FFmpeg Accelerated</span>
            </div>
            
            <p className="card-desc">
              Transform any raw footage into high-retention social content using natural language directives.
              The AI automatically generates and compiles production-ready FFmpeg filter chains.
            </p>

            {/* Step 1: Video Selection */}
            <div className="form-section">
              <label className="form-label">
                <span className="step-badge">1</span> Select Source Media File
              </label>
              
              <div className="form-input-container">
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. data/broll/broll_peaky4k.mp4 or D:\Clips\clip.mp4"
                  value={videoInput}
                  onChange={(e) => setVideoInput(e.target.value)}
                />
              </div>

              <select 
                className="form-select" 
                style={{ marginTop: '8px' }}
                value={videoInput}
                onChange={(e) => { if (e.target.value) setVideoInput(e.target.value); }}
              >
                <option value="">-- Or choose from project media library --</option>
                <optgroup label="B-Roll Library">
                  {systemData.broll_clips?.map(f => (
                    <option key={f} value={`data/broll/${f}`}>{f}</option>
                  ))}
                </optgroup>
                <optgroup label="Approved Viral Clips">
                  {systemData.approved_clips?.map(f => (
                    <option key={f} value={`data/approved_clips/${f}`}>{f}</option>
                  ))}
                </optgroup>
                <optgroup label="Previous Renders">
                  {systemData.custom_edits?.map(f => (
                    <option key={f} value={`data/custom_edits/${f}`}>{f}</option>
                  ))}
                </optgroup>
              </select>
            </div>

            {/* Step 2: Edit Prompt */}
            <div className="form-section">
              <label className="form-label">
                <span className="step-badge">2</span> AI Editing Directives & Visual Style
              </label>
              
              <textarea 
                className="form-textarea" 
                rows="3"
                placeholder="Describe your desired edits: e.g. Make a 9:16 vertical short with ambient blurred backdrop, cinematic contrast vignette, and boost bass audio"
                value={editPrompt}
                onChange={(e) => setEditPrompt(e.target.value)}
              ></textarea>

              <div className="preset-chips-container">
                <div className="preset-chips-label">Quick Preset Inspirations:</div>
                <div className="preset-chips">
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setEditPrompt('Make 9:16 vertical short with ambient blur background and cinematic contrast')}
                  >
                    📱 9:16 Viral Reel
                  </button>
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setEditPrompt('Enhance cinematic contrast, saturation and add dark aesthetic vignette')}
                  >
                    🎨 Cinematic Grade
                  </button>
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setEditPrompt('Boost bass by +5dB and dialogue treble with punchy movie theater audio')}
                  >
                    🔊 Dolby Bass Boost
                  </button>
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setEditPrompt('Apply 1.05x anti-copyright speed micro-tempo shift')}
                  >
                    ⚡ Anti-Copyright 1.05x
                  </button>
                </div>
              </div>
            </div>

            {/* Render Trigger */}
            <button 
              className="btn-primary" 
              style={{ width: '100%', padding: '14px 24px' }}
              disabled={renderLoading}
              onClick={handleRenderVideo}
            >
              {renderLoading ? (
                <>
                  <RefreshCw size={16} className="spin-icon" />
                  <span>Processing Video Render with FFmpeg Engine...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Generate AI Render</span>
                </>
              )}
            </button>
          </div>

          {/* Preview Monitor Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <Play size={18} color="#38bdf8" />
                <h2 className="card-title">Live Studio Monitor</h2>
              </div>
              {renderResult && <span className="pill-badge online">Render Complete</span>}
            </div>

            {/* Empty State */}
            {!renderResult && !renderLoading && !renderError && (
              <div className="empty-state-box">
                <div className="empty-state-icon">
                  <FileVideo size={28} />
                </div>
                <h3 className="empty-state-title">No Video Rendered Yet</h3>
                <p className="empty-state-desc">
                  Select a clip on the left, enter your editing prompt, and click "Generate AI Render" to produce your video.
                </p>
              </div>
            )}

            {/* Loading State */}
            {renderLoading && (
              <div className="empty-state-box" style={{ color: '#818cf8' }}>
                <div className="empty-state-icon" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8' }}>
                  <RefreshCw size={32} className="spin-icon" />
                </div>
                <h3 className="empty-state-title" style={{ color: '#c7d2fe' }}>Compiling & Rendering Footage</h3>
                <p className="empty-state-desc">
                  AI is analyzing directives, configuring FFmpeg hardware acceleration, and encoding final video stream (approx. 20-40 seconds)...
                </p>
              </div>
            )}

            {/* Error State */}
            {renderError && (
              <div className="toast-banner error" style={{ margin: '20px 0' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <AlertCircle size={18} style={{ marginTop: '2px', flexShrink: 0 }} />
                  <div>
                    <strong style={{ display: 'block', marginBottom: '2px' }}>Render Execution Failed</strong>
                    <span>{renderError}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Result Player & Telemetry */}
            {renderResult && (
              <div>
                <div className="player-container">
                  <video 
                    className="video-element" 
                    controls 
                    src={`/video/${renderResult.filename}`}
                    autoPlay
                  ></video>
                </div>

                {/* Telemetry Specs */}
                <div className="telemetry-grid">
                  <div className="telemetry-item">
                    <div className="telemetry-label">Resolution</div>
                    <div className="telemetry-val">{renderResult.resolution || '1080x1920'}</div>
                  </div>
                  <div className="telemetry-item">
                    <div className="telemetry-label">File Size</div>
                    <div className="telemetry-val">{renderResult.size_mb} MB</div>
                  </div>
                  <div className="telemetry-item">
                    <div className="telemetry-label">Duration</div>
                    <div className="telemetry-val">{renderResult.duration?.toFixed(1)}s</div>
                  </div>
                </div>

                {/* AI Plan Detail */}
                <div className="plan-detail-card">
                  <div className="plan-title">
                    {renderResult.plan?.preset_title || 'Custom AI Video Edit'}
                  </div>
                  <div className="plan-desc">
                    {renderResult.plan?.explanation}
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                  <a 
                    href={`/video/${renderResult.filename}`} 
                    download={renderResult.filename}
                    className="btn-primary" 
                    style={{ flex: 1, textDecoration: 'none' }}
                  >
                    <Download size={15} /> Download Rendered MP4
                  </a>
                  <button 
                    className="btn-secondary"
                    onClick={() => {
                      navigator.clipboard.writeText(`data/custom_edits/${renderResult.filename}`);
                      showToast('success', 'File path copied to clipboard');
                    }}
                    title="Copy relative file path"
                  >
                    <Copy size={14} /> Copy Path
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: AFTER EFFECTS AI STUDIO                                            */}
      {/* ========================================================================= */}
      {activeTab === 'aftereffects' && (
        <div className="studio-grid">
          {/* Controls Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <Zap size={18} color="#a855f7" />
                <h2 className="card-title">After Effects Automation Studio</h2>
              </div>
              <span className={`pill-badge ${aeStatus.online ? 'online' : 'offline'}`}>
                {aeStatus.online ? 'Live Bridge Connected' : 'ExtendScript Standalone'}
              </span>
            </div>

            <p className="card-desc">
              Integrated with <b>solomondivyananth/aftereffects-mcp</b>. Describe any kinetic typography, lower-thirds, or composition layers,
              and AI will generate and dispatch production-grade ExtendScript (.jsx) directly into Adobe After Effects.
            </p>

            {/* MCP Integration Status Pills */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
              <span className="pill-badge online" style={{ fontSize: '11px', padding: '4px 10px' }}>
                ✓ MCP Engine: Linked (aftereffects-mcp)
              </span>
              <span className="pill-badge online" style={{ fontSize: '11px', padding: '4px 10px' }}>
                ✓ 50 AE Motion Tools Ready
              </span>
              <span className={`pill-badge ${aeStatus.panel_installed ? 'online' : 'info'}`} style={{ fontSize: '11px', padding: '4px 10px' }}>
                ✓ CEP Panel: Installed (com.aemcpbridge)
              </span>
              <span className={`pill-badge ${aeStatus.online ? 'online' : 'offline'}`} style={{ fontSize: '11px', padding: '4px 10px' }}>
                Port 7788: {aeStatus.online ? 'Connected' : 'Standby'}
              </span>
            </div>

            {/* Quick Setup Note if offline */}
            {!aeStatus.online && (
              <div style={{ padding: '12px 14px', background: 'rgba(168, 85, 247, 0.08)', border: '1px solid rgba(168, 85, 247, 0.25)', borderRadius: '10px', marginBottom: '18px', fontSize: '12.5px', color: '#e9d5ff', lineHeight: '1.5' }}>
                ⚡ <b>To Enable Live Execution:</b> Launch Adobe After Effects ➔ Go to <b>Window ➔ Extensions ➔ AE MCP Bridge</b>. Once the panel opens, generated scripts will run live inside AE automatically!
              </div>
            )}

            {/* Composition Ratio Selector */}
            <div className="form-section">
              <label className="form-label">Select Composition Canvas Aspect Ratio:</label>
              <div className="aspect-selector-group">
                <div 
                  className={`aspect-card ${aeCompType === '9:16' ? 'active' : ''}`}
                  onClick={() => setAeCompType('9:16')}
                >
                  <Smartphone size={20} color={aeCompType === '9:16' ? '#c084fc' : '#94a3b8'} />
                  <span className="aspect-card-title">9:16 Vertical Short</span>
                  <span className="aspect-card-sub">1080 x 1920 (Reels / Shorts)</span>
                </div>

                <div 
                  className={`aspect-card ${aeCompType === '16:9' ? 'active' : ''}`}
                  onClick={() => setAeCompType('16:9')}
                >
                  <Monitor size={20} color={aeCompType === '16:9' ? '#c084fc' : '#94a3b8'} />
                  <span className="aspect-card-title">16:9 Widescreen</span>
                  <span className="aspect-card-sub">1920 x 1080 (Landscape)</span>
                </div>
              </div>
            </div>

            {/* Animation Prompt */}
            <div className="form-section">
              <label className="form-label">Describe Motion Graphics & Layer Behavior:</label>
              <textarea 
                className="form-textarea" 
                rows="4"
                placeholder="e.g. Create kinetic typography title 'NEON OVERDRIVE' with bounce scale keyframes from 0% to 115% to 100%, motion blur, and ambient gradient glow backdrop"
                value={aePrompt}
                onChange={(e) => setAePrompt(e.target.value)}
              ></textarea>

              <div className="preset-chips-container">
                <div className="preset-chips-label">AE Motion Presets:</div>
                <div className="preset-chips">
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setAePrompt("Create 9:16 kinetic typography with bounce easing and motion blur")}
                  >
                    ⚡ Kinetic Bounce Text
                  </button>
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setAePrompt("Add cinematic lower third title card with dark gradient and fade in")}
                  >
                    🏷️ Lower-Third Banner
                  </button>
                  <button 
                    type="button"
                    className="chip-btn" 
                    onClick={() => setAePrompt("Animate camera zoom in from 100% to 125% with smooth ease curves")}
                  >
                    🎥 Smooth Camera Push
                  </button>
                </div>
              </div>
            </div>

            {/* Generate Trigger */}
            <button 
              className="btn-primary" 
              style={{ width: '100%', background: 'var(--gradient-purple)', boxShadow: 'var(--shadow-glow-purple)' }}
              disabled={aeLoading}
              onClick={handleGenerateAE}
            >
              {aeLoading ? (
                <>
                  <RefreshCw size={16} className="spin-icon" />
                  <span>Generating ExtendScript Code...</span>
                </>
              ) : (
                <>
                  <Zap size={16} />
                  <span>Generate ExtendScript (.jsx)</span>
                </>
              )}
            </button>
          </div>

          {/* ExtendScript Code Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <Terminal size={18} color="#c084fc" />
                <h2 className="card-title">ExtendScript (.jsx) Inspector</h2>
              </div>
              {aeResult && (
                <button 
                  className="btn-secondary" 
                  onClick={() => copyToClipboard(aeResult.plan?.jsx_code || '')}
                >
                  <Copy size={13} /> {copiedJsx ? 'Copied!' : 'Copy Code'}
                </button>
              )}
            </div>

            {/* Empty State */}
            {!aeResult && !aeLoading && (
              <div className="empty-state-box">
                <div className="empty-state-icon">
                  <Layers size={28} />
                </div>
                <h3 className="empty-state-title">Ready for Motion Directives</h3>
                <p className="empty-state-desc">
                  {aeStatus.online 
                    ? 'Adobe After Effects Bridge is connected. Generated scripts can execute in real time.' 
                    : 'Generated scripts are automatically saved to your project disk and can be launched directly in After Effects.'}
                </p>
              </div>
            )}

            {/* Loading State */}
            {aeLoading && (
              <div className="empty-state-box" style={{ color: '#c084fc' }}>
                <div className="empty-state-icon" style={{ background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc' }}>
                  <RefreshCw size={32} className="spin-icon" />
                </div>
                <h3 className="empty-state-title" style={{ color: '#e9d5ff' }}>Synthesizing ExtendScript Architecture</h3>
                <p className="empty-state-desc">
                  Building keyframe tracks, layer positioning, easing curves, and composition settings...
                </p>
              </div>
            )}

            {/* Code Output */}
            {aeResult && (
              <div>
                <div style={{ marginBottom: '12px', padding: '12px 14px', background: 'var(--bg-input)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ color: '#c084fc', fontWeight: '700', fontSize: '14px' }}>
                    {aeResult.plan?.title || 'ARIS Motion Script'}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '12.5px', marginTop: '4px' }}>
                    {aeResult.plan?.explanation}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                    Saved Target: <code className="mono" style={{ color: '#38bdf8' }}>{aeResult.filename}</code>
                  </div>
                </div>

                <div className="terminal-window">
                  <div className="terminal-header">
                    <div className="terminal-dots">
                      <span className="terminal-dot red"></span>
                      <span className="terminal-dot yellow"></span>
                      <span className="terminal-dot green"></span>
                    </div>
                    <span className="terminal-title">{aeResult.filename}</span>
                  </div>
                  <pre className="terminal-body">
                    {aeResult.plan?.jsx_code}
                  </pre>
                </div>

                <div style={{ marginTop: '14px', fontSize: '12.5px', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)', padding: '12px 14px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                  💡 <b>How to Execute:</b> Open Adobe After Effects, navigate to <b>File ➔ Scripts ➔ Run Script File...</b> and select <code className="mono" style={{ color: '#a5b4fc' }}>{aeResult.filename}</code> to build the entire comp automatically.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: 24/7 AUTOPILOT CONTROL                                             */}
      {/* ========================================================================= */}
      {activeTab === 'autopilot' && (
        <div>
          {/* Dispatch Center */}
          <div className="glass-panel card-padding" style={{ marginBottom: '24px' }}>
            <div className="card-header">
              <div className="card-title-group">
                <Clock size={18} color="#10b981" />
                <h2 className="card-title">24/7 Autopilot Dispatch Center</h2>
              </div>
              <span className="pill-badge online">Autonomous Daemon Ready</span>
            </div>
            
            <p className="card-desc">
              Execute immediate one-click multi-platform publications to YouTube and Instagram, or trigger schedule tests.
            </p>

            <div className="dispatch-cards-grid">
              <div className="dispatch-card">
                <div>
                  <div className="dispatch-card-title">
                    <Share2 size={16} color="#38bdf8" /> Channel 1 + Instagram
                  </div>
                  <p className="dispatch-card-desc">
                    Publishes top viral short simultaneously to YouTube Channel 1 and Instagram Reels with full hashtags.
                  </p>
                </div>
                <button 
                  className="btn-primary" 
                  disabled={runningSlot}
                  onClick={() => handleTriggerRun('ch1')}
                >
                  {runningSlot ? <RefreshCw size={14} className="spin-icon" /> : <Play size={14} />}
                  <span>Run Channel 1 Now</span>
                </button>
              </div>

              <div className="dispatch-card">
                <div>
                  <div className="dispatch-card-title">
                    <Radio size={16} color="#a855f7" /> Channel 2 (ArisVexx)
                  </div>
                  <p className="dispatch-card-desc">
                    Directly uploads anime commentary / recap video to secondary dedicated YouTube channel.
                  </p>
                </div>
                <button 
                  className="btn-secondary" 
                  disabled={runningSlot}
                  onClick={() => handleTriggerRun('ch2')}
                >
                  {runningSlot ? <RefreshCw size={14} className="spin-icon" /> : <Play size={14} />}
                  <span>Run Channel 2 Now</span>
                </button>
              </div>

              <div className="dispatch-card">
                <div>
                  <div className="dispatch-card-title">
                    <Clock size={16} color="#10b981" /> Scheduled Cloud Slot
                  </div>
                  <p className="dispatch-card-desc">
                    Triggers the exact routine scheduled for the current hour based on the 24-hour editorial calendar.
                  </p>
                </div>
                <button 
                  className="btn-secondary" 
                  disabled={runningSlot}
                  onClick={() => handleTriggerRun('auto')}
                >
                  {runningSlot ? <RefreshCw size={14} className="spin-icon" /> : <Play size={14} />}
                  <span>Run Active Time Slot</span>
                </button>
              </div>
            </div>

            {/* Terminal Window */}
            <div className="terminal-window">
              <div className="terminal-header">
                <div className="terminal-dots">
                  <span className="terminal-dot red"></span>
                  <span className="terminal-dot yellow"></span>
                  <span className="terminal-dot green"></span>
                </div>
                <span className="terminal-title">autopilot-daemon.log</span>
                <button 
                  className="btn-secondary"
                  style={{ padding: '3px 10px', fontSize: '11px' }}
                  onClick={() => setTerminalLog('[*] Terminal cleared.\n')}
                >
                  Clear Log
                </button>
              </div>
              <pre className="terminal-body">
                {terminalLog}
              </pre>
            </div>
          </div>

          {/* Publication Ledger */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <CheckCircle2 size={18} color="#38bdf8" />
                <h2 className="card-title">Publication Ledger & History</h2>
              </div>
              <span className="pill-badge info">Total Published: {systemData.total_published || 0}</span>
            </div>

            <div className="table-responsive">
              <table className="modern-table">
                <thead>
                  <tr>
                    <th>Content Title</th>
                    <th>Destination Channel</th>
                    <th>Status</th>
                    <th>Publication Date</th>
                    <th>Live Destination</th>
                  </tr>
                </thead>
                <tbody>
                  {systemData.recent_records && systemData.recent_records.length > 0 ? (
                    systemData.recent_records.slice().reverse().map((r, i) => (
                      <tr key={i}>
                        <td style={{ maxWidth: '320px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: '600' }}>
                          {r.title || 'Untitled Automation Video'}
                        </td>
                        <td>{r.channel || (r.youtube_id ? 'Channel 1 (iταchι)' : 'Instagram')}</td>
                        <td>
                          <span className="pill-badge online" style={{ padding: '3px 10px', fontSize: '11px' }}>
                            {r.status || 'published'}
                          </span>
                        </td>
                        <td>{(r.published_at || r.timestamp || '').split('T')[0] || 'Today'}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            {r.youtube_id && (
                              <a 
                                href={`https://youtu.be/${r.youtube_id}`} 
                                target="_blank" 
                                rel="noreferrer" 
                                className="table-link-btn"
                              >
                                YouTube <ExternalLink size={10} />
                              </a>
                            )}
                            {r.instagram_id && (
                              <a 
                                href={`https://instagram.com/reel/${r.instagram_id}`} 
                                target="_blank" 
                                rel="noreferrer" 
                                className="table-link-btn"
                              >
                                Instagram <ExternalLink size={10} />
                              </a>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                        No published records yet in ledger. Run a dispatch slot to publish your first content!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: VIRAL MEDIA QUEUE                                                  */}
      {/* ========================================================================= */}
      {activeTab === 'sourcing' && (
        <div className="glass-panel card-padding">
          <div className="card-header">
            <div className="card-title-group">
              <Flame size={18} color="#f59e0b" />
              <h2 className="card-title">Viral Anime Clip Queue</h2>
            </div>
            <span className="pill-badge online">
              Queue Inventory: {systemData.approved_clips?.length || 0} Clips Ready
            </span>
          </div>

          <p className="card-desc">
            The Autopilot engine pulls from this inventory queue to automatically construct shorts for Channel 1 and Instagram.
            Click below to fetch and analyze fresh high-engagement clips.
          </p>

          <button 
            className="btn-primary" 
            style={{ background: 'var(--gradient-amber)', boxShadow: '0 4px 16px rgba(245, 158, 11, 0.35)' }}
            disabled={sourcingLoading}
            onClick={handleFetchClips}
          >
            {sourcingLoading ? (
              <>
                <RefreshCw size={16} className="spin-icon" />
                <span>Downloading & Processing Fresh Clips...</span>
              </>
            ) : (
              <>
                <Download size={16} />
                <span>Download 3 Fresh Viral Anime Clips</span>
              </>
            )}
          </button>

          {/* Sourcing Log */}
          <div className="terminal-window" style={{ marginTop: '20px' }}>
            <div className="terminal-header">
              <div className="terminal-dots">
                <span className="terminal-dot red"></span>
                <span className="terminal-dot yellow"></span>
                <span className="terminal-dot green"></span>
              </div>
              <span className="terminal-title">viral-sourcing-engine.log</span>
            </div>
            <pre className="terminal-body" style={{ maxHeight: '200px' }}>
              {sourcingLog}
            </pre>
          </div>

          {/* Current Queue Grid */}
          <div style={{ marginTop: '28px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '14px' }}>
              Clips Currently Approved & Available in Queue:
            </h3>

            {systemData.approved_clips && systemData.approved_clips.length > 0 ? (
              <div className="queue-grid">
                {systemData.approved_clips.map((clip, idx) => (
                  <div key={idx} className="queue-clip-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                      <Film size={16} color="#38bdf8" style={{ flexShrink: 0 }} />
                      <span className="queue-clip-name" title={clip}>{clip}</span>
                    </div>
                    <button 
                      className="btn-secondary" 
                      style={{ padding: '5px 10px', fontSize: '11px', flexShrink: 0 }}
                      onClick={() => selectClipForEditor(`data/approved_clips/${clip}`)}
                      title="Load into AI Video Editor"
                    >
                      Use in Editor
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state-box" style={{ padding: '36px 20px' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  No approved clips in queue. Click "Download 3 Fresh Viral Anime Clips" above to replenish inventory.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: AI COPYRIGHT REMOVER & FORENSIC SHIELD                             */}
      {/* ========================================================================= */}
      {activeTab === 'copyright' && (
        <div className="studio-grid">
          {/* Controls Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <ShieldCheck size={20} color="#06b6d4" />
                <h2 className="card-title">Copyright Forensic Neutralizer</h2>
              </div>
              <span className="pill-badge" style={{ background: 'rgba(6, 182, 212, 0.12)', color: '#22d3ee', borderColor: 'rgba(6, 182, 212, 0.25)' }}>
                ContentID & pHash Shield
              </span>
            </div>

            <p className="card-desc">
              Inspect any raw video for copyright risk vectors (audio ContentID, aspect ratio, frame hash, timestamp sync), 
              apply micro-transformations with a custom branded watermark, and generate high-CTR viral metadata.
            </p>

            {/* Segmented Mode Selector: Local File vs Online URL */}
            <div className="input-mode-toggle">
              <button 
                type="button" 
                className={`input-mode-btn ${cpInputType === 'file' ? 'active' : ''}`}
                onClick={() => setCpInputType('file')}
              >
                <Folder size={14} />
                <span>Local Video File</span>
              </button>
              <button 
                type="button" 
                className={`input-mode-btn ${cpInputType === 'url' ? 'active' : ''}`}
                onClick={() => setCpInputType('url')}
              >
                <Globe size={14} />
                <span>Online Video Link (YouTube / Shorts / Reels)</span>
              </button>
            </div>

            {/* Input 1: Local File Mode */}
            {cpInputType === 'file' && (
              <div className="form-group">
                <label className="form-label">
                  <span>Source Video File Path</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Local Path or /data/...</span>
                </label>
                <input 
                  type="text" 
                  className="cyber-input" 
                  placeholder="e.g. data/approved_clips/clip_1.mp4 or D:/Videos/scene.mp4" 
                  value={cpInputVideo} 
                  onChange={(e) => setCpInputVideo(e.target.value)} 
                />

                {/* Quick Pickers from Queue */}
                {systemData.approved_clips && systemData.approved_clips.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Quick Select from Approved Clips:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {systemData.approved_clips.slice(0, 4).map((c, i) => (
                        <button
                          key={i}
                          type="button"
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '11px', borderRadius: '6px' }}
                          onClick={() => setCpInputVideo(`data/approved_clips/${c}`)}
                        >
                          {c.length > 22 ? c.substring(0, 20) + '...' : c}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Input 2: Online Video Link Mode */}
            {cpInputType === 'url' && (
              <div className="form-group">
                <label className="form-label">
                  <span>Online Video URL (YouTube / Shorts / TikTok / Reels)</span>
                  <span style={{ fontSize: '11px', color: '#22d3ee', fontWeight: '600' }}>Direct Download</span>
                </label>
                <div style={{ position: 'relative' }}>
                  <input 
                    type="text" 
                    className="cyber-input" 
                    placeholder="Paste link e.g. https://www.youtube.com/shorts/... or https://vt.tiktok.com/..." 
                    value={cpUrl} 
                    onChange={(e) => setCpUrl(e.target.value)} 
                    style={{ paddingLeft: '38px' }}
                  />
                  <Link2 size={16} color="#06b6d4" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                </div>

                {/* Auto-Cleanup Notice */}
                <div className="cleanup-notice-banner">
                  <Trash2 size={16} color="#22d3ee" style={{ flexShrink: 0 }} />
                  <span>
                    <strong>Auto-Cleanup Shield:</strong> The online video will be downloaded temporarily, remastered with your custom watermark, and the original raw file will be <strong>automatically deleted</strong>! Only the clean copyright-free video will be saved in <code>data/copyright_free/</code>.
                  </span>
                </div>
              </div>
            )}

            {/* Watermark Configuration */}
            <div className="form-group">
              <label className="form-label">
                <span>Branded Watermark Badge</span>
                <span style={{ fontSize: '11px', color: '#22d3ee', fontWeight: '600' }}>Custom Creator Signature</span>
              </label>
              <div className="watermark-input-group">
                <input 
                  type="text" 
                  className="cyber-input" 
                  style={{ flex: 1 }}
                  placeholder="Watermark text (default: ARIS)" 
                  value={cpWatermark} 
                  onChange={(e) => setCpWatermark(e.target.value)} 
                />
                <div className="watermark-badge-preview">
                  ⚡ {cpWatermark || 'ARIS'}
                </div>
              </div>
            </div>

            {/* Mode & Micro-Tempo */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '18px' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">
                  <span>Remaster Aspect Ratio</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Auto Format</span>
                </label>
                <select 
                  className="cyber-select" 
                  value={cpMode} 
                  onChange={(e) => setCpMode(e.target.value)}
                >
                  <option value="9:16_short">9:16 Vertical Short (Reels/TikTok)</option>
                  <option value="16:9_landscape">16:9 Landscape Clean (Full HD)</option>
                  <option value="mirror_clean">Subtle Mirror & Rescale</option>
                </select>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">
                  <span>Micro-Tempo Shift</span>
                  <span style={{ fontSize: '11px', color: '#22d3ee', fontWeight: '700' }}>{cpTempo}x Speed</span>
                </label>
                <input 
                  type="range" 
                  min="1.02" 
                  max="1.08" 
                  step="0.01" 
                  value={cpTempo} 
                  onChange={(e) => setCpTempo(parseFloat(e.target.value))} 
                  className="cyber-range-slider"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                type="button"
                className="btn-secondary" 
                style={{ flex: 1, padding: '12px 14px', borderColor: 'rgba(6, 182, 212, 0.4)' }}
                disabled={cpAuditLoading || !(cpInputType === 'file' ? cpInputVideo.trim() : cpUrl.trim())}
                onClick={handleAuditCopyright}
              >
                {cpAuditLoading ? (
                  <>
                    <RefreshCw size={14} className="spin-icon" />
                    <span>{cpInputType === 'url' ? 'Downloading & Auditing...' : 'Analyzing Risks...'}</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert size={15} color="#06b6d4" />
                    <span>Run Forensic Risk Audit</span>
                  </>
                )}
              </button>

              <button 
                type="button"
                className="btn-primary" 
                style={{ flex: 1.2, padding: '12px 14px', background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', boxShadow: '0 4px 16px rgba(6, 182, 212, 0.35)' }}
                disabled={cpProcessLoading || !(cpInputType === 'file' ? cpInputVideo.trim() : cpUrl.trim())}
                onClick={handleProcessCopyright}
              >
                {cpProcessLoading ? (
                  <>
                    <RefreshCw size={14} className="spin-icon" />
                    <span>{cpInputType === 'url' ? 'Downloading, Remastering & Cleaning...' : 'Remastering & Neutralizing...'}</span>
                  </>
                ) : (
                  <>
                    <Zap size={15} />
                    <span>⚡ Remaster & Neutralize</span>
                  </>
                )}
              </button>
            </div>

            {/* Error Message */}
            {cpError && (
              <div className="error-card" style={{ marginTop: '16px' }}>
                <AlertCircle size={16} />
                <span>{cpError}</span>
              </div>
            )}

            {/* Forensic Risk Audit Report */}
            {cpAudit && (
              <div style={{ marginTop: '24px' }}>
                <div className="card-header" style={{ marginBottom: '10px' }}>
                  <div className="card-title-group">
                    <ShieldAlert size={16} color={cpAudit.risk_score >= 70 ? '#ef4444' : '#f59e0b'} />
                    <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>
                      Forensic Copyright Risk Analysis
                    </h3>
                  </div>
                  <span className={`severity-pill ${cpAudit.risk_score >= 70 ? 'CRITICAL' : 'HIGH'}`}>
                    {cpAudit.risk_level}
                  </span>
                </div>

                {/* Risk Meter Container */}
                <div className="risk-meter-container">
                  <div className="risk-meter-header">
                    <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)' }}>
                      Vulnerability Exposure Score
                    </span>
                    <span style={{ fontSize: '15px', fontWeight: '800', color: cpAudit.risk_score >= 70 ? '#ef4444' : '#f59e0b' }}>
                      {cpAudit.risk_score} / 100
                    </span>
                  </div>
                  <div className="risk-bar-track">
                    <div 
                      className={`risk-bar-fill ${cpAudit.risk_score >= 70 ? 'critical' : cpAudit.risk_score >= 50 ? 'high' : 'moderate'}`}
                      style={{ width: `${cpAudit.risk_score}%` }}
                    />
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px', lineHeight: '1.4' }}>
                    {cpAudit.summary}
                  </p>
                </div>

                {/* Factors List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '14px' }}>
                  {cpAudit.factors.map((f, idx) => (
                    <div key={idx} className="risk-factor-item">
                      <div className="risk-factor-header">
                        <span className="risk-factor-target">{f.target}</span>
                        <span className={`severity-pill ${f.severity}`}>{f.severity}</span>
                      </div>
                      <div className="risk-factor-desc">
                        <div><strong>Detected:</strong> {f.detected}</div>
                        <div><strong>Impact:</strong> {f.impact}</div>
                        <div style={{ color: '#22d3ee', marginTop: '2px' }}>
                          <strong>Shield Fix:</strong> {f.solution}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Result Player & Viral Metadata Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <div className="card-title-group">
                <Play size={18} color="#22d3ee" />
                <h2 className="card-title">Remastered Video & Viral Engine</h2>
              </div>
              {cpResult && (
                <span className="pill-badge online">
                  🛡️ Copyright Neutralized
                </span>
              )}
            </div>

            {cpResult ? (
              <div>
                {/* Remastered Video Player */}
                <div className="video-player-container">
                  <video 
                    controls 
                    autoPlay 
                    src={`/video/${cpResult.filename}`}
                    className="video-element"
                  />
                </div>

                {/* Telemetry Row */}
                <div style={{ 
                  display: 'flex', 
                  flexWrap: 'wrap', 
                  gap: '12px', 
                  padding: '12px 14px', 
                  background: 'rgba(255,255,255,0.02)', 
                  borderRadius: '10px', 
                  border: '1px solid var(--border-subtle)',
                  marginTop: '12px'
                }}>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Resolution</span>
                    <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{cpResult.resolution}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Duration</span>
                    <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{cpResult.duration}s</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>File Size</span>
                    <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{cpResult.size_mb} MB</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Watermark</span>
                    <strong style={{ fontSize: '13px', color: '#22d3ee' }}>⚡ {cpResult.watermark}</strong>
                  </div>
                  <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
                    <a 
                      href={`/video/${cpResult.filename}`} 
                      download={cpResult.filename}
                      className="btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                    >
                      <Download size={13} />
                      <span>Download Remaster</span>
                    </a>
                  </div>
                </div>

                {/* Applied Techniques Checklist */}
                <div style={{ marginTop: '16px' }}>
                  <h4 style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Shield Techniques Applied:
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '6px' }}>
                    {cpResult.techniques_applied.map((t, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-primary)' }}>
                        <CheckCircle2 size={14} color="#10b981" style={{ flexShrink: 0 }} />
                        <span>{t}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Viral Metadata Suite */}
                {cpResult.viral_metadata && (
                  <div className="viral-meta-card" style={{ marginTop: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <TrendingUp size={16} color="#f59e0b" />
                        <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>
                          AI Viral Optimization Suite
                        </h3>
                      </div>
                      <span className="pill-badge info">High CTR Algorithm Hooks</span>
                    </div>

                    {/* Viral Titles Suggestions */}
                    <div style={{ marginBottom: '14px' }}>
                      <label className="form-label" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Top Suggested Titles (Click to Copy):
                      </label>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {cpResult.viral_metadata.viral_titles?.map((title, idx) => (
                          <div key={idx} className="title-suggestion-row">
                            <span className="title-suggestion-text">{title}</span>
                            <button 
                              type="button"
                              className="btn-secondary" 
                              style={{ padding: '4px 8px', fontSize: '11px', flexShrink: 0 }}
                              onClick={() => copySnippet(title, 'Title')}
                              title="Copy title"
                            >
                              <Copy size={12} />
                              <span>Copy</span>
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Trending Hashtags */}
                    <div style={{ marginBottom: '14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                        <label className="form-label" style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                          Trending Hashtags:
                        </label>
                        <button 
                          type="button"
                          className="btn-secondary"
                          style={{ padding: '3px 8px', fontSize: '11px' }}
                          onClick={() => copySnippet(cpResult.viral_metadata.primary_hashtags?.join(' '), 'All Hashtags')}
                        >
                          <Hash size={12} />
                          <span>Copy All</span>
                        </button>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {cpResult.viral_metadata.primary_hashtags?.map((tag, idx) => (
                          <button
                            key={idx}
                            type="button"
                            className="hashtag-pill"
                            onClick={() => copySnippet(tag, tag)}
                            title="Click to copy hashtag"
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Posting Time & Engagement Tip */}
                    <div style={{ 
                      padding: '10px 12px', 
                      background: 'rgba(245, 158, 11, 0.08)', 
                      borderRadius: '8px', 
                      border: '1px solid rgba(245, 158, 11, 0.2)',
                      fontSize: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f59e0b', fontWeight: '700' }}>
                        <Clock size={13} />
                        <span>Recommended Posting Window:</span>
                      </div>
                      <div style={{ color: 'var(--text-primary)', marginTop: '2px', fontWeight: '600' }}>
                        {cpResult.viral_metadata.posting_time}
                      </div>
                      <div style={{ color: 'var(--text-muted)', marginTop: '4px', fontStyle: 'italic' }}>
                        💡 {cpResult.viral_metadata.engagement_tip}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-state-box" style={{ padding: '60px 24px', textAlign: 'center' }}>
                <ShieldCheck size={44} color="#06b6d4" style={{ margin: '0 auto 16px', opacity: 0.8 }} />
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>
                  Ready to Neutralize & Remaster
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 20px', lineHeight: '1.5' }}>
                  Select or enter any video on the left, then click <strong>Run Forensic Risk Audit</strong> to inspect ContentID vulnerabilities, or click <strong>⚡ Remaster & Neutralize</strong> to generate a clean video with your branded <strong>ARIS</strong> watermark badge.
                </p>
                <div style={{ display: 'inline-flex', gap: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <div>🛡️ ContentID Evasion</div>
                  <div>⚡ 9:16 Micro-Zoom</div>
                  <div>💎 'ARIS' Watermark</div>
                  <div>🚀 High-CTR Titles</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      </main>
    </div>
  );
}
