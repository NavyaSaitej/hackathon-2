/**
 * QuickCards — API Module
 *
 * Handles all communication with the FastAPI backend.
 * Injects the X-App-Secret handshake header on every request.
 */

// Backend URL — update for production
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8080"
    : ""; // Use relative path on Vercel

const APP_SECRET = "quickcards-dev-secret"; // Must match backend .env

/**
 * Send a YouTube URL to the backend and receive a quiz deck.
 * @param {string} url - The YouTube video URL
 * @param {string} language - The selected language for the quiz
 * @returns {Promise<Object>} The deck JSON
 * @throws {Error} with user-friendly message
 */
export async function generateDeck(url, language = "English") {
  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-App-Secret": APP_SECRET,
    },
    body: JSON.stringify({ url, language }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = data.detail || `Server error (${response.status})`;
    throw new Error(detail);
  }

  return response.json();
}
