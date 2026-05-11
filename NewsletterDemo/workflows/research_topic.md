# Workflow: Research Topic

## Objective
Search the web for a given topic and produce a structured JSON file of sources that can be used to generate newsletter content.

## Tool
`tools/research_topic.py`

## Inputs
| Input | Description | Default |
|---|---|---|
| `topic` | Search query string | required |
| `days` | How many days back to search | 7 |
| `results` | Number of results to return | 8 |

## Steps

1. **Check for duplicates first** (if prior research archives exist):
   ```
   python tools/check_duplicates.py --research <last_research_file>
   ```
   - If overlap > 60%: inform user, suggest a more specific angle. Do not run research without confirmation.
   - If no prior research: skip this step.

2. **Run research**:
   ```
   python tools/research_topic.py --topic "<topic>" --days <days> --results <results>
   ```

3. **Validate output**:
   - At least 3 sources returned → proceed
   - 1-2 sources → warn user, offer to broaden query or increase `--days`
   - 0 sources → check API key, try a simpler query

4. **Inspect source quality** (skim the JSON):
   - Prefer sources with `score > 0.5`
   - If all sources are from the same domain, the query may be too narrow

## Output
`.tmp/research_{timestamp}.json` containing:
```json
{
  "topic": "...",
  "searched_at": "ISO timestamp",
  "days_back": 7,
  "answer_summary": "Tavily's auto-summary of the topic",
  "sources": [
    {"title": "...", "url": "...", "content": "...", "score": 0.85},
    ...
  ]
}
```

## Notes
- Tavily free tier: 1,000 searches/month. Each call to this tool counts as one search.
- The `answer_summary` field is useful for the newsletter intro — Claude often uses it as a starting point.
- If the topic is broad (e.g. "technology"), narrow it (e.g. "AI chip shortages 2026") for better results.
