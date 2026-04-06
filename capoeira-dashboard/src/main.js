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
const loadingRing = document.getElementById('loading-ring');
const loadingPercent = document.getElementById('loading-percent');
const sessionIdEl = document.getElementById('session-id');

// Stats Elements
const overallScoreEl = document.getElementById('overall-score');
const scoreRing = document.getElementById('score-ring');
const detectionRateEl = document.getElementById('detection-rate');
const movementList = document.getElementById('movement-list');
const movementCountEl = document.getElementById('movement-count');
const flowScoreEl = document.getElementById('flow-score');

// Progress ring circumference
const RING_CIRCUMFERENCE = 326.7; // 2 * PI * 52

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

// --- API Integration (Fully Automatic - No Movement Selection) ---

// Step 1: Button click -> pick file
uploadBtn.addEventListener('click', () => fileInput.click());

// Step 2: File picked -> automatically start analysis (no modal)
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // Show video in player immediately (detection starts on play)
  if (window._showVideoInPlayer) window._showVideoInPlayer(file);

  // Automatically start analysis - no movement selection needed
  startAutoAnalysis(file);
});

// Update circular progress ring
function updateLoadingProgress(percent) {
  const offset = RING_CIRCUMFERENCE - (percent / 100) * RING_CIRCUMFERENCE;
  if (loadingRing) loadingRing.style.strokeDashoffset = offset;
  if (loadingPercent) loadingPercent.textContent = `${Math.round(percent)}%`;
}

// Automatic analysis function - detects movements automatically
function startAutoAnalysis(file) {
  // Show loading overlay
  loadingOverlay.style.display = 'flex';
  updateLoadingProgress(0);
  loadingStatus.innerText = `Uploading "${file.name}"...`;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('athlete_name', 'Davud A.');
  formData.append('auto_detect', 'true'); // Enable automatic movement detection

  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (evt) => {
    if (evt.lengthComputable) {
      const pct = Math.round((evt.loaded / evt.total) * 50);
      updateLoadingProgress(pct);
      loadingStatus.innerText = `Uploading video... ${pct * 2}%`;
    }
  });

  xhr.upload.addEventListener('load', () => {
    updateLoadingProgress(55);
    loadingStatus.innerText = 'Detecting movements...';
    let prog = 55;
    const interval = setInterval(() => {
      prog += 2;
      if (prog < 95) {
        updateLoadingProgress(prog);
        if (prog === 63) loadingStatus.innerText = 'Running pose estimation...';
        if (prog === 71) loadingStatus.innerText = 'Identifying movements...';
        if (prog === 79) loadingStatus.innerText = 'Calculating scores...';
        if (prog === 87) loadingStatus.innerText = 'Analyzing sequence flow...';
      }
    }, 1200);
    xhr._progressInterval = interval;
  });

  xhr.addEventListener('load', () => {
    clearInterval(xhr._progressInterval);
    updateLoadingProgress(100);
    if (xhr.status >= 200 && xhr.status < 300) {
      loadingStatus.innerText = 'Analysis Complete!';
      try {
        const data = JSON.parse(xhr.responseText);
        updateDashboard(data);
        if (window.showToast) window.showToast('success', 'Analysis Complete', `Detected ${data.movements?.length || 0} movements`);
      } catch(err) {
        loadingStatus.innerText = 'Error parsing response';
        console.error(err, xhr.responseText);
        if (window.showToast) window.showToast('error', 'Error', 'Failed to parse analysis results');
      }
      setTimeout(() => { loadingOverlay.style.display = 'none'; }, 1000);
    } else {
      loadingStatus.innerText = `Analysis Failed (${xhr.status})`;
      console.error(xhr.responseText);
      if (window.showToast) window.showToast('error', 'Analysis Failed', 'Please try again');
      setTimeout(() => { loadingOverlay.style.display = 'none'; }, 2000);
    }
    fileInput.value = '';
  });

  xhr.addEventListener('error', () => {
    clearInterval(xhr._progressInterval);
    loadingStatus.innerText = 'Connection failed';
    if (window.showToast) window.showToast('error', 'Connection Failed', 'Is the backend running on port 8000?');
    setTimeout(() => { loadingOverlay.style.display = 'none'; }, 2000);
    fileInput.value = '';
  });

  xhr.addEventListener('timeout', () => {
    clearInterval(xhr._progressInterval);
    loadingStatus.innerText = 'Request timed out';
    if (window.showToast) window.showToast('error', 'Timeout', 'Try a shorter video');
    setTimeout(() => { loadingOverlay.style.display = 'none'; }, 2000);
    fileInput.value = '';
  });

  xhr.open('POST', 'http://localhost:8000/analyze');
  xhr.timeout = 300000;
  xhr.send(formData);
}

// Movement icons based on category - Extended with all 35+ movements
const MOVEMENT_ICONS = {
  // Fundamental
  'ginga': '🦵',
  // Kicks
  'armada': '💨', 'meia': '🦶', 'bencao': '🥋', 'martelo': '⚡', 'queixada': '🌀',
  'chapa': '🦿', 'ponteira': '👟', 'gancho': '🪝', 'rabo': '🦂', 'chibata': '🎯',
  'pisao': '👢', 'joelhada': '🦵', 'cotovelhada': '💪', 'cabecada': '🗣️',
  'escorpiao': '🦂',
  // Defense
  'esquiva': '🛡️', 'negativa': '⬇️', 'cocorinha': '🧎', 'role': '🔄', 'resistencia': '💪',
  'queda': '⬇️',
  // Acrobatics
  'au': '🤸', 'macaco': '🐒', 'bananeira': '🍌', 'ponte': '🌉', 's_dobrado': '🔀',
  'parafuso': '🌪️', 'piao': '🌀', 'mortal': '🔄', 'folha': '🍃',
  // Takedowns
  'rasteira': '🧹', 'banda': '🦵', 'tesoura': '✂️', 'vingativa': '⚔️',
  // Default
  'default': '🎯'
};

function getMovementIcon(name) {
  const lower = name.toLowerCase();
  for (const [key, icon] of Object.entries(MOVEMENT_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return MOVEMENT_ICONS.default;
}

function getMovementCategory(name) {
  const lower = name.toLowerCase();
  // Fundamental
  if (lower.includes('ginga')) return 'Fundamental';
  // Acrobatics
  if (lower.includes('au') || lower.includes('macaco') || lower.includes('bananeira') ||
      lower.includes('ponte') || lower.includes('queda_de_rins') || lower.includes('s_dobrado') ||
      lower.includes('parafuso') || lower.includes('piao') || lower.includes('mortal') ||
      lower.includes('folha')) return 'Acrobatic';
  // Defense
  if (lower.includes('esquiva') || lower.includes('negativa') || lower.includes('cocorinha') ||
      lower.includes('role') || lower.includes('resistencia') || lower.includes('queda_de_quatro'))
    return 'Defense';
  // Takedowns
  if (lower.includes('rasteira') || lower.includes('banda') || lower.includes('tesoura') ||
      lower.includes('vingativa')) return 'Takedown';
  // Kicks (largest category)
  if (lower.includes('armada') || lower.includes('meia') || lower.includes('bencao') ||
      lower.includes('martelo') || lower.includes('queixada') || lower.includes('chapa') ||
      lower.includes('ponteira') || lower.includes('gancho') || lower.includes('rabo') ||
      lower.includes('chibata') || lower.includes('pisao') || lower.includes('joelhada') ||
      lower.includes('cotovelhada') || lower.includes('cabecada') || lower.includes('escorpiao'))
    return 'Kick';
  return 'Movement';
}

function updateDashboard(data) {
  // Update Header & Stats
  if (sessionIdEl) sessionIdEl.innerText = `#${data.session_id?.split('-')[1] || '0000'}`;

  // Update overall score with animation
  if (overallScoreEl) {
    overallScoreEl.textContent = data.overall_score?.toFixed(1) || '0.0';
  }

  // Update score ring
  if (scoreRing) {
    const scorePercent = (data.overall_score || 0) / 10;
    const circumference = 251.2;
    const offset = circumference - (scorePercent * circumference);
    scoreRing.style.strokeDashoffset = offset;
  }

  // Update stats
  if (detectionRateEl) {
    detectionRateEl.innerHTML = `${data.detection_stats?.detection_rate?.toFixed(1) || '0.0'}<span class="unit">%</span>`;
  }
  if (movementCountEl) {
    movementCountEl.textContent = data.movements?.length || 0;
  }
  if (flowScoreEl && data.combination_analysis) {
    flowScoreEl.textContent = (data.combination_analysis.overall_score / 10).toFixed(1);
  }

  // Update Movement List with new design
  if (movementList) {
    movementList.innerHTML = '';
    const labels = [];
    const scores = [];
    const stabilities = [];

    (data.movements || []).forEach(m => {
      const scoreClass = m.overall_score >= 7 ? 'high' : (m.overall_score >= 5 ? 'mid' : 'low');
      const progressColor = m.overall_score >= 7 ? 'var(--accent-green)' : (m.overall_score >= 5 ? 'var(--accent-gold)' : 'var(--accent-red)');

      const div = document.createElement('div');
      div.className = 'movement-item';
      div.innerHTML = `
        <div class="movement-icon">${getMovementIcon(m.movement_name)}</div>
        <div class="movement-info">
          <div class="movement-name">${m.movement_name}</div>
          <div class="movement-category">${getMovementCategory(m.movement_name)}</div>
        </div>
        <div class="movement-score ${scoreClass}">${m.overall_score.toFixed(1)}</div>
        <div class="movement-progress" style="width: ${m.overall_score * 10}%; background: ${progressColor};"></div>
      `;
      div.onclick = () => {
        document.getElementById('feedback-panel')?.scrollIntoView({ behavior: 'smooth' });
        document.querySelectorAll('.feedback-card').forEach(c => c.style.outline = 'none');
        const card = document.getElementById(`feedback-${m.movement_name.replace(/\s+/g, '-')}`);
        if (card) card.style.outline = '2px solid var(--accent-gold)';
      };
      movementList.appendChild(div);

      labels.push(m.movement_name);
      scores.push(m.overall_score);
      stabilities.push(Math.max(0, m.overall_score - (Math.random() * 1.5)));
    });

    // Update chart
    if (labels.length > 0) {
      initChart(labels, scores, stabilities);
      const placeholder = document.getElementById('chart-placeholder');
      if (placeholder) placeholder.style.display = 'none';
    }
  }

  // Update sequence timeline
  const sequenceTimeline = document.getElementById('sequence-timeline');
  if (sequenceTimeline && data.combination_analysis?.movement_sequence) {
    sequenceTimeline.innerHTML = '';
    data.combination_analysis.movement_sequence.forEach((name) => {
      const isGinga = name.toLowerCase().includes('ginga');
      const node = document.createElement('div');
      node.className = 'sequence-node';
      node.innerHTML = `
        <div class="sequence-dot" style="background: ${isGinga ? 'var(--accent-green)' : 'var(--accent-gold)'};"></div>
        <div class="sequence-label">${name}</div>
      `;
      sequenceTimeline.appendChild(node);
    });

    // Update flow stats
    const transitionCount = document.getElementById('transition-count');
    const smoothTransitions = document.getElementById('smooth-transitions');
    const rhythmScore = document.getElementById('rhythm-score');

    if (transitionCount) transitionCount.textContent = data.combination_analysis.transitions_analyzed || 0;
    if (smoothTransitions) smoothTransitions.textContent = `${Math.round(data.combination_analysis.transition_score || 0)}%`;
    if (rhythmScore) {
      const rhythm = data.combination_analysis.rhythm_score || 0;
      rhythmScore.textContent = rhythm >= 80 ? 'Excellent' : rhythm >= 60 ? 'Good' : rhythm >= 40 ? 'Fair' : 'Needs Work';
    }
  }

  // --- Populate Feedback Panel ---
  const feedbackPanel = document.getElementById('feedback-panel');
  const feedbackCards = document.getElementById('feedback-cards');
  if (!feedbackCards) return;
  feedbackCards.innerHTML = '';

  // Show raw detected movements summary if available
  if (data.detected_movements_raw && data.detected_movements_raw.length > 0) {
    const summaryCard = document.createElement('div');
    summaryCard.style.cssText = `
      grid-column: 1 / -1;
      background: rgba(244, 196, 48, 0.08);
      border: 1px solid rgba(244, 196, 48, 0.3);
      border-radius: 16px;
      padding: 1.2rem;
      margin-bottom: 0.5rem;
    `;
    const movementTags = data.detected_movements_raw.map(m =>
      `<span style="display: inline-block; background: rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 20px; margin: 4px; font-size: 0.8rem;">
        ${getMovementIcon(m.name)} <strong>${m.name_pt || m.name}</strong>
        <span style="color: var(--text-secondary);">(${m.segments}x)</span>
      </span>`
    ).join('');
    summaryCard.innerHTML = `
      <div style="font-size: 0.75rem; color: var(--accent-gold); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">🎯 Detected Movements</div>
      <div style="display: flex; flex-wrap: wrap; gap: 4px;">${movementTags}</div>
    `;
    feedbackCards.appendChild(summaryCard);
  }

  (data.movements || []).forEach(m => {
    const isGood = m.overall_score >= 7;
    const isMid = m.overall_score >= 5;
    const scoreColor = isGood ? '#00ff88' : (isMid ? '#FFD700' : '#ff4444');
    const scoreLabel = isGood ? '✅ Good' : (isMid ? '⚠️ Needs Work' : '❌ Poor');

    // Separate feedback into positives and negatives
    const feedbackList = m.feedback || [];
    const positives = feedbackList.filter(f =>
      /good|great|excellent|correct|proper|well|strong|maintain/i.test(f)
    );
    const negatives = feedbackList.filter(f =>
      /too|not|need|low|high|lack|incorrect|improve|weak|missing/i.test(f)
    );
    // Anything not categorized goes to negatives
    const uncategorized = feedbackList.filter(f => !positives.includes(f) && !negatives.includes(f));
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

    const noFeedbackHtml = feedbackList.length === 0
      ? `<p style="color: var(--text-secondary); font-size: 0.85rem;">Movement detected but limited pose data for detailed scoring.</p>`
      : '';

    // Detection info (if available from auto-detection)
    const detectionInfo = m.detection_count
      ? `<div style="display: flex; gap: 0.75rem; margin-bottom: 0.75rem; font-size: 0.75rem;">
          <span style="background: rgba(77, 159, 255, 0.15); padding: 3px 8px; border-radius: 6px; color: #4d9fff;">
            ${m.detection_segments || 1}x detected
          </span>
          <span style="background: rgba(0, 214, 125, 0.15); padding: 3px 8px; border-radius: 6px; color: #00d67d;">
            ${m.detection_confidence || 0}% conf
          </span>
          <span style="background: rgba(255, 255, 255, 0.08); padding: 3px 8px; border-radius: 6px; color: var(--text-secondary);">
            ${m.category || 'Movement'}
          </span>
        </div>`
      : '';

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
        <div>
          <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            ${getMovementIcon(m.detected_as || m.movement_name)}
            ${m.movement_name}
          </h4>
          ${m.detected_as && m.detected_as !== m.movement_name ? `<div style="font-size: 0.75rem; color: var(--text-secondary);">Detected as: ${m.detected_as}</div>` : ''}
        </div>
        <div style="text-align: right;">
          <div style="font-size: 1.75rem; font-weight: 800; color: ${scoreColor};">${m.overall_score.toFixed(1)}<span style="font-size: 0.85rem; color: var(--text-secondary);">/10</span></div>
          <div style="font-size: 0.75rem; color: ${scoreColor};">${scoreLabel}</div>
        </div>
      </div>
      ${detectionInfo}
      <div style="display: flex; gap: 1.25rem; margin-bottom: 1rem; font-size: 0.8rem; color: var(--text-secondary); padding: 0.5rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
        <span>Peak: <strong style="color: #fff;">${(m.peak_score || 0).toFixed(1)}</strong></span>
        <span>Avg: <strong style="color: #fff;">${(m.average_score || 0).toFixed(1)}</strong></span>
        <span>Low: <strong style="color: #fff;">${(m.lowest_score || 0).toFixed(1)}</strong></span>
      </div>
      <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; line-height: 1.7;">
        ${positivesHtml}
        ${negativesHtml}
        ${noFeedbackHtml}
      </ul>
    `;
    feedbackCards.appendChild(card);
  });

  // Add combination analysis feedback if available
  if (data.combination_analysis) {
    const ca = data.combination_analysis;
    const flowCard = document.createElement('div');
    flowCard.style.cssText = `
      grid-column: 1 / -1;
      background: linear-gradient(135deg, rgba(0, 214, 125, 0.08), rgba(77, 159, 255, 0.08));
      border: 1px solid rgba(0, 214, 125, 0.3);
      border-radius: 16px;
      padding: 1.5rem;
    `;

    const strengthsHtml = (ca.strengths || []).map(s => `<li style="color: #00ff88; margin-bottom: 4px;">✅ ${s}</li>`).join('');
    const improvementsHtml = (ca.areas_to_improve || []).map(s => `<li style="color: #ff6b6b; margin-bottom: 4px;">📈 ${s}</li>`).join('');

    flowCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="font-size: 1rem; font-weight: 700;">🌊 Movement Flow Analysis</h4>
        <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-gold);">${ca.level || 'N/A'}</div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
        <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Transitions</div>
          <div style="font-weight: 700;">${Math.round(ca.transition_score || 0)}%</div>
        </div>
        <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Rhythm</div>
          <div style="font-weight: 700;">${Math.round(ca.rhythm_score || 0)}%</div>
        </div>
        <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Sequence</div>
          <div style="font-weight: 700;">${Math.round(ca.sequence_logic_score || 0)}%</div>
        </div>
        <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Recovery</div>
          <div style="font-weight: 700;">${Math.round(ca.recovery_score || 0)}%</div>
        </div>
        <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Variety</div>
          <div style="font-weight: 700;">${Math.round(ca.variety_score || 0)}%</div>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        ${strengthsHtml ? `<div><div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Strengths</div><ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem;">${strengthsHtml}</ul></div>` : ''}
        ${improvementsHtml ? `<div><div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Areas to Improve</div><ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem;">${improvementsHtml}</ul></div>` : ''}
      </div>
    `;
    feedbackCards.appendChild(flowCard);
  }

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
