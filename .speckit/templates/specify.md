# Specification

**Project Name:** QuickCards
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study flashcards from educational YouTube videos. By taking a YouTube URL as input, the system extracts the video transcript and uses a Large Language Model to identify key concepts, saving students hours of manual note-taking and improving learning retention.

## 2. Problem Statement
Students and self-learners spend an inordinate amount of time manually creating flashcards from video lectures. There is a need for a seamless, instantaneous tool that bridges the gap between passive video consumption and active recall studying, without requiring complex software installations or manual transcription.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary). System must support both manual and auto-generated YouTube captions. Multilingual support via strict transliteration.
- **Platform Scope:** Web Browser (Mobile-responsive).

## 4. Functional Requirements
1. The system must accept a valid YouTube URL and validate its format using strict regex (supporting `youtu.be` and `youtube.com/watch` formats).
2. The system must extract the English transcript. It must prioritize manual captions, falling back to auto-generated. If neither exists, OR if the transcript contains fewer than 100 words (e.g., a music video), it must explicitly crash with a logged 400 error.
3. The system must process the transcript to generate dynamic flashcards: 3 cards for videos under 5 mins, and 5 cards per 10 minutes for longer videos.
4. The system must render these pairs as interactive, flippable digital cards in the browser, with specific error UI states for invalid videos.
5. **[New] Export to Anki:** The system must provide a 1-click button to download the flashcard deck as a `.txt` file formatted specifically for Anki import (tab-separated values).
6. **Accessibility:** The UI must adhere to WCAG 2.1 AA standards (keyboard navigability).
7. **[Security] Rate Limiting:** The API must limit users to 5 generations per IP per hour to prevent API credit abuse during the hackathon.

## 5. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts via `youtube-transcript-api`. LLM generation via Gemini APIs.
- **PII Risk Level:** Low/Medium. All raw transcripts must pass through an explicit `presidio-analyzer` (or strict regex fallback) PII scrubbing pipeline removing emails/phone numbers *before* LLM ingestion.
- **Scale:** Maximum video length enforced at 20 minutes (approx. 3,000 words).
- **Format Constraints:** Standard UTF-8 text. Mixed scripts must use strict transliteration libraries.

## 6. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** Flashcard generation end-to-end latency < 15.0 seconds. Token processing speed > 100 tokens/sec.
- **Software Metrics:** Initial page load time < 1.5 seconds.
- **A11y Metrics:** 100% Lighthouse Accessibility Score.
- **Business/User Metrics:** Generates exactly a 5-card deck from a standard 10-minute video with 0 data extraction failures on captioned videos.
