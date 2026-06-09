# Specification

**Project Name:** QuickCards (V3 - UI Mastered)
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study tools from educational YouTube videos. By taking a YouTube URL as input, the system extracts the transcript and uses an LLM to generate an interactive multiple-choice quiz and flashcard deck, complete with contextual deep-links back to a sticky Picture-in-Picture (PiP) video player.

## 2. Problem Statement
Students spend too much time manually creating notes. Standard flashcard apps are passive, disconnected from the source material, and visually uninspiring.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary). 
- **Platform Scope:** Web Browser (Mobile-responsive).

## 4. Functional Requirements
1. The system must accept a valid YouTube URL. A "Paste Demo URL" button must be provided for 1-click judge testing. The "Generate" button remains disabled until a valid URL is detected.
2. The system must extract the English transcript. Crash with 400 error if < 100 words.
3. The system must generate a dynamic "Interactive Quiz Deck" (3 cards for < 5 mins, 5 cards per 10 mins).
4. **Quiz Mode:** Each card must include the Question, the Correct Answer, 3 Distractors, and a 1-sentence explanation.
5. **Contextual Timestamps:** The back of every card must sync with an embedded YouTube player, jumping the video to the exact moment the concept is discussed.
6. **Export to Anki:** Provide a 1-click button to download the deck as a `.txt` file.
7. **Accessibility:** UI adheres to WCAG 2.1 AA standards (keyboard navigability, Iconography for colorblindness).
8. **Rate Limiting:** Maximum 5 generations per IP per hour.

## 5. UI & Design Strategy (New)
- **Aesthetic:** Premium Dark Mode Glassmorphism with deep ambient gradients.
- **Layout:** 4-State Flow (Landing, Loading, Quiz, Summary). Single-card focused view.
- **Video Embed:** Embedded as a collapsible/sticky Picture-in-Picture iframe using `youtube-nocookie.com` to prevent tracking.

## 6. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts. Gemini APIs.
- **PII Scrubbing:** `presidio-analyzer` sanitization.
- **Format Constraints:** Standard UTF-8 text.

## 7. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** End-to-end latency < 15.0 seconds. 
- **Software Metrics:** Initial page load time < 1.5 seconds.
- **A11y Metrics:** 100% Lighthouse Score.
