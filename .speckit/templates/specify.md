# Specification

**Project Name:** Video-to-Flashcards Auto-Study Buddy
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study flashcards from educational YouTube videos. By taking a YouTube URL as input, the system extracts the video transcript and uses a Large Language Model to identify key concepts, saving students hours of manual note-taking and improving learning retention.

## 2. Problem Statement
Students and self-learners spend an inordinate amount of time manually creating flashcards from video lectures. There is a need for a seamless, instantaneous tool that bridges the gap between passive video consumption and active recall studying, without requiring complex software installations or manual transcription.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary), with potential for multilingual transcript support.
- **Platform Scope:** Web Browser (Mobile-responsive).

## 4. Functional Requirements
1. The system must accept a valid YouTube URL as input.
2. The system must successfully extract the English transcript/captions for the provided video.
3. The system must process the transcript to generate exactly 5 to 10 distinct Question & Answer pairs.
4. The system must render these pairs as interactive, flippable digital cards in the browser.

## 5. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts via rapid API or lightweight proxy. LLM generation via OpenAI/Gemini APIs.
- **PII Risk Level:** Low. Educational videos typically do not contain PII.
- **Scale:** Small scale per request (max ~15-minute video transcripts, roughly 2,000-3,000 words).
- **Format Constraints:** Standard UTF-8 text.

## 6. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** Flashcard generation latency must be < 15 seconds.
- **Software Metrics:** Page load time < 1.5s.
- **Business/User Metrics:** Flawless generation of a 5-card deck from a standard 10-minute educational video.
