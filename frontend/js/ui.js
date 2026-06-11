/**
 * QuickCards — UI Module
 *
 * All DOM manipulation, card rendering, quiz logic,
 * ARIA state management, and Anki export live here.
 */

import { seekTo } from "./video.js";

// ── State ─────────────────────────────────────
let deck = null; // The full deck object from the API
let currentIndex = 0; // Current card index
let score = 0; // Correct answers count
let answered = []; // Track which cards have been answered
let missedCards = []; // Track incorrect answers for review

// ── Audio Context (Web Audio API) ─────────────
const AudioContext = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContext();
let soundEnabled = true;

export function toggleSound() {
  // Resume context if suspended (browser autoplay policy)
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  soundEnabled = !soundEnabled;
  return soundEnabled;
}

function playSound(type) {
  if (!soundEnabled) return;
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  
  const oscillator = audioCtx.createOscillator();
  const gainNode = audioCtx.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  
  if (type === 'correct') {
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
    oscillator.frequency.exponentialRampToValueAtTime(1046.50, audioCtx.currentTime + 0.1); // C6
    gainNode.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.3);
  } else {
    oscillator.type = 'sawtooth';
    oscillator.frequency.setValueAtTime(150, audioCtx.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.2);
    gainNode.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.2);
  }
}

// ── DOM References ────────────────────────────
const cardCounter = document.getElementById("card-counter");
const scoreDisplay = document.getElementById("score-display");
const question = document.getElementById("card-question");
const answer = document.getElementById("card-answer");
const explanation = document.getElementById("card-explanation");
const flashcard = document.getElementById("flashcard");
const cardFront = document.getElementById("card-front");
const cardBack = document.getElementById("card-back");
const choicesContainer = document.getElementById("choices-container");
const btnTimestamp = document.getElementById("btn-timestamp");
const timestampLabel = document.getElementById("timestamp-label");
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const progressFill = document.getElementById("progress-fill");
const finalScore = document.getElementById("final-score");
const totalCards = document.getElementById("total-cards");
const summaryMessage = document.getElementById("summary-message");

/**
 * Initialize the quiz UI with a deck from the API.
 * @param {Object} deckData - The deck JSON from the backend
 */
export function initQuiz(deckData) {
  deck = deckData;
  currentIndex = 0;
  score = 0;
  answered = new Array(deck.cards.length).fill(false);
  missedCards = [];
  renderCard();
}

/**
 * Render the current card: question, choices, progress.
 */
function renderCard() {
  const card = deck.cards[currentIndex];
  const total = deck.cards.length;

  // Progress
  cardCounter.textContent = `Card ${currentIndex + 1} / ${total}`;
  scoreDisplay.innerHTML = `<i class="fa-solid fa-star"></i> ${score}`;

  // Question (front)
  question.textContent = card.question;

  // Answer (back)
  answer.textContent = card.correct_answer;
  explanation.textContent = card.explanation;

  // Update progress bar
  const pct = Math.max(5, (currentIndex / total) * 100);
  progressFill.style.width = `${pct}%`;

  // Timestamp button
  const mins = Math.floor(card.timestamp_seconds / 60);
  const secs = card.timestamp_seconds % 60;
  timestampLabel.textContent = `Jump to ${mins}:${String(secs).padStart(2, "0")}`;

  // Un-flip card
  flashcard.classList.remove("flipped");
  cardFront.setAttribute("aria-hidden", "false");
  cardBack.setAttribute("aria-hidden", "true");

  // Navigation
  btnPrev.disabled = currentIndex === 0;
  btnNext.textContent = currentIndex === total - 1 ? "Finish" : "Next";
  btnNext.innerHTML =
    currentIndex === total - 1
      ? 'Finish <i class="fa-solid fa-flag-checkered"></i>'
      : 'Next <i class="fa-solid fa-chevron-right"></i>';

  // Build choices
  renderChoices(card);
}

/**
 * Render the 4 multiple-choice buttons (1 correct + 3 distractors).
 * Shuffles the order randomly.
 */
function renderChoices(card) {
  choicesContainer.innerHTML = "";

  const options = [card.correct_answer, ...card.distractors];
  shuffle(options);

  const letters = ["A", "B", "C", "D"];

  options.forEach((option, i) => {
    const btn = document.createElement("button");
    btn.className = "choice-btn";
    btn.innerHTML = `<span class="choice-letter">${letters[i]}</span><span>${option}</span>`;

    if (answered[currentIndex]) {
      // Already answered — show results
      btn.classList.add("selected");
      if (option === card.correct_answer) {
        btn.classList.add("correct");
        btn.innerHTML += `<i class="fa-solid fa-circle-check choice-feedback-icon" style="color: var(--correct)"></i>`;
      }
      btn.disabled = true;
    } else {
      btn.addEventListener("click", () => handleChoice(option, card, btn));
    }

    choicesContainer.appendChild(btn);
  });
}

/**
 * Handle a user selecting a choice.
 */
function handleChoice(selected, card, clickedBtn) {
  if (answered[currentIndex]) return;
  answered[currentIndex] = true;

  const isCorrect = selected === card.correct_answer;

  if (isCorrect) {
    score++;
    playSound('correct');
    clickedBtn.classList.add("correct");
    clickedBtn.innerHTML += `<i class="fa-solid fa-circle-check choice-feedback-icon" style="color: var(--correct)"></i>`;
  } else {
    playSound('wrong');
    missedCards.push({
      question: card.question,
      wrongAnswer: selected,
      correctAnswer: card.correct_answer
    });
    clickedBtn.classList.add("wrong");
    clickedBtn.innerHTML += `<i class="fa-solid fa-circle-xmark choice-feedback-icon" style="color: var(--wrong)"></i>`;

    // Highlight the correct answer
    const allBtns = choicesContainer.querySelectorAll(".choice-btn");
    allBtns.forEach((btn) => {
      if (btn.querySelector("span:last-child").textContent === card.correct_answer) {
        btn.classList.add("correct");
        btn.innerHTML += `<i class="fa-solid fa-circle-check choice-feedback-icon" style="color: var(--correct)"></i>`;
      }
    });
  }

  // Disable all choices
  choicesContainer.querySelectorAll(".choice-btn").forEach((btn) => {
    btn.disabled = true;
    btn.style.cursor = "default";
  });

  // Flip card to show answer
  setTimeout(() => {
    flashcard.classList.add("flipped");
    cardFront.setAttribute("aria-hidden", "true");
    cardBack.setAttribute("aria-hidden", "false");
  }, 600);

  // Update score
  scoreDisplay.innerHTML = `<i class="fa-solid fa-star"></i> ${score}`;
}

/**
 * Prepare the summary screen data.
 * Returns an object that state.js uses to populate the summary.
 */
export function getSummaryData() {
  const total = deck.cards.length;
  const pct = Math.round((score / total) * 100);
  let message = "Keep practicing!";
  if (pct >= 90) message = "Outstanding! You crushed it! 🎉";
  else if (pct >= 70) message = "Great job! Solid understanding! 💪";
  else if (pct >= 50) message = "Good effort! Review the tricky ones.";

  return { score, total, message };
}

/**
 * Render the missed cards panel on the summary screen
 */
export function renderReviewMistakes() {
  const container = document.getElementById("review-mistakes-container");
  const list = document.getElementById("review-mistakes-list");
  if (!container || !list) return;

  if (missedCards.length === 0) {
    container.style.display = "none";
  } else {
    container.style.display = "block";
    list.innerHTML = "";
    missedCards.forEach(mc => {
      const li = document.createElement("li");
      li.innerHTML = `
        <div class="review-q">${mc.question}</div>
        <div>
          <span class="review-w"><i class="fa-solid fa-xmark"></i> ${mc.wrongAnswer}</span>
          <span class="review-a"><i class="fa-solid fa-check"></i> ${mc.correctAnswer}</span>
        </div>
      `;
      list.appendChild(li);
    });
  }
}

/**
 * Export the deck to Anki-compatible TSV format.
 * Downloads as a .txt file.
 */
export function exportAnki() {
  if (!deck) return;

  const lines = deck.cards.map((c) => `${c.question}\t${c.correct_answer} — ${c.explanation}`);
  const content = lines.join("\n");
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "quickcards_deck.txt";
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Get the current card index.
 */
export function getCurrentIndex() {
  return currentIndex;
}

/**
 * Get total number of cards.
 */
export function getTotalCards() {
  return deck ? deck.cards.length : 0;
}

/**
 * Navigate to the next card.
 * @returns {boolean} true if moved to next card, false if at the end.
 */
export function nextCard() {
  if (currentIndex < deck.cards.length - 1) {
    currentIndex++;
    renderCard();
    return true;
  }
  return false; // At the end — trigger summary
}

/**
 * Navigate to the previous card.
 */
export function prevCard() {
  if (currentIndex > 0) {
    currentIndex--;
    renderCard();
  }
}

// ── Timestamp button ──────────────────────────
btnTimestamp.addEventListener("click", () => {
  if (deck) {
    seekTo(deck.cards[currentIndex].timestamp_seconds);
  }
});

// ── Utility ───────────────────────────────────
function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}
