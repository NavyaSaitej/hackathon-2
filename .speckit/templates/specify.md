# Specification

**Project Name:** QuickCards (V4 - Enterprise Compliance)
**Date:** 2026-06-09

## 1. Executive Summary
A web-based application designed to automatically generate interactive study tools from educational YouTube videos. It features an interactive multiple-choice quiz, flashcard deck, and contextual deep-links to a sticky Picture-in-Picture (PiP) video player.

## 2. Problem Statement
Students spend too much time manually creating notes. Standard flashcard apps are passive, disconnected from the source material, and visually uninspiring.

## 3. Scope & Audience
- **Primary Users:** High school/college students and self-directed learners.
- **Language Scope:** English (Primary). 
- **Platform Scope:** Web Browser, Mobile-responsive, and Installable PWA.

## 4. Functional Requirements
1. The system must accept a valid YouTube URL. A "Paste Demo URL" button must be provided. The "Generate" button remains disabled until valid.
2. The system must extract the English transcript. Crash with 400 error if < 100 words.
3. The system must generate a dynamic "Interactive Quiz Deck".
4. **Quiz Mode:** Each card must include Question, Correct Answer, 3 Distractors, and a 1-sentence explanation.
5. **Contextual Timestamps:** Cards sync with an embedded `youtube-nocookie.com` PiP player.
6. **Export to Anki:** 1-click download to `.txt`.
7. **Progressive Web App (PWA):** Must include a Service Worker (`sw.js`) and manifest for offline caching and home-screen installation.
8. **Accessibility:** UI adheres to WCAG 2.1 AA standards.
9. **Rate Limiting:** Maximum 5 generations per IP per hour.

## 5. UI & Design Strategy
- **Aesthetic:** Premium Dark Mode Glassmorphism.
- **Layout:** 4-State Flow (Landing, Loading, Quiz, Summary).

## 6. Data Governance & Privacy (Mandatory)
- **Data Sources:** Public YouTube transcripts. Gemini APIs.
- **PII Scrubbing:** `presidio-analyzer` sanitization.
- **Strict Gitignore:** `.env` keys must never be committed.

## 7. Success Metrics & Benchmarks
- **AI/LLM Benchmarks:** End-to-end latency < 15.0 seconds. 
- **Software Metrics:** Initial page load time < 1.5 seconds.
- **Compliance Metrics:** 100% Swecha Code Quality Compliance (CI/CD, Linters, Docs).
