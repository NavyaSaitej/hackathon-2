/**
 * QuickCards — API Module
 *
 * Handles all communication with the FastAPI backend.
 * Injects the X-App-Secret handshake header on every request.
 */

// Backend URL — update for production
const API_BASE =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : ''; // Use relative path on Vercel

const APP_SECRET = 'quickcards-dev-secret'; // Must match backend .env

/**
 * Send a YouTube URL to the backend and receive a quiz deck.
 * @param {string} url - The YouTube video URL
 * @param {string} language - The selected language for the quiz
 * @returns {Promise<Object>} The deck JSON
 * @throws {Error} with user-friendly message
 */
export async function generateDeck(url, language = 'English') {
  let aiProvider = localStorage.getItem('ai_provider') || 'gemini';
  const apiKey = localStorage.getItem('gemini_api_key') || '';
  const localEndpoint = localStorage.getItem('local_endpoint') || 'http://localhost:11434/api/chat';
  const localModel = localStorage.getItem('local_model') || 'llama3';

  // Force default Gemini provider for the hardcoded Demo Video to ensure it remains instant
  if (url.includes('Dq6dBoFor00')) {
    aiProvider = 'gemini';
  }

  if (aiProvider === 'local') {
    // 1. Fetch transcript from backend
    const transcriptRes = await fetch(`${API_BASE}/transcript`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-App-Secret': APP_SECRET,
      },
      body: JSON.stringify({ url }),
    });

    if (!transcriptRes.ok) {
      const data = await transcriptRes.json().catch(() => ({}));
      throw new Error(data.detail || `Server error fetching transcript (${transcriptRes.status})`);
    }

    const { video_id, transcript } = await transcriptRes.json();

    // 2. Local inference with Ollama
    const systemPrompt = `You are an expert educational content creator. Given a video transcript
with [TS:seconds] annotations, generate a quiz deck as valid JSON.

RULES:
1. Each question must test a distinct key concept from the transcript.
2. The correct_answer must be factually accurate per the transcript.
3. Each distractor must be plausible but clearly wrong.
4. The explanation must be exactly 1 sentence.
5. timestamp_seconds MUST be copied from the nearest [TS:seconds] tag
   in the transcript — do NOT invent timestamps.
6. Before outputting, internally verify: are all 3 distractors actually
   wrong? Is the correct_answer actually supported by the transcript?

OUTPUT FORMAT (strict JSON, no markdown fences):
{
  "video_title": "...",
  "cards": [
    {
      "question": "...",
      "correct_answer": "...",
      "distractors": ["...", "...", "..."],
      "explanation": "...",
      "timestamp_seconds": 0
    }
  ]
}`;

    // Calculate approx cards like backend does
    const wordCount = transcript.split(' ').length;
    let cardCount = 3;
    if (wordCount >= 500 && wordCount < 1500) cardCount = 5;
    else if (wordCount >= 1500) cardCount = 8;

    const userPrompt = `Generate exactly ${cardCount} quiz cards from this transcript.
The quiz cards (question, correct_answer, distractors, explanation) MUST be written in the ${language} language.
The JSON keys MUST remain in English.

Transcript:
${transcript}`;

    let ollamaRes;
    try {
      ollamaRes = await fetch(localEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: localModel,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt },
          ],
          stream: false,
          format: 'json',
          options: { temperature: 0.0 },
        }),
      });
    } catch (_e) {
      throw new Error(
        `Failed to connect to Local AI at ${localEndpoint}.\n\n` +
          `If using localhost, modern browsers block public sites from accessing local ports (Private Network Access).\n` +
          `Workarounds:\n` +
          `1. Run 'ngrok http 11434' and paste the ngrok HTTPS URL here.\n` +
          `2. Or, run this website locally on your machine.`
      );
    }

    if (!ollamaRes.ok) {
      throw new Error(`Local AI error (${ollamaRes.status})`);
    }

    const ollamaData = await ollamaRes.json();
    try {
      const parsed = JSON.parse(ollamaData.message.content);
      parsed.video_id = video_id;
      return parsed;
    } catch (_e) {
      throw new Error('Failed to parse JSON from Local AI.');
    }
  }

  // Gemini (Default or BYOK)
  const body = { url, language };
  if (aiProvider === 'byok' && apiKey) {
    body.api_key = apiKey;
  }

  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-App-Secret': APP_SECRET,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = data.detail || `Server error (${response.status})`;
    throw new Error(detail);
  }

  return response.json();
}
