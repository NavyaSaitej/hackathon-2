# QuickCards — User Manual

## Getting Started

### What is QuickCards?
QuickCards transforms YouTube educational videos into interactive quiz flashcards. Paste a YouTube URL, and our AI will generate a multiple-choice quiz deck that tests your understanding of the video content.

### How to Use

1. **Open QuickCards** in your browser.
2. **Paste a YouTube URL** into the input field, or click the ⚡ **Demo** button to use a sample video.
3. Click **Generate Cards** (the button activates once a valid URL is detected).
4. Wait while the AI processes your video (typically 5-15 seconds).
5. **Take the Quiz!** Select your answer from the 4 options displayed.
6. After answering, the card flips to reveal the correct answer and explanation.
7. Click the **Jump to** button to watch the relevant part of the video.
8. Navigate with **Prev/Next** buttons.
9. At the end, view your **score** and optionally **Export to Anki**.

### Features in Detail

#### Interactive Quiz Mode
Each card presents a question with 4 choices (1 correct + 3 plausible distractors). After selecting an answer:
- ✅ Correct answers glow green with a checkmark icon.
- ❌ Wrong answers glow red with an X icon, and the correct answer is highlighted.

#### Contextual Video Timestamps
Every flashcard has a "Jump to X:XX" button on its back side. Clicking it seeks the embedded YouTube player to the exact moment the concept was discussed.

#### Anki Export
On the summary screen, click **Export to Anki** to download a `.txt` file. Import this file into Anki using the "Tab-separated" option.

#### Progressive Web App (PWA)
QuickCards can be installed on your phone or desktop. Look for the "Install" prompt in your browser's address bar.

### Troubleshooting

| Issue | Solution |
|---|---|
| "Generate" button stays disabled | Ensure your URL matches `youtube.com/watch?v=...` or `youtu.be/...` format |
| "Transcript too short" error | The video needs English captions with at least 100 words |
| "Video too long" error | Videos must be under 20 minutes |
| "Rate limit exceeded" | Maximum 5 generations per hour — wait and try again |
| Cards not loading | Check your internet connection; the backend may be warming up (up to 30s on first request) |

### Privacy
- QuickCards uses `youtube-nocookie.com` for video embeds to prevent tracking.
- No user data is stored on our servers. All processing happens in memory and is immediately discarded.
- Your quiz data is only stored locally in your browser.
