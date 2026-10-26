// SlothOps Client Application

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  checkAIStatus();
  initBriefSection();
  initTidySection();
  initWindDownSection();
  initSoundscapeEngine();
});

// Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.dataset.tab;
      const targetContent = document.getElementById(targetId);
      if (targetContent) targetContent.classList.add('active');
    });
  });
}

// AI Status Check
async function checkAIStatus() {
  const badge = document.getElementById('aiStatusBadge');
  const dot = badge.querySelector('.status-dot');
  const text = document.getElementById('aiStatusText');
  const infoJson = document.getElementById('engineInfoJson');

  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    if (data.status === 'online') {
      const llm = data.llm;
      if (llm.available) {
        dot.classList.add('online');
        text.textContent = `Local AI Active: ${llm.active_model} (${llm.provider})`;
      } else {
        dot.classList.remove('online');
        text.textContent = 'Local Fallback Engine Active (Zero-Config)';
      }
      if (infoJson) {
        infoJson.textContent = JSON.stringify(data, null, 2);
      }
    }
  } catch (err) {
    dot.classList.remove('online');
    text.textContent = 'Offline / Connecting...';
  }
}

// 1. Morning Brief Section
function initBriefSection() {
  const btn = document.getElementById('btnGenerateBrief');
  const btnSample = document.getElementById('btnLoadSampleNotes');
  const input = document.getElementById('briefNotesInput');
  const output = document.getElementById('briefOutputArea');

  const sampleDump = `- urgent: deploy hotfix for session token memory leak
- finish reviewing PR #42 for postgres connection pooling
- update readme for hacktoberfest submission
- fix css glitch on mobile navbar
- organize downloaded screenshots and tax PDFs
- read 12 articles bookmarked on dev.to
- buy dark roast coffee beans
- completely rewrite database query engine in c++ (maybe?)`;

  btnSample.addEventListener('click', () => {
    input.value = sampleDump;
  });

  btn.addEventListener('click', async () => {
    const notes = input.value.trim();
    if (!notes) {
      alert('Please enter or load some messy notes first!');
      return;
    }

    output.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon" style="animation: spin 2s linear infinite;">⏳</div>
        <h3>Synthesizing like a sloth...</h3>
        <p>Filtering noise and calculating zero-guilt priorities.</p>
      </div>
    `;

    try {
      const res = await fetch('/api/brief', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });
      const data = await res.json();
      renderBrief(data, output);
    } catch (err) {
      output.innerHTML = `<div class="empty-state"><p style="color:#ef4444;">Error generating brief: ${err.message}</p></div>`;
    }
  });
}

function renderBrief(data, container) {
  const highImpactHtml = (data.high_impact || [])
    .map(t => `<li><strong>•</strong> ${escapeHtml(t)}</li>`)
    .join('');

  const safeToIgnoreHtml = (data.safe_to_ignore || [])
    .map(t => `<li><strong>•</strong> ${escapeHtml(t)}</li>`)
    .join('');

  container.innerHTML = `
    <div class="brief-result-card">
      <div class="brief-meta">
        <span>Engine: <strong>${escapeHtml(data.engine_used || 'Local')}</strong></span>
        <span class="time-pill">Saved ~${data.time_saved_minutes || 20}m of stress</span>
      </div>

      <div class="brief-section high">
        <h4>🎯 Focus On These (Calm & Steady)</h4>
        <ul class="task-list">${highImpactHtml}</ul>
      </div>

      <div class="brief-section low">
        <h4>🦥 Safe To Procrastinate (No Guilt)</h4>
        <ul class="task-list">${safeToIgnoreHtml}</ul>
      </div>

      <div class="brief-section wisdom">
        <h4>🧘 Sloth Wisdom</h4>
        <div class="wisdom-quote">"${escapeHtml(data.wisdom || 'Breathe.')}"</div>
      </div>
    </div>
  `;
}

// 2. Lazy Tidy Section
let currentScanItems = [];

function initTidySection() {
  const btnScan = document.getElementById('btnScanDir');
  const inputDir = document.getElementById('targetDirPath');
  const resultsArea = document.getElementById('tidyResultsArea');

  btnScan.addEventListener('click', async () => {
    const dir = inputDir.value.trim();
    resultsArea.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon" style="animation: spin 2s linear infinite;">📂</div>
        <h3>Scanning files...</h3>
      </div>
    `;

    try {
      const res = await fetch('/api/tidy/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: dir })
      });
      const data = await res.json();

      if (res.status !== 200 || data.error) {
        resultsArea.innerHTML = `<div class="empty-state"><p style="color:#ef4444;">${data.detail || data.error}</p></div>`;
        return;
      }

      currentScanItems = data.items || [];
      renderTidyPlan(data, resultsArea);
    } catch (err) {
      resultsArea.innerHTML = `<div class="empty-state"><p style="color:#ef4444;">Scan error: ${err.message}</p></div>`;
    }
  });
}

function renderTidyPlan(data, container) {
  if (!data.items || data.items.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✨</div>
        <h3>Spotless Folder!</h3>
        <p>No loose clutter found in <code>${escapeHtml(data.source_dir)}</code>.</p>
      </div>
    `;
    return;
  }

  const rows = data.items.map(it => `
    <tr>
      <td><strong>${escapeHtml(it.filename)}</strong></td>
      <td><span class="category-badge ${it.suggested_category}">${it.suggested_category}</span></td>
      <td><small style="color:var(--text-dim);">${formatBytes(it.size_bytes)}</small></td>
    </tr>
  `).join('');

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
      <p>Found <strong>${data.total_files}</strong> files in <code>${escapeHtml(data.source_dir)}</code></p>
      <div style="display:flex; gap:0.5rem;">
        <button class="btn btn-primary" id="btnExecuteTidy">⚡ Execute Tidy</button>
        <button class="btn btn-secondary" id="btnUndoTidy">↩ Undo</button>
      </div>
    </div>
    <div style="overflow-x:auto;">
      <table class="tidy-table">
        <thead>
          <tr>
            <th>File</th>
            <th>Target Category</th>
            <th>Size</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;

  document.getElementById('btnExecuteTidy').addEventListener('click', executeTidyAction);
  document.getElementById('btnUndoTidy').addEventListener('click', undoTidyAction);
}

async function executeTidyAction() {
  if (!currentScanItems.length) return;
  try {
    const res = await fetch('/api/tidy/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: currentScanItems })
    });
    const result = await res.json();
    alert(`Success! Organized ${result.moved_count} file(s) safely.`);
    document.getElementById('btnScanDir').click();
  } catch (err) {
    alert(`Error executing tidy: ${err.message}`);
  }
}

async function undoTidyAction() {
  try {
    const res = await fetch('/api/tidy/undo', { method: 'POST' });
    const result = await res.json();
    alert(`Restored ${result.restored} file(s) back to their original spots.`);
    document.getElementById('btnScanDir').click();
  } catch (err) {
    alert(`Error during undo: ${err.message}`);
  }
}

// 3. Wind-Down Section
function initWindDownSection() {
  const btn = document.getElementById('btnGenerateWindDown');
  const input = document.getElementById('winddownInput');
  const output = document.getElementById('winddownOutputArea');

  btn.addEventListener('click', async () => {
    const accomplishments = input.value.trim();
    output.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon" style="animation: spin 2s linear infinite;">🌙</div>
        <h3>Preparing your restful summary...</h3>
      </div>
    `;

    try {
      const res = await fetch('/api/winddown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accomplishments })
      });
      const data = await res.json();

      output.innerHTML = `
        <div class="brief-result-card" style="margin-bottom:1.5rem;">
          <div class="brief-meta">
            <span>Engine: <strong>${escapeHtml(data.engine_used || 'Local')}</strong></span>
            <span class="time-pill">Day Concluded</span>
          </div>
          <div class="brief-section high">
            <h4>🏆 Today's Progress</h4>
            <p style="font-size:0.92rem; color:var(--text-main);">${escapeHtml(data.recap)}</p>
          </div>
          <div class="brief-section low">
            <h4>💤 Permission to Rest</h4>
            <p style="font-size:0.92rem; color:#fde68a;">${escapeHtml(data.permission_to_rest)}</p>
          </div>
          <div class="brief-section wisdom">
            <h4>🧘 Tonight's Mantra</h4>
            <div class="wisdom-quote">"${escapeHtml(data.tomorrow_mantra)}"</div>
          </div>
        </div>
      `;
    } catch (err) {
      output.innerHTML = `<div class="empty-state"><p style="color:#ef4444;">Error: ${err.message}</p></div>`;
    }
  });
}

// 4. Procedural Ambient Web Audio Soundscape Synthesizer
let audioCtx = null;
let currentPreset = 'rain';
let isAudioPlaying = false;
let activeNodes = [];
let masterGain = null;

function initSoundscapeEngine() {
  const toggleBtn = document.getElementById('btnToggleAudio');
  const chips = document.querySelectorAll('.sound-chip');
  const slider = document.getElementById('volumeSlider');

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentPreset = chip.dataset.sound;
      if (isAudioPlaying) {
        stopAudio();
        startAudio();
      }
    });
  });

  toggleBtn.addEventListener('click', () => {
    if (!isAudioPlaying) {
      startAudio();
      toggleBtn.textContent = '⏸ Pause Ambient Sound';
      toggleBtn.classList.add('playing');
    } else {
      stopAudio();
      toggleBtn.textContent = '▶ Play Ambient Sound';
      toggleBtn.classList.remove('playing');
    }
  });

  slider.addEventListener('input', (e) => {
    if (masterGain && audioCtx) {
      masterGain.gain.setValueAtTime(parseFloat(e.target.value), audioCtx.currentTime);
    }
  });
}

function startAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }

  masterGain = audioCtx.createGain();
  const volume = parseFloat(document.getElementById('volumeSlider').value || 0.3);
  masterGain.gain.setValueAtTime(volume, audioCtx.currentTime);
  masterGain.connect(audioCtx.destination);

  if (currentPreset === 'rain') {
    // Generate pink noise rain with resonant filter
    const bufferSize = 2 * audioCtx.sampleRate;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      output[i] = (b0 + b1 + b2) * 0.15;
    }

    const whiteNoise = audioCtx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, audioCtx.currentTime);

    whiteNoise.connect(filter);
    filter.connect(masterGain);
    whiteNoise.start();
    activeNodes.push(whiteNoise);

  } else if (currentPreset === 'drone') {
    // 432 Hz warm binaural drone
    const osc1 = audioCtx.createOscillator();
    const osc2 = audioCtx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(108, audioCtx.currentTime); // 432 / 4 = 108Hz
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(216, audioCtx.currentTime);

    const gain2 = audioCtx.createGain();
    gain2.gain.setValueAtTime(0.2, audioCtx.currentTime);

    osc1.connect(masterGain);
    osc2.connect(gain2);
    gain2.connect(masterGain);

    osc1.start();
    osc2.start();
    activeNodes.push(osc1, osc2);

  } else if (currentPreset === 'forest') {
    // Gentle modulated wind noise
    const bufferSize = 2 * audioCtx.sampleRate;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = (Math.random() * 2 - 1) * 0.1;
    }
    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    noise.loop = true;

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(350, audioCtx.currentTime);
    filter.Q.setValueAtTime(2.0, audioCtx.currentTime);

    noise.connect(filter);
    filter.connect(masterGain);
    noise.start();
    activeNodes.push(noise);
  }

  isAudioPlaying = true;
}

function stopAudio() {
  activeNodes.forEach(node => {
    try { node.stop(); node.disconnect(); } catch (e) {}
  });
  activeNodes = [];
  isAudioPlaying = false;
}

// Helpers
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
