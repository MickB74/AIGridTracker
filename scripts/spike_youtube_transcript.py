"""Throwaway connectivity spike — NOT part of the app.

Question this answers: does youtube-transcript-api work from a GitHub
Actions runner, or does YouTube block the datacenter IP range for its
unofficial caption endpoint? That's the real blocker for a transcript
feature, since news-refresh.yml runs hourly from exactly that kind of IP.

Deliberately prints only pass/fail + exception type/class — never the
transcript text itself, since this script's job is to test connectivity,
not to display or store anyone's caption content.

Delete this file (and its workflow) once the question is answered.
"""
import sys

# A handful of well-known, definitely-captioned public videos, tried in
# sequence. Any single failure could be that video's captions being off;
# what we care about is the pattern across all of them.
TEST_VIDEO_IDS = [
    "dQw4w9WgXcQ",   # ubiquity-tested, always captioned
    "jNQXAC9IVRw",   # first YouTube video ever uploaded, has captions
    "9bZkp7q19f0",   # extremely high view count, definitely captioned
]


def main():
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as e:
        print(f"IMPORT FAILED: {e}")
        sys.exit(2)

    results = []
    for vid in TEST_VIDEO_IDS:
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(vid)
            segment_count = len(transcript.snippets) if hasattr(transcript, "snippets") else len(transcript)
            print(f"{vid}: OK — {segment_count} segments")
            results.append(True)
        except Exception as e:                                    # noqa: BLE001
            print(f"{vid}: FAILED — {type(e).__name__}: {e}")
            results.append(False)

    ok_count = sum(results)
    print(f"\n{ok_count}/{len(results)} succeeded")
    if ok_count == 0:
        print("VERDICT: blocked — every attempt failed, likely IP-level block")
        sys.exit(1)
    elif ok_count < len(results):
        print("VERDICT: partial — inconsistent, worth another run to check flakiness")
        sys.exit(0)
    else:
        print("VERDICT: works — runner IP is not blocked")
        sys.exit(0)


if __name__ == "__main__":
    main()
