#!/usr/bin/env python3
"""Timestamped captions to JSON. No API key, no login. Python, Node.js and cURL clients for the YouTube Transcript Downloader on Apify, pay per result.

Command-line client for the themineworks/youtube-transcript-scraper actor on Apify: runs it, waits for it
to finish and saves every result as JSON and CSV. Flags map 1:1 to the actor's input.
Free Apify account and API token: https://console.apify.com/sign-up
Docs and pricing: https://themineworks.com/actors/youtube-transcript-scraper/
"""
import argparse, csv, json, os, sys
from apify_client import ApifyClient

ACTOR = "themineworks/youtube-transcript-scraper"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--token", default=os.environ.get("APIFY_TOKEN"), help="Apify API token (or set APIFY_TOKEN)")
    ap.add_argument("--out", default="results", help="Output basename, writes .json and .csv")
    ap.add_argument("--video-urls", help="Comma-separated. One or more YouTube videos, one per line")
    ap.add_argument("--output-formats", help="Comma-separated. Which transcript formats to return on each row")
    ap.add_argument("--language", help="Language code of the caption track to prefer, for example en, es, hi, fr or pt")
    ap.add_argument("--include-timestamps", action=argparse.BooleanOptionalAction, help="When on, rows include the segments array (start time and duration of each line, in…")
    a = ap.parse_args()
    if not a.token:
        sys.exit("Provide --token or set APIFY_TOKEN. Free token: https://console.apify.com/sign-up")

    run_input = {}
    if a.video_urls: run_input["videoUrls"] = [s.strip() for s in a.video_urls.split(",") if s.strip()]
    if a.output_formats: run_input["outputFormats"] = [s.strip() for s in a.output_formats.split(",") if s.strip()]
    if a.language is not None: run_input["language"] = a.language
    if a.include_timestamps is not None: run_input["includeTimestamps"] = a.include_timestamps

    client = ApifyClient(a.token)
    print(f"Running {ACTOR} ...")
    run = client.actor(ACTOR).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    with open(a.out + ".json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    keys = []
    for it in items:
        keys += [k for k in it if k not in keys]
    if items:
        with open(a.out + ".csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for it in items:
                w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in it.items()})
    print(f"Done: {len(items)} results saved to {a.out}.json and {a.out}.csv")


if __name__ == "__main__":
    main()
