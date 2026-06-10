/**
 * QuickCards — State Router Module
 *
 * Manages the 4-state application lifecycle:
 *   Landing → Loading → Quiz → Summary
 *
 * This is the entry-point module loaded by index.html.
 */

import { generateDeck } from './api.js';
import { initQuiz, nextCard, prevCard, getSummaryData, exportAnki } from './ui.js';
import { loadVideo, clearVideo } from './video.js';

// ── YouTube URL Regex ─────────────────────────
const YT_REGEX = /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})(?:&.*)?$/;

// Demo URL for 1-click judge testing
const DEMO_URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';

// ── DOM References ────────────────────────────
const states = {
  landing: document.getElementById('state-landing'),
  loading: document.getElementById('state-loading'),
  quiz: document.getElementById('state-quiz'),
  summary: document.getElementById('state-summary'),
};

const urlInput = document.getElementById('youtube-url');
const btnGenerate = document.getElementById('btn-generate');
const btnDemoUrl = document.getElementById('btn-demo-url');
const loadingStatus = document.getElementById('loading-status');
const loadingProgress = document.getElementById('loading-progress');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const finalScore = document.getElementById('final-score');
const totalCardsEl = document.getElementById('total-cards');
const summaryMessage = document.getElementById('summary-message');
const btnExport = document.getElementById('btn-export-anki');
const btnRestart = document.getElementById('btn-restart');

// ── State Transitions ─────────────────────────
function showState(name) {
  Object.values(states).forEach((s) => s.classList.remove('active'));
  states[name].classList.add('active');
}

// ── URL Validation ────────────────────────────
function validateUrl() {
  const isValid = YT_REGEX.test(urlInput.value.trim());
  btnGenerate.disabled = !isValid;
  return isValid;
}

urlInput.addEventListener('input', validateUrl);

// ── Demo URL Button ───────────────────────────
btnDemoUrl.addEventListener('click', () => {
  urlInput.value = DEMO_URL;
  validateUrl();
  urlInput.focus();
});

// ── Progressive Loading Animation ─────────────
function animateLoading() {
  const stages = [
    { text: 'Fetching transcript...', progress: 25 },
    { text: 'Analyzing content...', progress: 55 },
    { text: 'Generating quiz cards...', progress: 85 },
  ];

  stages.forEach((stage, i) => {
    setTimeout(() => {
      loadingStatus.textContent = stage.text;
      loadingProgress.style.width = `${stage.progress}%`;
    }, i * 2500);
  });
}

// ── Generate Flow ─────────────────────────────
btnGenerate.addEventListener('click', async () => {
  const url = urlInput.value.trim();
  if (!YT_REGEX.test(url)) return;

  // Transition to loading
  showState('loading');
  animateLoading();

  try {
    const deckData = await generateDeck(url);

    // Complete progress bar
    loadingProgress.style.width = '100%';
    loadingStatus.textContent = 'Done!';

    // Short pause to let user see completion
    await new Promise((r) => setTimeout(r, 500));

    // Load video
    loadVideo(deckData.video_id, deckData.video_title);

    // Initialize quiz
    initQuiz(deckData);

    // Transition to quiz
    showState('quiz');
  } catch (err) {
    // Return to landing with error
    showState('landing');
    alert(`Error: ${err.message}`);
  }
});

// ── Quiz Navigation ───────────────────────────
btnPrev.addEventListener('click', prevCard);

btnNext.addEventListener('click', () => {
  const moved = nextCard();
  if (!moved) {
    // Quiz complete — show summary
    const data = getSummaryData();
    finalScore.textContent = data.score;
    totalCardsEl.textContent = data.total;
    summaryMessage.textContent = data.message;
    showState('summary');
  }
});

// ── Summary Actions ───────────────────────────
btnExport.addEventListener('click', exportAnki);

btnRestart.addEventListener('click', () => {
  urlInput.value = '';
  btnGenerate.disabled = true;
  clearVideo();

  // Reset loading state
  loadingProgress.style.width = '0%';
  loadingStatus.textContent = 'Fetching transcript...';

  showState('landing');
});

// ── PWA Service Worker Registration ───────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {
    // SW registration failure is non-critical
  });
}
