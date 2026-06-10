/**
 * QuickCards — API Module
 *
 * Handles all communication with the FastAPI backend.
 * Injects the X-App-Secret handshake header on every request.
 */

// Backend URL — update for production
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://quickcards-api.onrender.com'; // TODO: set actual Render URL

const APP_SECRET = 'quickcards-dev-secret'; // Must match backend .env

/**
 * Send a YouTube URL to the backend and receive a quiz deck.
 * @param {string} url - The YouTube video URL
 * @returns {Promise<Object>} The deck JSON
 * @throws {Error} with user-friendly message
 */
export async function generateDeck(url) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-App-Secret': APP_SECRET,
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = data.detail || `Server error (${response.status})`;
    throw new Error(detail);
  }

  return response.json();
}
