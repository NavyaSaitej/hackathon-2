# Architecture & Tech Stack

## Tech Stack (Vanilla + API approach)
To ensure simplicity and zero build-step overhead for the hackathon, the project will use a Vanilla frontend communicating with serverless/API backends.

- **Frontend:** HTML5, CSS3 (Vanilla, CSS Variables for theming), JavaScript (ES6+).
- **Icons & Fonts:** FontAwesome, Google Fonts (Inter).
- **Transcript API:** A lightweight Python/Node serverless function or an existing rapid API to fetch YouTube transcripts (e.g., `youtube-transcript-api`).
- **AI Triage/Generation:** Google Gemini API or OpenAI API to process the transcript and output structured JSON.

## System Workflow
1. **Client:** User pastes `https://youtube.com/watch?v=...` and clicks "Generate".
2. **Client -> API:** JS extracts the Video ID and sends a request to the Transcript Fetcher.
3. **Transcript Fetcher:** Retrieves the raw text captions.
4. **API -> LLM:** The text is bundled with a strict system prompt (`"You are an educator. Extract 10 flashcards in this exact JSON format: [{q: '...', a: '...'}]"`).
5. **LLM -> Client:** Returns the JSON array.
6. **Client UI:** Parses the JSON and dynamically creates DOM elements for the flashcard deck.

## Data Schema (LLM Output)
```json
{
  "flashcards": [
    {
      "question": "What is the powerhouse of the cell?",
      "answer": "Mitochondria"
    }
  ]
}
```

## Scalability Considerations
- **Stateless Design:** By not requiring user sessions or a database for the MVP, the app can handle immense traffic. The only bottleneck is the LLM API rate limit.
- **Client-Side Rendering:** The server only passes JSON. All DOM rendering and animations happen on the client's GPU, minimizing server load.
