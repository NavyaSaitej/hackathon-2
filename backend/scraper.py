"""
QuickCards — Transcript Scraper & Chunker (V5)

Responsibilities:
1. Validate YouTube URLs via strict regex.
2. Extract the video ID.
3. Fetch the English transcript via youtube-transcript-api.
4. Chunk the transcript with [TS_ID] annotations so the LLM
   maps answers to real timestamps instead of hallucinating them.
"""

import re
import gc
from youtube_transcript_api import YouTubeTranscriptApi
from loguru import logger


# Strict YouTube URL regex — accepts standard and shortened formats
YT_REGEX = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})(?:&.*)?$"
)

# Maximum video duration in seconds (20 minutes)
MAX_DURATION_SECONDS = 20 * 60


def extract_video_id(url: str) -> str | None:
    """Extract the 11-character video ID from a YouTube URL.

    Returns None if the URL doesn't match.
    """
    match = YT_REGEX.match(url.strip())
    return match.group(1) if match else None


def fetch_transcript(video_id: str) -> list[dict]:
    """Fetch the English transcript for a given video ID.

    Returns the raw list of transcript segments from youtube-transcript-api.
    Raises ValueError if the transcript is too short or unavailable.
    """
    logger.info(f"Fetching transcript for video: {video_id}")

    ytt_api = YouTubeTranscriptApi()
    transcript_segments = ytt_api.fetch(video_id, languages=["en"])

    # Validate minimum content length
    full_text = " ".join(seg.text for seg in transcript_segments)
    word_count = len(full_text.split())

    if word_count < 100:
        raise ValueError(
            f"Transcript too short ({word_count} words). Minimum 100 words required."
        )

    # Enforce maximum duration
    if transcript_segments:
        last_seg = transcript_segments[-1]
        total_duration = last_seg.start + last_seg.duration
        if total_duration > MAX_DURATION_SECONDS:
            raise ValueError(
                f"Video too long ({total_duration:.0f}s). Maximum {MAX_DURATION_SECONDS}s."
            )

    logger.info(f"Transcript fetched: {word_count} words, {len(transcript_segments)} segments")
    return transcript_segments


def chunk_transcript(segments: list[dict], chunk_size: int = 5) -> str:
    """Chunk transcript segments and annotate with timestamp IDs.

    Groups segments into chunks of `chunk_size` and prepends each chunk
    with a [TS:seconds] marker. This gives the LLM real timestamps to
    reference instead of hallucinating them.

    Returns a single annotated text block.
    """
    chunks = []
    for i in range(0, len(segments), chunk_size):
        group = segments[i : i + chunk_size]
        timestamp_sec = int(group[0].start)
        text = " ".join(seg.text for seg in group)
        chunks.append(f"[TS:{timestamp_sec}] {text}")

    annotated = "\n\n".join(chunks)
    logger.info(f"Chunked into {len(chunks)} annotated blocks")
    return annotated


def process_video(url: str) -> tuple[str, str]:
    """Full pipeline: URL → validated video ID → chunked transcript.

    Returns (video_id, annotated_transcript).
    Explicitly garbage-collects raw segments after chunking (Zero Retention).
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {url}")

    segments = fetch_transcript(video_id)
    annotated = chunk_transcript(segments)

    # Zero Retention: explicitly free raw transcript data
    del segments
    gc.collect()

    return video_id, annotated
