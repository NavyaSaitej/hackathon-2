# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-06-10

### Features
- Initial release of QuickCards
- AI-powered quiz generation from YouTube videos via Google Gemini
- Interactive multiple-choice quiz with 3 distractors per card
- Contextual timestamp deep links with embedded PiP YouTube player
- 1-click Anki export (.txt TSV format)
- Premium dark-mode Glassmorphic UI with 3D card flip animations
- Progressive Web App (PWA) with offline caching
- App-to-App X-App-Secret authentication
- IP rate limiting (5 requests/hour)
- 3-retry exponential backoff circuit breaker for Gemini API
- Dynamic ARIA state toggling for screen reader accessibility
- Colorblind-accessible feedback (icons + colors)

### Documentation
- README, USER_MANUAL, AGENTS, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY
- Swecha GitLab CI/CD pipeline
- Pre-commit hooks and code quality tooling (Biome, Prettier, Ruff)
