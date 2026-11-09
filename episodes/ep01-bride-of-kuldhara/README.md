# Episode 1 — The Bride of Kuldhara

Build scripts for the first Lantern Man episode. Generated media lives in `projects/ep01/` (git-ignored).

| Script | What it does |
| --- | --- |
| `ep1_images.py` | Generates the episode's stills with Gemini 3.1 Flash Lite Image; hero shots use the character references in `assets/characters/lantern-man/`. Pass keys to regenerate specific shots. |
| `build_pilot.py` | Builds the cold open + intro (also used as the episode's first segment). |
| `build_ep01.py` | Builds Parts 1–6: paces the narration, cuts shots on spoken anchor words, adds sound effects and music cues, burns karaoke captions. `AUDIO_ONLY=1` remixes sound without re-rendering video. |

Narration: ElevenLabs, voice "Jack – Deep Dark Horror Narrator", model eleven_v4, one take per part.
Word timings: faster-whisper `small.en`; check names in the transcripts (it hears "Kamla" as "Kamala").

Final join: concat the pilot + parts, loudnorm to -14 LUFS, encode yuv420p (the subtitles step outputs 4:4:4, which many players can't decode).

Known cost (Nov 2026): ~11,800 ElevenLabs credits (~₹205), ~64 images (~₹190). Render time on 2 CPU cores ≈ 5 min per minute of video; delete `build/part*/shot*.mp4` afterwards (they take ~20 GB).
