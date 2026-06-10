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
import json
import urllib.request
from dataclasses import dataclass

import yt_dlp
from loguru import logger


# Strict YouTube URL regex — accepts standard and shortened formats
YT_REGEX = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})(?:[?&].*)?$"
)

# Maximum video duration in seconds (2 hours)
MAX_DURATION_SECONDS = 2 * 60 * 60


def extract_video_id(url: str) -> str | None:
    """Extract the 11-character video ID from a YouTube URL.

    Returns None if the URL doesn't match.
    """
    match = YT_REGEX.match(url.strip())
    return match.group(1) if match else None


@dataclass
class Segment:
    text: str
    start: float
    duration: float


def fetch_transcript(video_id: str) -> list[Segment]:
    """Fetch the transcript for a given video ID using yt-dlp.

    Prefers English, but falls back to any available language.
    Returns the raw list of transcript segments.
    Raises ValueError if the transcript is too short or unavailable.
    """
    import os
    logger.info(f"Fetching transcript for video: {video_id}")
    
    # HARDCODED BYPASS FOR DEMO VIDEO to avoid Vercel 429 IP bans
    if video_id == "Dq6dBoFor00":
        try:
            try:
                from backend.demo_data import DEMO_SEGMENTS
            except ImportError:
                from demo_data import DEMO_SEGMENTS
            logger.info("Used hardcoded demo transcript bypass.")
            return [Segment(**s) for s in DEMO_SEGMENTS]
        except Exception as e:
            logger.error(f"Failed to load demo segments: {e}")

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-IN', 'hi', '.*'],
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'client': ['android', 'ios']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        subs = info.get('subtitles') or {}
        auto_subs = info.get('automatic_captions') or {}
        
        # Combine available languages
        available_langs = list(subs.keys()) + list(auto_subs.keys())
        if not available_langs:
            raise ValueError("No subtitles available")
            
        # Try to find English first, else pick first available
        target_lang = next((lang for lang in ['en', 'en-US', 'en-GB', 'en-IN'] if lang in available_langs), None)
        if not target_lang:
            target_lang = available_langs[0]
            
        # Get the sub tracks
        tracks = subs.get(target_lang) or auto_subs.get(target_lang)
        json3_url = next((t['url'] for t in tracks if t['ext'] == 'json3'), None)
        
        if not json3_url:
            raise ValueError("No JSON3 subtitle format found")
            
        resp = ydl.urlopen(json3_url)
        data = json.loads(resp.read().decode('utf-8'))
        
        transcript_segments = []
        for event in data.get('events', []):
            if 'segs' not in event:
                continue
            text = "".join(s.get('utf8', '') for s in event['segs']).strip()
            if not text or text == '\n':
                continue
            start = event.get('tStartMs', 0) / 1000.0
            duration = event.get('dDurationMs', 0) / 1000.0
            transcript_segments.append(Segment(text=text, start=start, duration=duration))
            
        if not transcript_segments:
            raise ValueError("Empty transcript")
            
    except Exception as e:
        logger.warning(f"yt-dlp failed: {e}. Falling back to youtube-transcript.ai...")
        try:
            req = urllib.request.Request(f'https://youtube-transcript.ai/transcript/{video_id}.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            with urllib.request.urlopen(req) as response:
                txt = response.read().decode('utf-8')

            transcript_segments = []
            for line in txt.split('\n'):
                line = line.strip()
                if line.startswith('['):
                    match = re.match(r'^\[([\d:]+)\]\s*(?:\[\]\s*)?(.*)', line)
                    if match:
                        time_str = match.group(1)
                        text = match.group(2).strip()
                        if not text: continue
                        
                        parts = time_str.split(':')
                        try:
                            if len(parts) == 3:
                                start = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
                            elif len(parts) == 2:
                                start = int(parts[0])*60 + float(parts[1])
                            else:
                                start = float(parts[0])
                        except ValueError:
                            continue
                            
                        transcript_segments.append(Segment(text=text, start=start, duration=5.0))
            
            if not transcript_segments:
                raise ValueError("Empty transcript from fallback")
                
            # Estimate durations
            for i in range(len(transcript_segments)-1):
                transcript_segments[i].duration = max(5.0, transcript_segments[i+1].start - transcript_segments[i].start)
                
        except Exception as fallback_e:
            raise ValueError(f"Could not retrieve a transcript for this video. yt-dlp error: {e}. Fallback error: {fallback_e}")


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
