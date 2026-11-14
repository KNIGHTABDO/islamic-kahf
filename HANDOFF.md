# HANDOFF: Ashab al-Kahf, chapter 1 (first full episode)

**Start here:** load the `islamic-story-episode` skill (`~/.claude/skills/islamic-story-episode/SKILL.md`), read
`reference/content-policy.md`, then follow the pipeline table one stage at a time. All commands run from this folder.

## Goal
One full chapter of أصحاب الكهف for **Sandouq Lhkayat** (@SandouqLhkayat, existing channel), **10-12 minutes**.
At the measured pace (~85 wpm including pauses) that is **~850-1000 words** of narration plus the verse blocks.
Suggested scope for chapter 1 (adjust after research): the city and its king, the youths' faith, the decision to leave,
the dog, entering the cave, the sleep. Verses roughly 18:9-18. Later chapters: the awakening and the coin (18:19-20),
the sign and the lesson (18:21-26). Keep a cliffhanger at the end of chapter 1.

## Decisions already made (don't re-ask)
- Narration: pure Fuṣḥā, fully diacritized, **one voice: Cruz** (`voice.json`, recipe in skill `reference/voice.md`).
  The user rates every take themselves (no AI judge). Send all takes.
- Script: **Gemini Argon High** writes it from sources **Claude** researches and saves in `sources/ch01.md`
  (prompts: skill `reference/script-prompts.md`). Argon also fact-checks. **The user reads the script before TTS.**
- Qur'an: never in the narration; use `@ayah S:A-B`. Reciter **Yasser Ad-Dussary**, `voice.json` "reciter" =
  `Yasser_Ad-Dussary_128kbps` (everyayah.com). Tested 2026-11-14: `fetch_ayah.py` got 18:9 and 18:10. The user asked for
  Omar bn Diaa al-Din, but he has no per-ayah files and no Kahf recording. Samples of three options for 18:10 are in
  `work/reciter-samples/`; switch only if the user asks. Credit the reciter in the YouTube description.
- Visuals: cel-shaded anime keyframes (Codex gpt-image), depth parallax, 2-4 Flow clips (check credits, `max_credits`),
  gold-on-navy branding. No prophet shown, women veiled (skill `reference/visuals.md`).
- Render: GitHub Actions, **public** repo, 40 shards. Never on the laptop.

## Not done yet
- **GitHub repo:** none yet. Create it public (`gh repo create KNIGHTABDO/islamic-kahf --public --source . --push`)
  before the first render. The local git identity is already set (same as render-repo).
- Everything from stage 1 (research) onwards.

## Watch on this episode (not proven yet, see SKILL.md table)
- Chunked TTS: the joined chunks must sound like one voice. The user approves the joined narration.
- Subtitle alignment over ~11 minutes: check the `<-- check` rows from assemble.py and spot-check the end.
- Lyria music in the real pipeline. `kapi doctor` showed the music route failing once (CDP timeout). Try `lyria-3.5`,
  then `lyria-3-pro-preview`.
- Render: ~20k frames, so about 4 min per shard plus ~3 min join (from the smoke runs). The full-quality file will be
  ~1 GB at crf14. Consider a higher crf for the upload copy. Record real numbers in skill `reference/render.md`.
- Recitation levels against the narration over long verse blocks.

## Constraints (the user's standing rules)
- Never print the kapi token; never sign in for the user; no billed Gemini API calls (everything through kapi).
- Flow: check credits, set `max_credits`, never retry `blocked`.
- Send every review file with SendUserFile using absolute paths (the user is often on their phone).
- Save tokens: text over screenshots, trim command output.
- Commits end with the Co-Authored-By line from the session reminder.

## References
- Skill smoke project (kept, public repo KNIGHTABDO/sandouq-kahf-smoke): `~/Desktop/projects/sandouq-kahf-smoke`
  (ch01/ch02 rendered, working examples of script, plan and render).
- Approved 66 s Kahf preview: `~/Desktop/projects/bta3-like/preview`, and skill `examples/ch01.script.txt` / `ch01.plan.json`.
- Memory: kahf-episode-1-decisions, narrator-voice-cruz-recipe, narration-pure-fusha-one-voice, channel-sandouq-lhkayat.
