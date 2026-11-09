"""Build the Lantern Man pilot: stretched narration, Ken Burns stills, karaoke captions, music + SFX."""
import json, subprocess, os, sys

P = "/home/claude/OpenMontage/projects/pilot"
ST = f"{P}/stills"
MUS = "/home/claude/OpenMontage/assets/music/lantern-man"
OUT = f"{P}/build"
os.makedirs(OUT, exist_ok=True)
FPS = 30

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); sys.exit(1)
    return r.stdout

words = json.load(open(f"{P}/words.json"))
for w in words:
    w["w"] = w["w"].replace("Koldhara", "Kuldhara")

# Extra pause (seconds) added after the word ending each sentence/beat.
extra = {"Kuldhara.": 0.9, "anklets,": 0.3, "footprints,": 0.5, "well,": 0.9, "stop.": 1.8,
         "months.": 2.4, "drowned.": 0.8, "dead.": 1.1, "them.": 1.2, "speak.": 0.7,
         "show.": 1.2, "watch,": 0.4}

# 1) split narration at cut points (midpoint of gap after each beat word) and insert silence
cuts, pads = [], []
for i, w in enumerate(words[:-1]):
    if w["w"] in extra:
        cuts.append(round((w["e"] + words[i + 1]["s"]) / 2, 3)); pads.append(extra[w["w"]])
bounds = [0.0] + cuts + [None]
parts = []
for k in range(len(bounds) - 1):
    a, b = bounds[k], bounds[k + 1]
    f = f"{OUT}/n{k:02d}.wav"
    trim = f"-ss {a}" + (f" -to {b}" if b else "")
    run(f"ffmpeg -v error -y {trim} -i {P}/narration_take1.mp3 -ar 48000 -ac 2 {f}")
    parts.append(f)
    if k < len(pads):
        s = f"{OUT}/s{k:02d}.wav"
        run(f"ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=stereo -t {pads[k]} {s}")
        parts.append(s)
open(f"{OUT}/concat.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
LEAD = 1.5  # seconds of bells/wind before the first word
run(f"ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=stereo -t {LEAD} {OUT}/lead.wav")
run(f"ffmpeg -v error -y -f concat -safe 0 -i {OUT}/concat.txt -c pcm_s16le {OUT}/narr_body.wav")
run(f"ffmpeg -v error -y -i {OUT}/lead.wav -i {OUT}/narr_body.wav -filter_complex concat=n=2:v=0:a=1 {OUT}/narration.wav")

# shift word times
shift = LEAD
ci = 0
for w in words:
    while ci < len(cuts) and w["s"] > cuts[ci]:
        shift += pads[ci]; ci += 1
    w["s2"], w["e2"] = round(w["s"] + shift, 2), round(w["e"] + shift, 2)
narr_end = float(run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {OUT}/narration.wav"))

def t_of(word, which="s2", nth=1):
    n = 0
    for w in words:
        if w["w"].startswith(word):
            n += 1
            if n == nth: return w[which]
    raise KeyError(word)

# 2) shots: (image, start, flip)
TITLE_LEN = 5.0
shots = [
    ("01_footprints", 0.0, False),
    ("04_ghost_street", t_of("You") - 0.3, False),
    ("03_well", t_of("and") - 0.3, False),
    ("02_ruins_wide", t_of("Every") - 0.4, False),
    ("07_hero_walk", t_of("When") - 0.8, False),
    ("06_hero_closeup", t_of("Since") - 0.4, True),
    ("05_hero_ruins", t_of("The") - 0.4, False),
    ("08_title_bg", narr_end + 0.3, False),
]
total = narr_end + 0.3 + TITLE_LEN
XF = 1.0
durs = []
for i, (img, st, fl) in enumerate(shots):
    end = shots[i + 1][1] if i + 1 < len(shots) else total
    durs.append(end - st)

# 3) render each shot as a slow push-in (alternating direction), graded with vignette + grain
for i, ((img, st, fl), d) in enumerate(zip(shots, durs)):
    clip_d = d + (XF if i < len(shots) - 1 else 0)
    n = int(round(clip_d * FPS))
    z_from, z_to = (1.0, 1.09) if i % 2 == 0 else (1.09, 1.0)
    z = f"{z_from}+({z_to}-{z_from})*on/{n}"
    flip = "hflip," if fl else ""
    vf = (f"{flip}scale=3840:-2:flags=lanczos,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1920x1080:fps={FPS},"
          f"eq=contrast=1.04:saturation=0.92,vignette=PI/4.5,noise=alls=6:allf=t,format=yuv420p")
    run(f"ffmpeg -v error -y -loop 1 -i {ST}/{img}.png -vf \"{vf}\" -frames:v {n} -c:v libx264 -preset veryfast -crf 16 {OUT}/shot{i}.mp4")

# 4) chain crossfades
inputs = " ".join(f"-i {OUT}/shot{i}.mp4" for i in range(len(shots)))
fc, prev, off = [], "[0:v]", 0.0
for i in range(1, len(shots)):
    off += durs[i - 1]
    lab = f"[v{i}]"
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off - XF + XF:.3f}{lab}".replace(f"offset={off - XF + XF:.3f}", f"offset={off:.3f}"))
    prev = lab
run(f"ffmpeg -v error -y {inputs} -filter_complex \"{';'.join(fc)}\" -map \"{prev}\" -c:v libx264 -preset veryfast -crf 18 {OUT}/video_raw.mp4")

# 5) captions (ASS karaoke: cream text, amber fill as each word is spoken) + title card
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
lines, cur = [], []
for w in words:
    cur.append(w)
    if w["w"][-1] in ".,?" or len(cur) >= 7:
        lines.append(cur); cur = []
if cur: lines.append(cur)
ev = []
for ln in lines:
    st, en = ln[0]["s2"] - 0.15, ln[-1]["e2"] + 0.35
    txt, t = "", st
    for w in ln:
        lead_cs = max(0, int(round((w["s2"] - t) * 100)))
        dur_cs = max(1, int(round((w["e2"] - w["s2"]) * 100)))
        txt += f"{{\\k{lead_cs}}}{{\\kf{dur_cs}}}{w['w']} "
        t = w["e2"]
    ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\fad(150,200)}}{txt.strip()}")
tstart = narr_end + 0.6
ev.append(f"Dialogue: 1,{ts(tstart)},{ts(total - 0.2)},Title,,0,0,0,,{{\\fad(1200,900)}}THE BRIDE OF KULDHARA")
ev.append(f"Dialogue: 1,{ts(tstart + 0.6)},{ts(total - 0.2)},Sub,,0,0,0,,{{\\fad(1200,900)}}THE LANTERN MAN")
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Lora,54,&H002E96E8,&H00D2E6EF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,2,2,2,200,200,90,1
Style: Title,Playfair Display,104,&H00D2E6EF,&H00D2E6EF,&H00000000,&H00000000,0,0,0,0,100,100,8,0,1,0,4,5,100,100,40,1
Style: Sub,Lora,40,&H002E96E8,&H002E96E8,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,0,3,5,100,100,-130,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/captions.ass", "w").write(ass)

# 6) audio: narration + anklet bells (cold open) + wind bed + main theme from the intro
theme_in = t_of("When") - 1.6
bells_out = t_of("they") + 0.6   # bells stop on "they stop"
bells = f"{P}/sfx_anklet_bells.mp3"
has_bells = os.path.exists(bells)
a_in = f"-i {OUT}/narration.wav -i {MUS}/creeping_music_box_horror_lullaby.mp3"
a_in += f" -f lavfi -t {total} -i anoisesrc=color=brown:r=48000:a=0.5"
if has_bells: a_in += f" -stream_loop -1 -i {bells}"
fc = [
    "[0:a]volume=1.0,apad[nar]",
    f"[1:a]atrim=0:{total - theme_in + 0.5},asetpts=PTS-STARTPTS,afade=t=in:d=2.5,"
    f"volume='if(lt(t,{narr_end - theme_in}),0.16,0.16+0.34*min(1,(t-{narr_end - theme_in})/1.5))':eval=frame,"
    f"afade=t=out:st={total - theme_in - 2.2}:d=2.2,adelay={int(theme_in * 1000)}|{int(theme_in * 1000)}[mus]",
    f"[2:a]lowpass=f=420,highpass=f=60,volume=0.10,tremolo=f=0.15:d=0.5,afade=t=in:d=2,afade=t=out:st={total - 2.5}:d=2.5,aformat=channel_layouts=stereo[wind]",
]
mix = "[nar][mus][wind]"
n = 3
if has_bells:
    fc.append(f"[3:a]atrim=0:{bells_out},asetpts=PTS-STARTPTS,volume=0.55,afade=t=in:d=0.8,afade=t=out:st={bells_out - 0.25}:d=0.25,aformat=channel_layouts=stereo[bel]")
    mix += "[bel]"; n = 4
fc.append(f"{mix}amix=inputs={n}:duration=longest:normalize=0,atrim=0:{total},alimiter=limit=0.9[aout]")
run(f"ffmpeg -v error -y {a_in} -filter_complex \"{';'.join(fc)}\" -map \"[aout]\" -ar 48000 {OUT}/mix.wav")

# 7) final mux with burned captions
run(f"ffmpeg -v error -y -i {OUT}/video_raw.mp4 -i {OUT}/mix.wav "
    f"-vf \"subtitles={OUT}/captions.ass:fontsdir={P}/fonts\" -c:v libx264 -preset veryfast -crf 18 "
    f"-c:a aac -b:a 192k -shortest -movflags +faststart {P}/lantern_man_pilot.mp4")
print("done", round(total, 2), "s; shots", [round(d, 2) for d in durs], "bells", has_bells)
