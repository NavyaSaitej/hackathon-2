# Specification

**Project Name:** Video-to-Flashcards Auto-Study Buddy
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study flashcards from educational YouTube videos. By taking a YouTube URL as input, the system extracts the video transcript and uses a Large Language Model to identify key concepts, saving students hours of manual note-taking and improving learning retention.

## 2. Problem Statement
Students and self-learners spend an inordinate amount of time manually creating flashcards from video lectures. There is a need for a seamless, instantaneous tool that bridges the gap between passive video consumption and active recall studying, without requiring complex software installations or manual transcription.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary), Multilingual support via strict transliteration.
- **Platform Scope:** Web Browser (Mobile-responsive).

## 4. Functional Requirements
1. The system must accept a valid YouTube URL and validate its format using regex.
2. The system must extract the English transcript/captions for the provided video. If captions are unavailable, it must explicitly crash with a logged error.
3. The system must process the transcript to generate exactly 5 Question & Answer pairs per 10 minutes of video.
4. The system must render these pairs as interactive, flippable digital cards in the browser.

## 5. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts via `youtube-transcript-api`. LLM generation via Gemini APIs.
- **PII Risk Level:** Low/Medium. While educational videos rarely contain PII, all raw transcripts must pass through an explicit regex-based PII scrubbing pipeline (removing emails/phone numbers) before LLM ingestion.
- **Scale:** Maximum video length enforced at 20 minutes (approx. 3,000 words).
- **Format Constraints:** Standard UTF-8 text. Mixed scripts must use strict transliteration libraries.

## 6. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** Flashcard generation end-to-end latency < 15.0 seconds. Token processing speed > 100 tokens/sec.
- **Software Metrics:** Initial page load time < 1.5 seconds.
- **Business/User Metrics:** Generates exactly a 5-card deck from a standard 10-minute video with 0 data extraction failures on captioned videos.
