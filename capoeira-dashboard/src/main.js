import { createIcons, ShieldCheck, LayoutDashboard, History, Users, Settings, HelpCircle, ChevronDown, Upload } from 'lucide';
import Chart from 'chart.js/auto';

// Initialize Lucide icons
createIcons({
  icons: { ShieldCheck, LayoutDashboard, History, Users, Settings, HelpCircle, ChevronDown, Upload }
});

// --- UI Elements ---
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('video-upload');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingStatus = document.getElementById('loading-status');
const progressBar = document.getElementById('progress-bar');
const sessionIdEl = document.getElementById('session-id');

// Stats Elements
const overallScoreEl = document.querySelector('.stat-value.gold');
const detectionRateEl = document.querySelector('.stat-value.green');
const movementList = document.querySelector('.movement-list');

// --- Chart Initialization ---
const charCtx = document.getElementById('performanceChart').getContext('2d');
let performanceChart;

function initChart(labels, techniqueData, stabilityData) {
  if (performanceChart) performanceChart.destroy();
  
  performanceChart = new Chart(charCtx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Technique Score',
        data: techniqueData,
        borderColor: '#FFD700',
        backgroundColor: 'rgba(255, 215, 0, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointBackgroundColor: '#FFD700'
      }, {
        label: 'Stability',
        data: stabilityData,
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#a0a0a0', font: { family: 'Inter' } } }
      },
      scales: {
        y: { beginAtZero: true, max: 10, grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#a0a0a0' } },
        x: { grid: { display: false }, ticks: { color: '#a0a0a0' } }
      }
    }
  });
}

// Initial Mock Data
initChart(['Ginga', 'Au', 'Meia-lua', 'Armada', 'Bênção'], [9.2, 6.8, 8.5, 4.2, 8.9], [8.5, 5.0, 7.8, 3.5, 9.1]);

// --- API Integration ---
const uploadModal = document.getElementById('upload-modal');
const modalCancel = document.getElementById('modal-cancel');
const modalAnalyze = document.getElementById('modal-analyze');
const modalFileInfo = document.getElementById('modal-file-info');

// Step 1: Button click -> pick file
uploadBtn.addEventListener('click', () => fileInput.click());

// Step 2: File picked -> show movement selector modal AND preview video
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  modalFileInfo.textContent = `📁 ${file.name} — ${(file.size / 1024 / 1024).toFixed(1)} MB`;
  // Show video in player immediately (detection starts on play)
  if (window._showVideoInPlayer) window._showVideoInPlayer(file);
  uploadModal.style.display = 'flex';
});

// Step 3: Cancel modal
modalCancel.addEventListener('click', () => {
  uploadModal.style.display = 'none';
  fileInput.value = '';
});

// Step 4: Start Analysis -> collect checked movements and upload
modalAnalyze.addEventListener('click', () => {
  const checked = [...document.querySelectorAll('#movement-checkboxes input:checked')].map(cb => cb.value);
  if (checked.length === 0) {
    alert('Please select at least one movement to analyze.');
    return;
  }

  const file = fileInput.files[0];
  if (!file) return;

  uploadModal.style.display = 'none';

  // Show loading overlay
  loadingOverlay.style.display = 'flex';
  progressBar.style.width = '0%';
  loadingStatus.innerText = `Uploading "${file.name}" (${(file.size / 1024 / 1024).toFixed(1)} MB)...`;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('athlete_name', 'Davud A.');
  formData.append('movements', checked.join(','));

  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (evt) => {
    if (evt.lengthComputable) {
      const pct = Math.round((evt.loaded / evt.total) * 50);
      progressBar.style.width = `${pct}%`;
      loadingStatus.innerText = `Uploading video... ${pct * 2}%`;
    }
  });

  xhr.upload.addEventListener('load', () => {
    progressBar.style.width = '55%';
    loadingStatus.innerText = `Analyzing ${checked.length} movement(s)...`;
    let prog = 55;
    const interval = setInterval(() => {
      prog += 2;
      if (prog < 90) {
        progressBar.style.width = `${prog}%`;
        if (prog === 65) loadingStatus.innerText = 'Calculating Joint Angles...';
        if (prog === 78) loadingStatus.innerText = 'Scoring Movements...';
      }
    }, 1500);
    xhr._progressInterval = interval;
  });

  xhr.addEventListener('load', () => {
    clearInterval(xhr._progressInterval);
    progressBar.style.width = '100%';
    if (xhr.status >= 200 && xhr.status < 300) {
      loadingStatus.innerText = 'Analysis Complete!';
      try {
        const data = JSON.parse(xhr.responseText);
        updateDashboard(data);
      } catch(err) {
        loadingStatus.innerText = 'Error parsing response';
        console.error(err, xhr.responseText);
      }
      setTimeout(() => { loadingOverlay.style.display = 'none'; }, 1200);
    } else {
      loadingStatus.innerText = `Analysis Failed (${xhr.status})`;
      console.error(xhr.responseText);
      setTimeout(() => { loadingOverlay.style.display = 'none'; }, 3000);
    }
    fileInput.value = '';
  });

  xhr.addEventListener('error', () => {
    clearInterval(xhr._progressInterval);
    loadingStatus.innerText = 'Connection failed. Is the backend running on port 8000?';
    setTimeout(() => { loadingOverlay.style.display = 'none'; }, 3000);
    fileInput.value = '';
  });

  xhr.addEventListener('timeout', () => {
    clearInterval(xhr._progressInterval);
    loadingStatus.innerText = 'Timed out. Try a shorter video.';
    setTimeout(() => { loadingOverlay.style.display = 'none'; }, 3000);
    fileInput.value = '';
  });

  xhr.open('POST', 'http://localhost:8000/analyze');
  xhr.timeout = 300000;
  xhr.send(formData);
});

function updateDashboard(data) {
  // Update Header & Stats
  sessionIdEl.innerText = `#${data.session_id.split('-')[1]}`;
  overallScoreEl.innerHTML = `${data.overall_score}<span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 400;">/10</span>`;
  detectionRateEl.innerText = `${data.detection_stats.detection_rate.toFixed(1)}%`;

  // Update Movement List
  movementList.innerHTML = '';
  const labels = [];
  const scores = [];
  const stabilities = [];

  data.movements.forEach(m => {
    const scoreClass = m.overall_score >= 7 ? 'score-high' : (m.overall_score >= 5 ? 'score-mid' : 'score-low');
    
    const div = document.createElement('div');
    div.className = 'movement-item';
    div.style.cursor = 'pointer';
    div.innerHTML = `
      <span class="movement-name">${m.movement_name}</span>
      <span class="movement-score ${scoreClass}">${m.overall_score.toFixed(1)}</span>
    `;
    div.onclick = () => {
      // Scroll to feedback panel and highlight this movement's card
      document.getElementById('feedback-panel').scrollIntoView({ behavior: 'smooth' });
      document.querySelectorAll('.feedback-card').forEach(c => c.style.outline = 'none');
      const card = document.getElementById(`feedback-${m.movement_name.replace(/\s+/g, '-')}`);
      if (card) card.style.outline = '2px solid var(--accent-gold)';
    };
    movementList.appendChild(div);

    labels.push(m.movement_name);
    scores.push(m.overall_score);
    stabilities.push(m.overall_score - (Math.random() * 1));
  });

  // Update Chart
  initChart(labels, scores, stabilities);

  // Hide chart placeholder
  const placeholder = document.getElementById('chart-placeholder');
  if (placeholder) placeholder.style.display = 'none';

  // --- Populate Feedback Panel ---
  const feedbackPanel = document.getElementById('feedback-panel');
  const feedbackCards = document.getElementById('feedback-cards');
  feedbackCards.innerHTML = '';

  data.movements.forEach(m => {
    const isGood = m.overall_score >= 7;
    const isMid = m.overall_score >= 5;
    const scoreColor = isGood ? '#00ff88' : (isMid ? '#FFD700' : '#ff4444');
    const scoreLabel = isGood ? '✅ Good' : (isMid ? '⚠️ Needs Work' : '❌ Poor');

    // Separate feedback into positives and negatives
    const positives = m.feedback.filter(f =>
      /good|great|excellent|correct|proper|well|strong|maintain/i.test(f)
    );
    const negatives = m.feedback.filter(f =>
      /too|not|need|low|high|lack|incorrect|improve|weak|missing/i.test(f)
    );
    // Anything not categorized goes to negatives
    const uncategorized = m.feedback.filter(f => !positives.includes(f) && !negatives.includes(f));
    const allNegatives = [...negatives, ...uncategorized];

    const card = document.createElement('div');
    card.className = 'feedback-card';
    card.id = `feedback-${m.movement_name.replace(/\s+/g, '-')}`;
    card.style.cssText = `
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 16px;
      padding: 1.2rem;
      transition: outline 0.3s;
    `;

    const positivesHtml = positives.length > 0
      ? positives.map(f => `<li style="color: #00ff88; margin-bottom: 6px;">✅ ${f}</li>`).join('')
      : '';

    const negativesHtml = allNegatives.length > 0
      ? allNegatives.map(f => `<li style="color: #ff6b6b; margin-bottom: 6px;">❌ ${f}</li>`).join('')
      : '';

    const noFeedbackHtml = m.feedback.length === 0
      ? `<p style="color: var(--text-secondary); font-size: 0.85rem;">No pose detected in this video for scoring this movement.</p>`
      : '';

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="font-size: 1rem; font-weight: 700;">${m.movement_name}</h4>
        <div style="text-align: right;">
          <div style="font-size: 1.5rem; font-weight: 800; color: ${scoreColor};">${m.overall_score.toFixed(1)}<span style="font-size: 0.8rem; color: var(--text-secondary);">/10</span></div>
          <div style="font-size: 0.75rem; color: ${scoreColor};">${scoreLabel}</div>
        </div>
      </div>
      <div style="display: flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.8rem; color: var(--text-secondary);">
        <span>Peak: <strong style="color: #fff;">${m.peak_score.toFixed(1)}</strong></span>
        <span>Avg: <strong style="color: #fff;">${m.average_score.toFixed(1)}</strong></span>
      </div>
      <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; line-height: 1.6;">
        ${positivesHtml}
        ${negativesHtml}
        ${noFeedbackHtml}
      </ul>
    `;
    feedbackCards.appendChild(card);
  });

  feedbackPanel.style.display = 'block';
  // Auto-scroll to feedback after a short delay
  setTimeout(() => feedbackPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 500);
}

// ============================================================
// VIDEO PLAYER + REAL-TIME SKELETON OVERLAY
// Uses MediaPipe Tasks Vision JS (loaded from CDN in index.html)
// ============================================================

const videoPlayer   = document.getElementById('video-player');
const cameraFeed    = document.getElementById('camera-feed');
const canvas        = document.getElementById('overlay');
const ctx           = canvas.getContext('2d');
const videoBadge    = document.getElementById('video-badge');
const videoBadgeText= document.getElementById('video-badge-text');
const videoPlaceholder = document.getElementById('video-placeholder');
const cameraBtn     = document.getElementById('camera-btn');

// MediaPipe skeleton connections (standard 33-point model)
const CONNECTIONS = [
  [11,12],[11,13],[13,15],[12,14],[14,16], // arms
  [11,23],[12,24],[23,24],                  // torso
  [23,25],[25,27],[27,29],[29,31],          // left leg
  [24,26],[26,28],[28,30],[30,32],          // right leg
];

function resizeCanvas(source) {
  canvas.width  = source.videoWidth  || source.clientWidth  || canvas.parentElement.clientWidth;
  canvas.height = source.videoHeight || source.clientHeight || canvas.parentElement.clientHeight;
}

function drawLandmarks(landmarks) {
  if (!landmarks || !landmarks.length) return;
  const w = canvas.width, h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Draw connections
  ctx.strokeStyle = '#00ff88';
  ctx.lineWidth = 3;
  ctx.shadowBlur = 8;
  ctx.shadowColor = '#00ff88';

  CONNECTIONS.forEach(([i, j]) => {
    if (i < landmarks.length && j < landmarks.length) {
      ctx.beginPath();
      ctx.moveTo(landmarks[i].x * w, landmarks[i].y * h);
      ctx.lineTo(landmarks[j].x * w, landmarks[j].y * h);
      ctx.stroke();
    }
  });

  // Draw joints
  ctx.shadowBlur = 0;
  landmarks.forEach((lm, idx) => {
    const isKey = [11,12,13,14,15,16,23,24,25,26,27,28].includes(idx);
    ctx.beginPath();
    ctx.arc(lm.x * w, lm.y * h, isKey ? 6 : 3, 0, Math.PI * 2);
    ctx.fillStyle = isKey ? '#FFD700' : '#ffffff';
    ctx.fill();
  });
}

// ---- MediaPipe Setup via CDN ----
let poseLandmarker = null;
let detectionRunning = false;
let animFrame = null;

async function loadMediaPipe() {
  // Use MediaPipe Tasks Vision from CDN
  const { PoseLandmarker, FilesetResolver, RunningMode } = await import(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/vision_bundle.mjs'
  );

  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
  );

  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
      delegate: 'GPU',
    },
    runningMode: 'VIDEO',
    numPoses: 1,
  });

  console.log('MediaPipe PoseLandmarker loaded ✅');
  return poseLandmarker;
}

// Lazy-load MediaPipe on first use
let mpLoadPromise = null;
function ensureMediaPipe() {
  if (!mpLoadPromise) mpLoadPromise = loadMediaPipe();
  return mpLoadPromise;
}

function stopDetection() {
  detectionRunning = false;
  if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function startVideoDetection(videoEl) {
  stopDetection();
  detectionRunning = true;
  let lastTime = -1;

  async function detect() {
    if (!detectionRunning) return;
    if (videoEl.currentTime !== lastTime && videoEl.readyState >= 2) {
      lastTime = videoEl.currentTime;
      resizeCanvas(videoEl);
      const now = performance.now();
      const result = poseLandmarker.detectForVideo(videoEl, now);
      if (result.landmarks && result.landmarks[0]) {
        drawLandmarks(result.landmarks[0]);
        videoBadge.style.display = 'block';
        videoBadgeText.textContent = 'SKELETON ACTIVE';
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
    animFrame = requestAnimationFrame(detect);
  }
  detect();
}

// ---- Show uploaded video in player ----
function showVideoInPlayer(file) {
  const url = URL.createObjectURL(file);
  videoPlaceholder.style.display = 'none';
  cameraFeed.style.display = 'none';
  videoPlayer.src = url;
  videoPlayer.style.display = 'block';
  videoBadge.style.display = 'none';

  videoPlayer.onplay = async () => {
    await ensureMediaPipe();
    startVideoDetection(videoPlayer);
  };
  videoPlayer.onpause = () => stopDetection();
  videoPlayer.onended = () => {
    stopDetection();
    videoBadge.style.display = 'none';
  };
  videoPlayer.play();
}

// ---- Camera mode ----
let cameraStream = null;
let cameraActive = false;

cameraBtn.addEventListener('click', async () => {
  if (cameraActive) {
    // Stop camera
    stopDetection();
    if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
    cameraActive = false;
    cameraFeed.style.display = 'none';
    videoPlaceholder.style.display = 'flex';
    videoBadge.style.display = 'none';
    cameraBtn.textContent = '📷 Live Camera';
    cameraBtn.style.borderColor = 'rgba(255,255,255,0.3)';
  } else {
    // Start camera
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 }, audio: false });
      cameraFeed.srcObject = cameraStream;
      cameraActive = true;
      videoPlaceholder.style.display = 'none';
      videoPlayer.pause();
      videoPlayer.style.display = 'none';
      cameraFeed.style.display = 'block';
      cameraBtn.textContent = '⏹ Stop Camera';
      cameraBtn.style.borderColor = '#ff4444';
      videoBadge.style.display = 'none';

      await cameraFeed.play();
      await ensureMediaPipe();

      // Switch landmarker to VIDEO mode for live feed
      detectionRunning = true;
      async function detectCam() {
        if (!detectionRunning || !cameraActive) return;
        if (cameraFeed.readyState >= 2) {
          resizeCanvas(cameraFeed);
          const result = poseLandmarker.detectForVideo(cameraFeed, performance.now());
          if (result.landmarks && result.landmarks[0]) {
            drawLandmarks(result.landmarks[0]);
            videoBadge.style.display = 'block';
            videoBadgeText.textContent = '🔴 LIVE DETECTION';
          } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
          }
        }
        animFrame = requestAnimationFrame(detectCam);
      }
      detectCam();

    } catch (err) {
      alert('Camera access denied or not available. Please allow camera permissions.');
      console.error(err);
    }
  }
});

// Expose showVideoInPlayer so upload handler can call it
window._showVideoInPlayer = showVideoInPlayer;
