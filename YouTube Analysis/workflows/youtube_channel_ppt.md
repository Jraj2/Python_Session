# YouTube Channel PPT — Workflow

## Objective
Build a polished, corporate-professional PowerPoint deck for a **single YouTube channel** (any channel, any niche). The deck is a reusable template focused on three core visuals: views over time, channel growth (area chart), and top videos ranking. Designed for board reviews, sponsor pitches, or quarterly content performance reports.

This workflow is **complementary** to `youtube_niche_analysis.md` — that one analyzes 50+ channels in a niche; this one drills into ONE channel.

---

## Required Inputs
- `YOUTUBE_API_KEY` — YouTube Data API v3 key (already in `.env`)
- **Channel identifier**, one of:
  - Channel ID (starts with `UC...`, e.g. `UCBJycsmduvYEL83R_U4JriQ`)
  - Handle (e.g. `@mkbhd`)
  - Custom URL slug (e.g. `mkbhd`)
- *Optional:* `subscriber_history.csv` — two-column CSV (`date,subscribers`) for accurate growth chart. If absent, the tool falls back to cumulative-views proxy.

---

## One-time setup

```bash
pip install google-api-python-client python-pptx matplotlib python-dotenv pandas
```

The `.env` should already contain:
```
YOUTUBE_API_KEY=<your key>
```

---

## Steps

### Step 1 — Fetch channel data
```bash
python tools/fetch_channel_data.py --channel "@mkbhd"
# or by ID:
python tools/fetch_channel_data.py --channel UCBJycsmduvYEL83R_U4JriQ
```
Resolves the handle/slug to a channel ID, then pulls:
- Channel snapshot (title, description, current subscriber count, total views, video count, thumbnail)
- Up to 50 most recent uploads with view/like/comment counts and publish dates

**Output:** `.tmp/channel_<ID>.json`
**Quota cost:** ~5 units per channel

---

### Step 2 — Generate the PPT
```bash
python tools/create_channel_ppt.py --channel "@mkbhd"
# optional growth file:
python tools/create_channel_ppt.py --channel "@mkbhd" --history subscriber_history.csv
```
Builds an 8-slide corporate-professional deck:

| # | Slide | Visual |
|---|-------|--------|
| 1 | Cover | Channel name, handle, run date |
| 2 | Channel Snapshot | Stat cards: subs, views, videos, avg engagement |
| 3 | Views Over Time | **Line chart** — monthly view aggregate |
| 4 | Channel Growth | **Area chart** — subscriber growth (or cumulative views proxy) |
| 5 | Top Videos Ranking | **Horizontal bar chart** — top 10 by views |
| 6 | Engagement Insights | Best-performing video + per-video engagement rate stat |
| 7 | Key Takeaways | 3 data-driven observations |
| 8 | Closing | Thank-you + data source credit |

**Output:** `.tmp/channel_<ID>_<YYYY-MM-DD>.pptx`
**Quota cost:** None — fully local once Step 1 has run.

---

## Expected outputs

| File | Description |
|------|-------------|
| `.tmp/channel_<ID>.json` | Channel snapshot + recent video records |
| `.tmp/channel_<ID>_<DATE>.pptx` | Final 8-slide corporate-professional deck |

---

## Edge cases & notes

**Handle resolution:** The YouTube API requires a channel ID, not a handle. The tool calls `channels.list(forHandle=...)` to resolve `@username` → `UC...`. If a handle has been recently changed it may take 24h to propagate.

**Subscriber history accuracy:** YouTube Data API v3 returns *current* subscriber count only. True historical subs require YouTube Analytics API (OAuth, channel-owner only). For non-owner reports, the area chart shows cumulative channel views as a proxy with an honest axis label. Supply your own `subscriber_history.csv` for accurate growth.

**Hidden subscriber counts:** Some channels hide their subscriber count → API returns 0. In that case the snapshot card shows "Hidden" instead of "0".

**Shorts mixed in:** The 50 recent uploads include YouTube Shorts. Shorts often skew average view counts upward; the deck flags this in the Engagement Insights slide if Shorts make up >30% of the sample.

**Quota:** A full run costs ~5 units of the 10k daily limit — effectively free.

**Run cadence:** Weekly or monthly is sensible. Daily produces noisy charts since recent videos haven't had time to accumulate views.

**Re-running for a different channel:** Just pass a new `--channel` argument; outputs are namespaced by channel ID, so they won't collide.
