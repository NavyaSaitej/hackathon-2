# Specification

**Project Name:** QuickCards (V2)
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study tools from educational YouTube videos. By taking a YouTube URL as input, the system extracts the transcript and uses an LLM to generate an interactive multiple-choice quiz and flashcard deck, complete with contextual deep-links back to the source video.

## 2. Problem Statement
Students spend too much time manually creating notes. Furthermore, standard flashcard apps are passive and disconnected from the source material; when a student forgets a concept, they don't know where in the 40-minute lecture it was discussed.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary). System must support both manual and auto-generated YouTube captions.
- **Platform Scope:** Web Browser (Mobile-responsive).

## 4. Functional Requirements
1. The system must accept a valid YouTube URL and validate its format using strict regex.
2. The system must extract the English transcript. It prioritizes manual captions, falling back to auto-generated. Crash with 400 error if < 100 words.
3. The system must generate a dynamic "Interactive Quiz Deck" (3 cards for videos < 5 mins, 5 cards per 10 mins).
4. **[V2] Quiz Mode:** Each card must include the Question, the Correct Answer, 3 Plausible Distractors, and a 1-sentence explanation of why the answer is correct.
5. **[V2] Contextual Timestamps:** The back of every card must contain a link that opens the exact moment in the YouTube video where the concept is discussed (must open in a new tab or iframe to preserve app state).
6. **Export to Anki:** Provide a 1-click button to download the deck as a `.txt` file for Anki import.
7. **Accessibility:** UI adheres to WCAG 2.1 AA standards.
8. **Rate Limiting:** Maximum 5 generations per IP per hour.

## 5. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts via `youtube-transcript-api`. LLM generation via Gemini APIs.
- **PII Scrubbing:** `presidio-analyzer` (or regex fallback) sanitization before LLM ingestion.
- **Scale:** Maximum video length enforced at 20 minutes (approx. 3,000 words).
- **Format Constraints:** Standard UTF-8 text.

## 6. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** End-to-end latency < 15.0 seconds. 
- **Software Metrics:** Initial page load time < 1.5 seconds.
- **A11y Metrics:** 100% Lighthouse Accessibility Score.
