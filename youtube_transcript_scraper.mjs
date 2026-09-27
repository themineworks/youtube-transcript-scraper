#!/usr/bin/env node
// Node.js client for the themineworks/youtube-transcript-scraper actor on Apify: runs it and saves results.json.
// Flags map 1:1 to the actor's input. Free API token: https://console.apify.com/sign-up
// Docs and pricing: https://themineworks.com/actors/youtube-transcript-scraper/
import { ApifyClient } from 'apify-client';
import { writeFileSync } from 'node:fs';

const ACTOR = 'themineworks/youtube-transcript-scraper';

function parseArgs(argv) {
    const out = {};
    for (let i = 0; i < argv.length; i++) {
        if (!argv[i].startsWith('--')) continue;
        const key = argv[i].slice(2);
        out[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
    return out;
}

const args = parseArgs(process.argv.slice(2));
const token = args.token || process.env.APIFY_TOKEN;
if (!token) {
    console.error('Provide --token or set APIFY_TOKEN. Free token: https://console.apify.com/sign-up');
    process.exit(1);
}

const runInput = {};
if (args['video-urls'] !== undefined) runInput.videoUrls = String(args['video-urls']).split(',').map((s) => s.trim());
if (args['output-formats'] !== undefined) runInput.outputFormats = String(args['output-formats']).split(',').map((s) => s.trim());
if (args['language'] !== undefined) runInput.language = String(args['language']);
if (args['include-timestamps'] !== undefined) runInput.includeTimestamps = args['include-timestamps'] === true || args['include-timestamps'] === 'true';

const client = new ApifyClient({ token });
console.log(`Running ${ACTOR} ...`);
const run = await client.actor(ACTOR).call(runInput);
const { items } = await client.dataset(run.defaultDatasetId).listItems();
writeFileSync('results.json', JSON.stringify(items, null, 2));
console.log(`Saved ${items.length} results to results.json`);
