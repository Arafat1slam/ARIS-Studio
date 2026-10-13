import React, { useState, useEffect } from 'react';
import { 
  Video, 
  Zap, 
  Clock, 
  Download, 
  Sparkles, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  Terminal, 
  Layers, 
  Film,
  RefreshCw,
  Copy,
  ExternalLink,
  Sliders,
  Flame
} from 'lucide-react';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('editor');
  
  // System Status
  const [systemData, setSystemData] = useState({
    status: 'connecting',
    port: 8585,
    approved_clips: [],
    broll_clips: [],
    custom_edits: [],
    recent_records: []
  });

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
  const [aeError, setAeError] = useState(null);
  const [copiedJsx, setCopiedJsx] = useState(false);

  // Autopilot State
  const [runningSlot, setRunningSlot] = useState(false);
  const [terminalLog, setTerminalLog] = useState('Ready. Select an action above to trigger a run...');

  // Sourcing State
  const [sourcingLoading, setSourcingLoading] = useState(false);
  const [sourcingLog, setSourcingLog] = useState('Ready to fetch fresh trending clips.');

  // Fetch initial data
  const refreshStatus = async () => {
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
    } catch (e) {}
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  // 1. Execute Custom AI Video Edit
  const handleRenderVideo = async () => {
    if (!videoInput.trim() || !editPrompt.trim()) {
      alert('ভিডিও পাথ এবং কীভাবে এডিট করতে চান তা বাংলায় বা ইংরেজিতে লিখুন!');
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
        refreshStatus();
      } else {
        setRenderError(data.error || 'Failed to render video.');
      }
    } catch (err) {
      setRenderError(err.message);
    } finally {
      setRenderLoading(false);
    }
  };

  // 2. Generate After Effects ExtendScript JSX
  const handleGenerateAE = async () => {
    if (!aePrompt.trim()) {
      alert('After Effects এ কী অ্যানিমেট করতে চান লিখুন!');
      return;
    }
    setAeLoading(true);
    setAeResult(null);
    setAeError(null);
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
        refreshStatus();
      } else {
        setAeError(data.error || 'Failed to generate ExtendScript.');
      }
    } catch (err) {
      setAeError(err.message);
    } finally {
      setAeLoading(false);
    }
  };

  // 3. Trigger Autopilot Run
  const handleTriggerRun = async (target) => {
    setRunningSlot(true);
    setTerminalLog(`[*] Starting ${target.toUpperCase()} run in background...\n`);
    try {
      const res = await fetch('/api/run_slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target })
      });
      const data = await res.json();
      setTerminalLog(data.output || 'Execution completed.');
      refreshStatus();
    } catch (err) {
      setTerminalLog(`[-] Execution Error: ${err.message}`);
    } finally {
      setRunningSlot(false);
    }
  };

  // 4. Fetch Viral Anime Clips
  const handleFetchClips = async () => {
    setSourcingLoading(true);
    setSourcingLog('[*] Searching & downloading 3 fresh viral anime clips online...\n');
    try {
      const res = await fetch('/api/fetch_clips', { method: 'POST' });
      const data = await res.json();
      setSourcingLog(data.output || 'Finished sourcing clips.');
      refreshStatus();
    } catch (err) {
      setSourcingLog(`[-] Sourcing Error: ${err.message}`);
    } finally {
      setSourcingLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedJsx(true);
    setTimeout(() => setCopiedJsx(false), 2500);
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <Sparkles size={24} color="#ffffff" />
          </div>
          <div>
            <h1 className="brand-title">ARIS Studio AI</h1>
            <p className="brand-subtitle">Smart Video Automation & After Effects Creative Suite</p>
          </div>
        </div>

        <div className="header-status">
          <span className="pill-badge online">
            <span className="status-dot online"></span> Engine Ready (:8585)
          </span>
          <span className={`pill-badge ${aeStatus.online ? 'online' : 'offline'}`}>
            <span className={`status-dot ${aeStatus.online ? 'online' : 'offline'}`}></span>
            AE Bridge: {aeStatus.online ? 'Live (:7788)' : 'Standby'}
          </span>
          <button className="btn-secondary" onClick={refreshStatus} title="Refresh System Status">
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button 
          className={`tab-btn ${activeTab === 'editor' ? 'active' : ''}`}
          onClick={() => setActiveTab('editor')}
        >
          <Film size={16} /> 🎬 Custom AI Video Editor
        </button>
        <button 
          className={`tab-btn ${activeTab === 'aftereffects' ? 'active' : ''}`}
          onClick={() => setActiveTab('aftereffects')}
        >
          <Zap size={16} /> ⚡ After Effects AI Studio
        </button>
        <button 
          className={`tab-btn ${activeTab === 'autopilot' ? 'active' : ''}`}
          onClick={() => setActiveTab('autopilot')}
        >
          <Clock size={16} /> 🤖 24/7 Autopilot Control
        </button>
        <button 
          className={`tab-btn ${activeTab === 'sourcing' ? 'active' : ''}`}
          onClick={() => setActiveTab('sourcing')}
        >
          <Flame size={16} /> 📥 Viral Anime Clips Queue
        </button>
      </nav>

      {/* ========================================================================= */}
      {/* TAB 1: CUSTOM AI VIDEO EDITOR                                             */}
      {/* ========================================================================= */}
      {activeTab === 'editor' && (
        <div className="grid-cols-2">
          {/* Controls Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <h2 className="card-title"><Film size={18} color="#818cf8" /> Prompt-to-Video Engine</h2>
              <span className="pill-badge online">Zero Config</span>
            </div>
            <p className="card-desc">ভিডিও সিলেক্ট করুন এবং নিজের ভাষায় নির্দেশ দিন। AI নিজ থেকেই হাই-কোয়ালিটি ফিল্টার প্রয়োগ করবে।</p>

            <div className="form-group">
              <label className="form-label">১. ভিডিও পাথ দিন অথবা ড্রপডাউন থেকে সিলেক্ট করুন:</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. data/broll/broll_peaky4k.mp4 or D:\Videos\my_clip.mp4"
                value={videoInput}
                onChange={(e) => setVideoInput(e.target.value)}
              />
              <select 
                className="form-select" 
                style={{ marginTop: '8px' }}
                onChange={(e) => { if (e.target.value) setVideoInput(e.target.value); }}
              >
                <option value="">-- প্রজেক্টের ভিডিও তালিকা থেকে বেছে নিন --</option>
                <optgroup label="B-Roll Clips">
                  {systemData.broll_clips?.map(f => (
                    <option key={f} value={`data/broll/${f}`}>{f}</option>
                  ))}
                </optgroup>
                <optgroup label="Approved Anime Clips">
                  {systemData.approved_clips?.map(f => (
                    <option key={f} value={`data/approved_clips/${f}`}>{f}</option>
                  ))}
                </optgroup>
                <optgroup label="Previous Custom Edits">
                  {systemData.custom_edits?.map(f => (
                    <option key={f} value={`data/custom_edits/${f}`}>{f}</option>
                  ))}
                </optgroup>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">২. কীভাবে এডিট করতে চান বাংলায় বা ইংরেজিতে লিখুন:</label>
              <textarea 
                className="form-textarea" 
                rows="3"
                placeholder="e.g. 9:16 vertical short বানাও blurred backdrop দিয়ে এবং সাউন্ড বুস্ট করো"
                value={editPrompt}
                onChange={(e) => setEditPrompt(e.target.value)}
              ></textarea>

              <div className="preset-chips">
                <button 
                  className="chip-btn" 
                  onClick={() => setEditPrompt('Make 9:16 vertical short with ambient blur background and cinematic contrast')}
                >
                  📱 9:16 Viral Short
                </button>
                <button 
                  className="chip-btn" 
                  onClick={() => setEditPrompt('Enhance cinematic contrast, saturation and add dark aesthetic vignette')}
                >
                  🎨 Cinematic Color
                </button>
                <button 
                  className="chip-btn" 
                  onClick={() => setEditPrompt('Boost bass by +5dB and dialogue treble with punchy movie theater audio')}
                >
                  🔊 Bass Boost (+5dB)
                </button>
                <button 
                  className="chip-btn" 
                  onClick={() => setEditPrompt('Apply 1.05x anti-copyright speed micro-tempo shift')}
                >
                  ⚡ 1.05x Anti-Copyright
                </button>
              </div>
            </div>

            <button 
              className="btn-primary" 
              style={{ width: '100%' }}
              disabled={renderLoading}
              onClick={handleRenderVideo}
            >
              {renderLoading ? (
                <>⏳ AI ভিডিও প্রসেস করছে (FFmpeg Engine)...</>
              ) : (
                <>⚡ AI দিয়ে ভিডিও এডিট করুন</>
              )}
            </button>
          </div>

          {/* Preview Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <h2 className="card-title"><Play size={18} color="#38bdf8" /> লাইভ ভিডিও প্রিভিউ ও রেজাল্ট</h2>
              {renderResult && <span className="pill-badge online">Render Completed</span>}
            </div>

            {!renderResult && !renderLoading && !renderError && (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                <Film size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
                <p style={{ fontSize: '14px' }}>কোনো ভিডিও রেন্ডার করা হয়নি।</p>
                <p style={{ fontSize: '12px', marginTop: '6px' }}>বাঁ দিকের ফর্মে নির্দেশ লিখে রেন্ডার বাটনে চাপুন।</p>
              </div>
            )}

            {renderLoading && (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: '#818cf8' }}>
                <RefreshCw size={40} className="spin" style={{ animation: 'spin 1.5s linear infinite', marginBottom: '16px' }} />
                <p style={{ fontWeight: '600', fontSize: '15px' }}>AI প্রম্পট বিশ্লেষণ করছে এবং FFmpeg রেন্ডার হচ্ছে...</p>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>সাধারণত ২০–৪০ সেকেন্ড সময় লাগে।</p>
              </div>
            )}

            {renderError && (
              <div style={{ padding: '20px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontWeight: '600' }}>
                  <AlertCircle size={18} /> রেন্ডারে সমস্যা হয়েছে
                </div>
                <p style={{ fontSize: '13px', marginTop: '8px', color: '#fca5a5' }}>{renderError}</p>
              </div>
            )}

            {renderResult && (
              <div>
                <video 
                  className="video-frame" 
                  controls 
                  src={`/video/${renderResult.filename}`}
                  autoPlay
                ></video>

                <div style={{ marginTop: '16px', padding: '14px', background: 'var(--bg-input)', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '14px', color: '#818cf8', fontWeight: '700' }}>
                    {renderResult.plan?.preset_title || 'Custom Video Edit'}
                  </h4>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {renderResult.plan?.explanation}
                  </p>
                  <div style={{ display: 'flex', gap: '16px', marginTop: '10px', fontSize: '12px', color: 'var(--text-muted)' }}>
                    <span>রেজোলিউশন: <b style={{ color: '#fff' }}>{renderResult.resolution}</b></span>
                    <span>সাইজ: <b style={{ color: '#fff' }}>{renderResult.size_mb} MB</b></span>
                    <span>দৈর্ঘ্য: <b style={{ color: '#fff' }}>{renderResult.duration?.toFixed(1)}s</b></span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                  <a 
                    href={`/video/${renderResult.filename}`} 
                    download={renderResult.filename}
                    className="btn-primary" 
                    style={{ flex: 1, textDecoration: 'none' }}
                  >
                    <Download size={15} /> ডাউনলোড ভিডিও
                  </a>
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
        <div className="grid-cols-2">
          {/* Controls Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <h2 className="card-title"><Zap size={18} color="#a855f7" /> After Effects AI Studio</h2>
              <span className={`pill-badge ${aeStatus.online ? 'online' : 'offline'}`}>
                {aeStatus.online ? 'Live Connected' : 'ExtendScript Standalone'}
              </span>
            </div>
            <p className="card-desc">
              aftereffects-mcp প্রযুক্তি দ্বারা চালিত। আপনি যা লিখবেন, AI সরাসরি Adobe After Effects-এর জন্য প্রোডাকশন-গ্রেড ExtendScript (.jsx) বানিয়ে দেবে।
            </p>

            <div className="form-group">
              <label className="form-label">কম্পোজিশন সাইজ নির্বাচন করুন:</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button 
                  className={`btn-secondary ${aeCompType === '9:16' ? 'active' : ''}`}
                  style={{ flex: 1, borderColor: aeCompType === '9:16' ? 'var(--accent)' : '' }}
                  onClick={() => setAeCompType('9:16')}
                >
                  📱 9:16 Vertical Short (1080x1920)
                </button>
                <button 
                  className={`btn-secondary ${aeCompType === '16:9' ? 'active' : ''}`}
                  style={{ flex: 1, borderColor: aeCompType === '16:9' ? 'var(--accent)' : '' }}
                  onClick={() => setAeCompType('16:9')}
                >
                  🖥️ 16:9 Widescreen (1920x1080)
                </button>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">After Effects-এ কী অ্যানিমেশন ও লেয়ার চান লিখুন:</label>
              <textarea 
                className="form-textarea" 
                rows="4"
                placeholder="e.g. Create kinetic typography title 'NEON BLADE' with scale bounce keyframes from 0% to 110% to 100% and ambient dark backdrop"
                value={aePrompt}
                onChange={(e) => setAePrompt(e.target.value)}
              ></textarea>

              <div className="preset-chips">
                <button 
                  className="chip-btn" 
                  onClick={() => setAePrompt("Create 9:16 kinetic typography with bounce easing and motion blur")}
                >
                  ⚡ Kinetic Bounce Text
                </button>
                <button 
                  className="chip-btn" 
                  onClick={() => setAePrompt("Add cinematic lower third title card with dark gradient and fade in")}
                >
                  🏷️ Lower Third Title
                </button>
                <button 
                  className="chip-btn" 
                  onClick={() => setAePrompt("Animate camera zoom in from 100% to 125% with smooth ease curves")}
                >
                  🎥 Camera Zoom In
                </button>
              </div>
            </div>

            <button 
              className="btn-primary" 
              style={{ width: '100%', background: 'var(--purple-gradient)' }}
              disabled={aeLoading}
              onClick={handleGenerateAE}
            >
              {aeLoading ? '⏳ ExtendScript (.jsx) তৈরি হচ্ছে...' : '⚡ AI দিয়ে After Effects স্ক্রিপ্ট তৈরি করুন'}
            </button>
          </div>

          {/* ExtendScript Preview & Bridge Column */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <h2 className="card-title"><Terminal size={18} color="#38bdf8" /> ExtendScript (.jsx) আউটপুট</h2>
              {aeResult && (
                <button 
                  className="btn-secondary" 
                  onClick={() => copyToClipboard(aeResult.plan?.jsx_code || '')}
                >
                  <Copy size={13} /> {copiedJsx ? 'কপি হয়েছে!' : 'Copy Code'}
                </button>
              )}
            </div>

            {!aeResult && !aeLoading && (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                <Layers size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
                <p style={{ fontSize: '14px' }}>স্ক্রিপ্ট তৈরি হলে এখানে কোড ও এক্সিকিউশন স্ট্যাটাস দেখাবে।</p>
                <p style={{ fontSize: '12px', marginTop: '6px' }}>
                  {aeStatus.online 
                    ? '🟢 After Effects প্যানেল কানেক্টেড আছে! ১-ক্লিকে সরাসরি AE-তে রান হবে।' 
                    : '🟡 After Effects চালু না থাকলেও .jsx ফাইল সেভ হবে, যা সরাসরি AE-তে রান করা যাবে।'}
                </p>
              </div>
            )}

            {aeLoading && (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: '#c084fc' }}>
                <RefreshCw size={40} className="spin" style={{ animation: 'spin 1.5s linear infinite', marginBottom: '16px' }} />
                <p style={{ fontWeight: '600', fontSize: '15px' }}>AI দিয়ে After Effects স্ক্রিপ্ট আর্কিটেকচার তৈরি হচ্ছে...</p>
              </div>
            )}

            {aeResult && (
              <div>
                <div style={{ marginBottom: '12px', padding: '12px', background: 'var(--bg-input)', borderRadius: '10px' }}>
                  <div style={{ color: '#c084fc', fontWeight: '700', fontSize: '14px' }}>
                    {aeResult.plan?.title || 'ARIS AE Motion Script'}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '12.5px', marginTop: '4px' }}>
                    {aeResult.plan?.explanation}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                    ফাইল: <code className="mono" style={{ color: '#38bdf8' }}>{aeResult.filename}</code>
                  </div>
                </div>

                <div className="terminal-box" style={{ maxHeight: '280px' }}>
                  {aeResult.plan?.jsx_code}
                </div>

                <div style={{ marginTop: '14px', fontSize: '12px', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                  💡 <b>ব্যবহারের নিয়ম:</b> After Effects সফটওয়্যারটি খুলে <b>File ➔ Scripts ➔ Run Script File...</b> সিলেক্ট করে এই <code className="mono">{aeResult.filename}</code> ফাইলটি রান করলেই সম্পুর্ণ কমপোজিশন তৈরি হয়ে যাবে!
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
          <div className="glass-panel card-padding" style={{ marginBottom: '24px' }}>
            <div className="card-header">
              <h2 className="card-title"><Clock size={18} color="#10b981" /> 24/7 Autopilot Control Center</h2>
              <span className="pill-badge online">Active Scheduler</span>
            </div>
            <p className="card-desc">
              আপনার ইউটিউব চ্যানেল ১, চ্যানেল ২ এবং ইন্সটাগ্রামে ১-ক্লিকে ইনস্ট্যান্ট পোস্ট করুন অথবা শিডিউলড স্লট টেস্ট করুন।
            </p>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button 
                className="btn-primary" 
                disabled={runningSlot}
                onClick={() => handleTriggerRun('ch1')}
              >
                🎬 Run Channel 1 + Instagram Now
              </button>
              <button 
                className="btn-secondary" 
                disabled={runningSlot}
                onClick={() => handleTriggerRun('ch2')}
              >
                🧠 Run Channel 2 (ArisVexx) Now
              </button>
              <button 
                className="btn-secondary" 
                disabled={runningSlot}
                onClick={() => handleTriggerRun('auto')}
              >
                🕒 Run Scheduled Time Slot
              </button>
            </div>

            <div className="terminal-box" style={{ marginTop: '16px' }}>
              {terminalLog}
            </div>
          </div>

          {/* Ledger Table */}
          <div className="glass-panel card-padding">
            <div className="card-header">
              <h2 className="card-title"><CheckCircle2 size={18} color="#38bdf8" /> সাম্প্রতিক পোস্ট লেজার (Recent Ledger Records)</h2>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>মোট পোস্ট: {systemData.total_published || 0}</span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Channel</th>
                    <th>Status</th>
                    <th>Published At</th>
                    <th>Links</th>
                  </tr>
                </thead>
                <tbody>
                  {systemData.recent_records?.slice().reverse().map((r, i) => (
                    <tr key={i}>
                      <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {r.title || 'Untitled'}
                      </td>
                      <td>{r.channel || (r.youtube_id ? 'iταchι Live' : 'Meta')}</td>
                      <td>
                        <span className="pill-badge online" style={{ fontSize: '11px', padding: '2px 8px' }}>
                          {r.status || 'published'}
                        </span>
                      </td>
                      <td>{(r.published_at || r.timestamp || '').split('T')[0]}</td>
                      <td>
                        {r.youtube_id && (
                          <a 
                            href={`https://youtu.be/${r.youtube_id}`} 
                            target="_blank" 
                            rel="noreferrer" 
                            className="link-btn"
                            style={{ marginRight: '8px' }}
                          >
                            YouTube <ExternalLink size={11} style={{ display: 'inline' }} />
                          </a>
                        )}
                        {r.instagram_id && (
                          <a 
                            href={`https://instagram.com/reel/${r.instagram_id}`} 
                            target="_blank" 
                            rel="noreferrer" 
                            className="link-btn"
                          >
                            Instagram <ExternalLink size={11} style={{ display: 'inline' }} />
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: VIRAL SOURCING ENGINE                                              */}
      {/* ========================================================================= */}
      {activeTab === 'sourcing' && (
        <div className="glass-panel card-padding">
          <div className="card-header">
            <h2 className="card-title"><Flame size={18} color="#f59e0b" /> ভাইরাল অ্যানিমে ক্লিপ কিউ (Approved Clips)</h2>
            <span className="pill-badge online">
              কিউতে আছে: {systemData.approved_clips?.length || 0} টি ক্লিপ
            </span>
          </div>
          <p className="card-desc">
            ক্লাউড অটোপাইলট এই ফোল্ডারের ক্লিপগুলো ১টি ১টি করে নিয়ে স্বয়ংক্রিয়ভাবে চ্যানেল ১ ও ইন্সটাগ্রামের জন্য শর্টস তৈরি করবে।
          </p>

          <button 
            className="btn-primary" 
            style={{ background: 'var(--amber-gradient)' }}
            disabled={sourcingLoading}
            onClick={handleFetchClips}
          >
            {sourcingLoading ? '⏳ ক্লিপ ডাউনলোড ও ফিল্টার হচ্ছে...' : '📥 নতুন ৩টি ভাইরাল অ্যানিমে ক্লিপ ডাউনলোড করুন'}
          </button>

          <div className="terminal-box" style={{ marginTop: '16px' }}>
            {sourcingLog}
          </div>

          <div style={{ marginTop: '24px' }}>
            <h4 style={{ fontSize: '15px', color: 'var(--text-primary)', marginBottom: '12px' }}>
              বর্তমানে কিউতে রেডি থাকা ক্লিপসমূহ:
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
              {systemData.approved_clips?.map((c, idx) => (
                <div key={idx} style={{ padding: '12px', background: 'var(--bg-input)', borderRadius: '10px', border: '1px solid var(--border)', fontSize: '13px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8' }}>
                    <Film size={14} /> <b>{c}</b>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
