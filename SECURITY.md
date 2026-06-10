# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue.
2. Email the maintainer directly with details of the vulnerability.
3. Include steps to reproduce, potential impact, and suggested fix if possible.

## Security Measures

- **API Key Protection:** The Gemini API key is stored in `.env` (never committed to git).
- **App-to-App Authentication:** The backend requires an `X-App-Secret` header to prevent direct API abuse.
- **Rate Limiting:** IP-based rate limiting (5 requests/hour) via `slowapi`.
- **CORS:** Strict origin allowlist prevents unauthorized cross-origin requests.
- **Privacy-Enhanced Embeds:** YouTube videos are embedded via `youtube-nocookie.com`.
- **Zero Data Retention:** All transcript and AI-generated data is garbage-collected after each request.

## Supported Versions

| Version | Supported |
|---|---|
| 1.x | ✅ |
