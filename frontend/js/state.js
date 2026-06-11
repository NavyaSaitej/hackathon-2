/**
 * QuickCards — State Router Module
 *
 * Manages the 4-state application lifecycle:
 *   Landing → Loading → Quiz → Summary
 *
 * This is the entry-point module loaded by index.html.
 */

import { generateDeck } from "./api.js";
import { exportAnki, getSummaryData, initQuiz, nextCard, prevCard, toggleSound, renderReviewMistakes } from "./ui.js";
import { clearVideo, loadVideo } from "./video.js";

// ── YouTube URL Regex ─────────────────────────
const YT_REGEX =
  /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})(?:[?&].*)?$/;

// Demo URL for 1-click judge testing
const DEMO_URL = "https://www.youtube.com/watch?v=Dq6dBoFor00";

// ── DOM References ────────────────────────────
const states = {
  landing: document.getElementById("state-landing"),
  loading: document.getElementById("state-loading"),
  quiz: document.getElementById("state-quiz"),
  summary: document.getElementById("state-summary"),
};

const urlInput = document.getElementById("youtube-url");
const btnGenerate = document.getElementById("btn-generate");
const btnDemoUrl = document.getElementById("btn-demo-url");
const loadingStatus = document.getElementById("loading-status");
const loadingProgress = document.getElementById("loading-progress");
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const finalScore = document.getElementById("final-score");
const totalCardsEl = document.getElementById("total-cards");
const summaryMessage = document.getElementById("summary-message");
const btnExport = document.getElementById("btn-export-anki");
const btnRestart = document.getElementById("btn-restart");
const btnShareResults = document.getElementById("btn-share-results");
const soundToggle = document.getElementById("sound-toggle");

// ── Theme Toggle ──────────────────────────────
const themeToggle = document.getElementById("theme-toggle");
const languageSelect = document.getElementById("language-select");

// ── Localization (i18n) ───────────────────────
const i18n = {
  English: {
    heroSubtitle: "Transform any YouTube video into interactive quiz flashcards — powered by AI.",
    demoBtn: "Demo",
    generateBtn: "Generate Cards",
    feat1Title: "AI-Powered",
    feat1Desc: "Gemini generates smart questions with plausible distractors.",
    feat2Title: "Timestamp Links",
    feat2Desc: "Every card links to the exact moment in the video.",
    feat3Title: "Anki Export",
    feat3Desc: "Download your deck as a ready-to-import Anki file.",
    loading: "Fetching transcript...",
    videoLabel: "Video",
    questionLabel: "Question",
    answerLabel: "Correct Answer",
    prevBtn: "Prev",
    nextBtn: "Next",
    quizComplete: "Quiz Complete!",
    greatEffort: "Great effort!",
    exportAnkiBtn: "Export to Anki",
    newVideoBtn: "New Video",
    loadingText: "Fetching transcript..."
  },
  Hindi: {
    heroSubtitle: "किसी भी YouTube वीडियो को इंटरैक्टिव क्विज़ फ्लैशकार्ड में बदलें — AI द्वारा संचालित।",
    demoBtn: "डेमो",
    generateBtn: "कार्ड जनरेट करें",
    feat1Title: "AI-संचालित",
    feat1Desc: "Gemini संभावित विकल्पों के साथ स्मार्ट प्रश्न उत्पन्न करता है।",
    feat2Title: "टाइमस्टैम्प लिंक",
    feat2Desc: "हर कार्ड वीडियो के सटीक क्षण से लिंक होता है।",
    feat3Title: "Anki निर्यात",
    feat3Desc: "अपने डेक को Anki फ़ाइल के रूप में डाउनलोड करें।",
    loading: "ट्रांसक्रिप्ट प्राप्त कर रहा है...",
    videoLabel: "वीडियो",
    questionLabel: "प्रश्न",
    answerLabel: "सही उत्तर",
    prevBtn: "पिछला",
    nextBtn: "अगला",
    quizComplete: "क्विज़ पूरा हुआ!",
    greatEffort: "बहुत बढ़िया प्रयास!",
    exportAnkiBtn: "Anki में निर्यात करें",
    newVideoBtn: "नया वीडियो",
    loadingText: "ट्रांसक्रिप्ट प्राप्त कर रहा है..."
  },
  Telugu: {
    heroSubtitle: "ఏదైనా YouTube వీడియోను ఇంటరాక్టివ్ క్విజ్ ఫ్లాష్‌కార్డ్‌లుగా మార్చండి — AI ద్వారా శక్తిని పొందుతుంది.",
    demoBtn: "డెమో",
    generateBtn: "కార్డులను రూపొందించండి",
    feat1Title: "AI-ఆధారితం",
    feat1Desc: "Gemini ఆమోదయోగ్యమైన ఎంపికలతో స్మార్ట్ ప్రశ్నలను సృష్టిస్తుంది.",
    feat2Title: "టైమ్‌స్టాంప్ లింక్‌లు",
    feat2Desc: "ప్రతి కార్డు వీడియోలోని ఖచ్చితమైన సమయానికి లింక్ చేస్తుంది.",
    feat3Title: "Anki ఎగుమతి",
    feat3Desc: "మీ డెక్‌ను Anki ఫైల్‌గా డౌన్‌లోడ్ చేసుకోండి.",
    loading: "ట్రాన్స్క్రిప్ట్ పొందుతోంది...",
    videoLabel: "వీడియో",
    questionLabel: "ప్రశ్న",
    answerLabel: "సరైన సమాధానం",
    prevBtn: "మునుపటి",
    nextBtn: "తదుపరి",
    quizComplete: "క్విజ్ పూర్తయింది!",
    greatEffort: "గొప్ప ప్రయత్నం!",
    exportAnkiBtn: "Anki కి ఎగుమతి చేయండి",
    newVideoBtn: "కొత్త వీడియో",
    loadingText: "ట్రాన్స్క్రిప్ట్ పొందుతోంది..."
  }
};

function updateLanguage(lang) {
  const dict = i18n[lang];
  if (!dict) return;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
}

if (languageSelect) {
  languageSelect.addEventListener("change", (e) => {
    updateLanguage(e.target.value);
    if (states.quiz.classList.contains("active") || states.summary.classList.contains("active")) {
      btnGenerate.click();
    }
  });
}
const rootHtml = document.documentElement;
let currentTheme = localStorage.getItem("theme") || "dark";

function applyTheme() {
  if (currentTheme === "light") {
    rootHtml.setAttribute("data-theme", "light");
    themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
  } else if (currentTheme === "oled") {
    rootHtml.setAttribute("data-theme", "oled");
    themeToggle.innerHTML = '<i class="fa-solid fa-circle-half-stroke"></i>';
  } else {
    rootHtml.removeAttribute("data-theme");
    themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
  }
}

// Initial apply
applyTheme();

// ── Daily Streak Logic ────────────────────────
function initStreakDisplay() {
  const streak = parseInt(localStorage.getItem("streak_count")) || 0;
  const streakCountEl = document.getElementById("streak-count");
  if (streakCountEl) streakCountEl.textContent = streak;
}

function updateStreak() {
  const today = new Date().toDateString();
  let streak = parseInt(localStorage.getItem("streak_count")) || 0;
  const lastPlayed = localStorage.getItem("last_played_date");

  if (lastPlayed !== today) {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (lastPlayed === yesterday.toDateString()) {
      streak += 1;
    } else {
      streak = 1;
    }
    localStorage.setItem("streak_count", streak);
    localStorage.setItem("last_played_date", today);
  }
  
  const streakCountEl = document.getElementById("streak-count");
  if (streakCountEl) streakCountEl.textContent = streak;
}

initStreakDisplay();

themeToggle.addEventListener("click", () => {
  if (currentTheme === "dark") currentTheme = "light";
  else if (currentTheme === "light") currentTheme = "oled";
  else currentTheme = "dark";
  
  localStorage.setItem("theme", currentTheme);
  applyTheme();
});

if (soundToggle) {
  soundToggle.addEventListener("click", () => {
    const isEnabled = toggleSound();
    soundToggle.innerHTML = isEnabled 
      ? '<i class="fa-solid fa-volume-high"></i>' 
      : '<i class="fa-solid fa-volume-xmark"></i>';
  });
}

// ── Settings Modal ────────────────────────────
const btnSettings = document.getElementById("btn-settings");
const settingsModal = document.getElementById("settings-modal");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnSaveSettings = document.getElementById("btn-save-settings");
const aiProviderSelect = document.getElementById("ai-provider");
const byokSettings = document.getElementById("byok-settings");
const localSettings = document.getElementById("local-settings");
const geminiApiKey = document.getElementById("gemini-api-key");
const localEndpoint = document.getElementById("local-endpoint");
const localModel = document.getElementById("local-model");

function loadSettings() {
  if (!aiProviderSelect) return;
  aiProviderSelect.value = localStorage.getItem("ai_provider") || "gemini";
  geminiApiKey.value = localStorage.getItem("gemini_api_key") || "";
  localEndpoint.value = localStorage.getItem("local_endpoint") || "http://localhost:11434/api/chat";
  localModel.value = localStorage.getItem("local_model") || "llama3";
  updateSettingsUI();
}

function updateSettingsUI() {
  byokSettings.style.display = aiProviderSelect.value === "byok" ? "block" : "none";
  localSettings.style.display = aiProviderSelect.value === "local" ? "block" : "none";
}

if (aiProviderSelect) aiProviderSelect.addEventListener("change", updateSettingsUI);

if (btnSettings) {
  btnSettings.addEventListener("click", () => {
    loadSettings();
    settingsModal.style.display = "flex";
  });
}

if (btnCloseSettings) {
  btnCloseSettings.addEventListener("click", () => {
    settingsModal.style.display = "none";
  });
}

if (btnSaveSettings) {
  btnSaveSettings.addEventListener("click", () => {
    localStorage.setItem("ai_provider", aiProviderSelect.value);
    localStorage.setItem("gemini_api_key", geminiApiKey.value.trim());
    localStorage.setItem("local_endpoint", localEndpoint.value.trim());
    localStorage.setItem("local_model", localModel.value.trim());
    settingsModal.style.display = "none";
  });
}

// Load settings on init
loadSettings();

// ── Help Modal ───────────────────────────────
const btnHelp = document.getElementById("btn-help");
const helpModal = document.getElementById("help-modal");
const btnCloseHelp = document.getElementById("btn-close-help");

if (btnHelp) {
  btnHelp.addEventListener("click", () => {
    helpModal.style.display = "flex";
  });
}

if (btnCloseHelp) {
  btnCloseHelp.addEventListener("click", () => {
    helpModal.style.display = "none";
  });
}

// ── PWA Install Prompt ────────────────────────
let deferredPrompt;
const btnInstall = document.getElementById("btn-install");

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (btnInstall) {
    btnInstall.style.display = "inline-flex";
  }
});

if (btnInstall) {
  btnInstall.addEventListener("click", async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    deferredPrompt = null;
    btnInstall.style.display = "none";
  });
}

// ── State Transitions ─────────────────────────
function showState(name) {
  Object.values(states).forEach((s) => s.classList.remove("active"));
  states[name].classList.add("active");
}

// ── URL Validation ────────────────────────────
function validateUrl() {
  const isValid = YT_REGEX.test(urlInput.value.trim());
  btnGenerate.disabled = !isValid;
  return isValid;
}

urlInput.addEventListener("input", validateUrl);

// ── Demo URL Button ───────────────────────────
btnDemoUrl.addEventListener("click", () => {
  urlInput.value = DEMO_URL;
  validateUrl();
  urlInput.focus();
});

// ── Progressive Loading Animation ─────────────
function animateLoading(lang) {
  const allStages = {
    English: [
      { text: "Fetching transcript...", progress: 25 },
      { text: "Analyzing content...", progress: 55 },
      { text: "Generating quiz cards...", progress: 85 },
    ],
    Hindi: [
      { text: "ट्रांसक्रिप्ट प्राप्त कर रहा है...", progress: 25 },
      { text: "सामग्री का विश्लेषण कर रहा है...", progress: 55 },
      { text: "क्विज़ कार्ड बना रहा है...", progress: 85 },
    ],
    Telugu: [
      { text: "ట్రాన్స్క్రిప్ట్ పొందుతోంది...", progress: 25 },
      { text: "కంటెంట్ విశ్లేషిస్తోంది...", progress: 55 },
      { text: "క్విజ్ కార్డులు సృష్టిస్తోంది...", progress: 85 },
    ]
  };

  const stages = allStages[lang] || allStages.English;

  stages.forEach((stage, i) => {
    setTimeout(() => {
      loadingStatus.textContent = stage.text;
      loadingProgress.style.width = `${stage.progress}%`;
    }, i * 2500);
  });
}

// ── Generate Flow ─────────────────────────────
btnGenerate.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!YT_REGEX.test(url)) return;

  const language = languageSelect ? languageSelect.value : "English";

  // Transition to loading
  showState("loading");
  animateLoading(language);

  try {
    const deckData = await generateDeck(url, language);

    // Complete progress bar
    loadingProgress.style.width = "100%";
    loadingStatus.textContent = language === "Hindi" ? "पूरा हुआ!" : language === "Telugu" ? "పూర్తయింది!" : "Done!";

    // Short pause to let user see completion
    await new Promise((r) => setTimeout(r, 500));

    // Load video
    loadVideo(deckData.video_id, deckData.video_title);

    // Initialize quiz
    initQuiz(deckData);

    // Transition to quiz
    showState("quiz");
  } catch (err) {
    // Return to landing with error
    showState("landing");
    alert(`Error: ${err.message}`);
  }
});

// ── Quiz Navigation ───────────────────────────
btnPrev.addEventListener("click", prevCard);

btnNext.addEventListener("click", () => {
  const moved = nextCard();
  if (!moved) {
    // Quiz complete — show summary
    const data = getSummaryData();
    finalScore.textContent = data.score;
    totalCardsEl.textContent = data.total;
    summaryMessage.textContent = data.message;
    
    updateStreak();
    renderReviewMistakes();

    showState("summary");

    // Trigger Confetti if perfect score
    if (data.score === data.total && typeof confetti === "function") {
      confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
    }
  }
});

// ── Global Keyboard Shortcuts ────────────────
document.addEventListener("keydown", (e) => {
  if (!states.quiz.classList.contains("active")) return;
  
  if (e.key === "ArrowLeft") {
    if (!btnPrev.disabled) btnPrev.click();
  } else if (e.key === "ArrowRight") {
    if (!btnNext.disabled) btnNext.click();
  } else if (e.code === "Space") {
    e.preventDefault(); // Prevent scrolling down
    const flashcard = document.getElementById("flashcard");
    if (flashcard) flashcard.classList.toggle("flipped");
  } else if (["1", "2", "3", "4"].includes(e.key)) {
    const choicesContainer = document.getElementById("choices-container");
    const buttons = choicesContainer.querySelectorAll(".choice-btn");
    const idx = parseInt(e.key) - 1;
    if (buttons[idx] && !buttons[idx].disabled) {
      buttons[idx].click();
    }
  }
});

// ── Summary Actions ───────────────────────────
btnExport.addEventListener("click", exportAnki);

if (btnShareResults) {
  btnShareResults.addEventListener("click", () => {
    const data = getSummaryData();
    const text = `I just scored ${data.score}/${data.total} on QuickCards AI Flashcards! 🧠⚡\n\nTry it out: ${window.location.href}`;
    if (navigator.share) {
      navigator.share({
        title: "My QuickCards Score",
        text: text,
        url: window.location.href
      }).catch(console.error);
    } else {
      navigator.clipboard.writeText(text);
      alert("Score copied to clipboard!");
    }
  });
}

btnRestart.addEventListener("click", () => {
  urlInput.value = "";
  btnGenerate.disabled = true;
  clearVideo();

  // Reset loading state
  loadingProgress.style.width = "0%";
  const lang = languageSelect ? languageSelect.value : "English";
  loadingStatus.textContent = i18n[lang]?.loadingText || "Fetching transcript...";

  showState("landing");
});

// ── PWA Service Worker Registration ───────────
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {
    // SW registration failure is non-critical
  });
}
