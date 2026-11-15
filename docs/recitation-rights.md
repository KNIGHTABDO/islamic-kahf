# Recitation rights (Content ID)

**What happened (Kahf ch1, 2026-11-15):** Salam Network claimed the video for Sheikh Yasser Ad-Dussary's recitation (everyayah.com files). It was a Copyright – Audio claim that matched every verse block. The video stayed up and only monetisation was affected. everyayah.com is a free download site, not a licence, and famous reciters' audio is in Content ID. Expect a claim every time one of those recordings is used.

## Hard rules (do not change)
- The Qur'an is always real human recitation. Never use AI or TTS recitation, never voice-clone a qari, and never put music under the ayat.
- Never mute, cut or speed-change the ayat to dodge a match.
- Never dispute a claim without a written licence or whitelist. A false dispute can turn into a copyright strike.
- Credit the reciter in the end credits (القرآن الكريم section) and in the description.

## Before choosing a reciter (step 4)
Ask the user which way to go, in this order:
1. **Licensed or whitelisted reciter.** If a rights holder has given the channel a written licence or whitelist, use that reciter. Licences go in the project's `docs/licences/` and are listed in `episodes.md`.
2. **Commissioned recitation.** The user pays a real qari for the verses, with a written work-for-hire licence or a monetised-YouTube licence. Put the files in `sources/quran/licensed/<name>/SSSAAA.mp3` (gitignored, never deleted by cleanup.sh) and set `"reciter": "local:<name>"` in `voice.json`. `fetch_ayah.py` then copies them instead of downloading.
3. **everyayah reciter with no licence** (the Kahf ch1 setup). Allowed, but tell the user up front that Content ID will most likely claim the audio and take the earnings on that video.

Do not trust "copyright-free Quran" sites unless they show who owns the recording and give a written licence. sites.google.com/view/copyrightfreequran is one example: it is unmaintained, ownership is not stated, and it points to YouTube rips.

## Upload (after step 11)
1. Upload the 4K as **Unlisted** (or Private) first.
2. Wait for YouTube Studio → **Checks** (copyright) to finish, about 5–15 min.
3. If a claim shows up, tell the user what it is: claimant, segments, and effect (block, monetisation, or tracking only). Then the user decides whether to publish. With a licence, the user can dispute with the licence attached. Without one, publish as is or wait for the rights holder.
4. Only then switch to Public.

## Asking a rights holder
Template: `islamic-kahf/docs/salam-network-email.md`, in Arabic and English. It covers whitelist, licence and release, and lists the matched segments. Find the contact on the claimant's YouTube channel (About → View email address; the user solves the CAPTCHA). The user sends the email. Claude only drafts it.
