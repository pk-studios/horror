"""Build Episode 1 of The Lantern Man, part by part. Usage: python build_ep01.py [part numbers]"""
import json, os, re, subprocess, sys

ROOT = "/home/claude/OpenMontage"
E = f"{ROOT}/projects/ep01"
A = f"{E}/audio"
ST = [f"{E}/stills", f"{ROOT}/projects/pilot/stills"]
MUS = f"{ROOT}/assets/music/lantern-man"
FONTS = f"{ROOT}/projects/pilot/fonts"
FPS, XF = 30, 1.0

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(cmd[:300]); print(r.stderr[-3000:]); sys.exit(1)
    return r.stdout

def img(name):
    for d in ST:
        if os.path.exists(f"{d}/{name}.png"): return f"{d}/{name}.png"
    raise FileNotFoundError(name)

V = dict(z=(1.10, 1.20))           # tighter "second look" at an image
VL = dict(z=(1.12, 1.22), fx=0.35) # second look, left of centre
VR = dict(z=(1.12, 1.22), fx=0.65) # second look, right of centre
F = dict(flip=True)

# (anchor words, image, options)
SHOTS = {
 1: [("Kamla found me", "p1_guesthouse", {}), ("She ran a small", "02_ruins_wide", {}),
     ("She met me", "p1_kamla_gate", {}), ("And a wooden walking", "p1_stick_hand", {}),
     ("They say you're", "p1_hero_kamla", F), ("Her guesthouse had", "p1_corridor", {}),
     ("Guests stayed one", "p1_empty_room", {}), ("Bells. Anklet bells", "p1_window_ruins", {}),
     ("And in the daytime", "p1_dawn_prints", {}), ("No footprints coming", "03_well", {}),
     ("And then there's my", "p1_dev_window", {}), ("She packed a bag", "p1_dev_window", V),
     ("Since then, Dev", "p3_dev_street", {}), ("Her hand was shaking", "p1_shaking_hand", {}),
     ("A young wife who", "04_ghost_street", {}), ("I already had", "06_hero_closeup", F),
     ("What I didn't know", "05_hero_ruins", {})],
 2: [("At two in the morning", "07_hero_walk", {}), ("If you've never seen", "02_ruins_wide", {}),
     ("No roofs", "p2_courtyard", {}), ("Just walls", "08_title_bg", {}),
     ("I set my lantern", "p2_lantern_ground", {}), ("At ten past two", "01_footprints", {}),
     ("The footprints formed", "p2_prints_lantern", {}), ("And then I saw her", "04_ghost_street", {}),
     ("She didn't turn", "p2_ghost_far", {}), ("The dead aren't", "04_ghost_street", V),
     ("I picked up my", "p2_hero_follow", F), ("She walked the whole", "p2_temple", {}),
     ("And there, she stopped", "p2_ghost_well", {}), ("Not at me", "p2_riverbed", {}),
     ("Then she was gone", "03_well", {}), ("I walked up to the well", "p2_hero_well", {}),
     ("But somewhere down there", "p2_well_down", {}), ("I didn't sleep", "p1_window_ruins", V)],
 3: [("In the morning, I asked", "p3_dawn_ruins", {}), ("I asked them about", "p3_tea_gate", {}),
     ("200 years ago, they", "p3_old_village", {}), ("Then a powerful minister", "p3_horseman", {}),
     ("He gave the village", "p3_horseman", V), ("The village didn't fight", "p3_old_village", VR),
     ("In a single night", "p3_exodus", {}), ("By morning", "p3_empty_dawn", {}),
     ("And as they left", "p3_curse", {}), ("That's the legend", "02_ruins_wide", V),
     ("200 years ago, a", "p3_exodus", VL), ("Last year, one girl", "04_ghost_street", {}),
     ("She ran off to", "p1_guesthouse", V), ("Nobody had asked", "p2_well_down", {}),
     ("I asked Kamla if", "p3_bedroom", {}), ("Only one thing was", "p3_bangles", {}),
     ("So she had packed", "p2_ghost_far", V), ("I found Dev on", "p3_dev_roof", {}),
     ("He was lying", "p3_dev_hands", {}), ("So I told him", "p3_hero_dev", {}),
     ("That night, Anjali told", "p3_dev_roof", V), ("They argued", "p1_dev_window", {}),
     ("I don't sleepwalk", "p3_dev_street", {}), ("And he has never walked", "03_well", V),
     ("So now I had", "p3_hero_dev", V), ("If you're thinking", "p3_dev_street", V)],
 4: [("The next night", "p4_hero_well", {}), ("At ten past two, the bells", "01_footprints", V),
     ("She was standing beside", "p4_side_by_side", {}), ("The night before", "p4_hero_well", V),
     ("And I heard what", "p4_riverbed_dark", {}), ("Tap", "p4_riverbed_dark", V),
     ("Something coming up", "p2_riverbed", V), ("A stick", "p4_stick_marks", {}),
     ("The tapping came closer", "p4_planks", {}), ("Then the bells shook", "p4_planks", V),
     ("Only the sound of sand", "p2_well_down", V), ("I stood there", "p4_hero_alone", {}),
     ("Dev doesn't walk", "p3_dev_street", {}), ("Kamla had told me", "p1_stick_hand", V),
     ("She hadn't been waiting", "p2_ghost_well", V)],
 5: [("In the morning, I told", "p5_kamla_door", {}), ("It has to be", "p1_hero_kamla", F),
     ("She was quiet", "p1_shaking_hand", V), ("I spoke to Dev", "p5_temple_wall", {}),
     ("At two o'clock", "p5_walk_together", {}), ("When we reached", "p5_kamla_well", {}),
     ("Ten past two. The bells", "01_footprints", {}), ("Kamla heard them", "p1_shaking_hand", {}),
     ("The bells came down", "04_ghost_street", {}), ("Anjali. In her red", "p5_ghost_reveal", {}),
     ("For eleven months, she had", "p2_ghost_well", {}), ("The rule is simple", "p5_ghost_reveal", V),
     ("Kamla's stick fell", "p5_stick_fallen", {}), ("I heard you leave", "p2_riverbed", {}),
     ("I didn't mean", "p5_kamla_kneel", {}), ("You were taking", "p5_kamla_kneel", V),
     ("I covered the well", "p4_planks", {}), ("Anjali didn't move", "p5_ghost_reveal", VR),
     ("Then, from the dark", "p5_dev_step", {}), ("He couldn't see her", "p5_ghost_turn", {}),
     ("And then she was gone", "p5_empty_edge", {}), ("At dawn, the police", "p5_dawn_rope", {}),
     ("Her cloth bag", "p5_bag", {}), ("Kamla didn't deny", "p1_kamla_gate", V),
     ("The guesthouse is closed", "p5_closed_house", {}), ("Dev lives in", "p5_city", {}),
     ("And at ten past two in", "p5_smooth_sand", {}), ("The dead can't speak. But", "p5_hero_road", {})],
 6: [("The story you just", "p6_wide_dusk", {}), ("Kuldhara stands in", "p6_daylight", {}),
     ("In the early", "p6_doorway", {}), ("The story of Salim", "p3_horseman", {}),
     ("The river that fed", "p6_dry_river", {}), ("One account suggests", "p3_empty_dawn", V),
     ("Today, Kuldhara is", "p6_daylight", V), ("If you go", "p6_doorway", V),
     ("Which haunted place", "p6_hero_edge", {})],
}

# Sound design: (start anchor, end anchor or seconds, file, gain, loop)
SFX = {
 1: [("And a wooden walking", 4.0, "sfx_stick_taps.mp3", 0.3, True),
     ("Bells. Anklet bells", 5.0, "sfx_anklet_bells.mp3", 0.08, True)],
 2: [("At ten past two", "And there, she stopped", "sfx_anklet_bells.mp3", 0.14, True),
     ("But somewhere down there", 6.0, "sfx_sand_falling.mp3", 0.15, True)],
 4: [("At ten past two, the bells", "And they stopped", "sfx_anklet_bells.mp3", 0.14, True),
     ("Tap", "Not footsteps", "sfx_stick_taps.mp3", 0.4, True),
     ("The tapping came closer", 3.0, "sfx_stick_taps.mp3", 0.4, True),
     ("Then the bells shook", 2.0, "sfx_bells_rattle.mp3", 0.2, False),
     ("Only the sound of sand", 6.0, "sfx_sand_falling.mp3", 0.15, True)],
 5: [("At two o'clock", "When we reached", "sfx_stick_taps.mp3", 0.3, True),
     ("Ten past two. The bells", "Anjali. In her red", "sfx_anklet_bells.mp3", 0.14, True),
     ("Kamla's stick fell", 1.0, "sfx_stick_drop.mp3", 0.25, False)],
}

# Music: (start anchor or 0, end anchor or None=end, track, volume)
MUSIC = {
 1: [(0, None, "dark_cinematic.mp3", 0.09)],
 2: [(0, "At ten past two", "dark_cinematic.mp3", 0.09), ("I walked up to the well", None, "ombre_nella_nebbia.mp3", 0.07)],
 3: [(0, "Nobody had asked", "gaslight_waltz.mp3", 0.08), ("I asked Kamla if", None, "horror_music_box.mp3", 0.07)],
 4: [("I stood there", None, "ombre_nella_nebbia.mp3", 0.08)],
 5: [(0, "Ten past two. The bells", "horror_music_box.mp3", 0.07), ("Anjali. In her red", "Kamla's stick fell", "gothic_choir.mp3", 0.16),
     ("And then she was gone", "The dead can't speak. But", "haunting_gothic_piano.mp3", 0.12),
     ("The dead can't speak. But", None, "creeping_music_box_horror_lullaby.mp3", 0.22)],
 6: [(0, None, "ombre_nella_nebbia.mp3", 0.10)],
}
WIND = {1: 0.05, 2: 0.07, 3: 0.04, 4: 0.08, 5: 0.06, 6: 0.0}
END_CARD = {5: ("THE LANTERN MAN", "The dead can't speak. Someone has to watch.", 5.0),
            6: ("THE LANTERN MAN", "Which haunted place should he visit next?", 6.0)}

def norm(t): return re.sub(r"[^a-z0-9']", "", t.lower().replace("’", "'"))

def find_anchor(words, phrase, start_idx):
    toks = [norm(t) for t in phrase.split()]
    for i in range(start_idx, len(words) - len(toks) + 1):
        if all(norm(words[i + j]["w"]) == toks[j] for j in range(len(toks))):
            return i
    raise KeyError(f"anchor not found: {phrase!r} after {start_idx}")

def build(p):
    OUT = f"{E}/build/part{p}"; os.makedirs(OUT, exist_ok=True)
    words = json.load(open(f"{A}/part{p}_words.json"))
    # pacing: make sure every sentence end is followed by a real pause
    cuts, pads = [], []
    for i, w in enumerate(words[:-1]):
        gap = words[i + 1]["s"] - w["e"]
        t = w["w"].rstrip('"”')
        want = 1.3 if t.endswith("...") or t.endswith("…") else (0.95 if t[-1:] in ".?!" else 0)
        if norm(w["w"]) == "tap": want = 1.4
        if want and gap < want:
            cuts.append(round((w["e"] + words[i + 1]["s"]) / 2, 3)); pads.append(round(want - gap, 2))
    LEAD = 1.5
    bounds = [0.0] + cuts + [None]; parts = []
    run(f"ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=stereo -t {LEAD} {OUT}/lead.wav"); parts.append(f"{OUT}/lead.wav")
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        f = f"{OUT}/n{k:03d}.wav"
        run(f"ffmpeg -v error -y -ss {a}" + (f" -to {b}" if b else "") + f" -i {A}/part{p}.mp3 -ar 48000 -ac 2 {f}")
        parts.append(f)
        if k < len(pads):
            s = f"{OUT}/s{k:03d}.wav"
            run(f"ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=stereo -t {pads[k]} {s}"); parts.append(s)
    open(f"{OUT}/concat.txt", "w").write("".join(f"file '{x}'\n" for x in parts))
    run(f"ffmpeg -v error -y -f concat -safe 0 -i {OUT}/concat.txt -c pcm_s16le {OUT}/narration.wav")
    shift, ci = LEAD, 0
    for w in words:
        while ci < len(cuts) and w["s"] > cuts[ci]:
            shift += pads[ci]; ci += 1
        w["s2"], w["e2"] = round(w["s"] + shift, 2), round(w["e"] + shift, 2)
    narr_end = float(run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {OUT}/narration.wav"))
    card = END_CARD.get(p)
    total = narr_end + 1.2 + (card[2] if card else 0.8)

    # anchors -> times (searched in order so repeated phrases resolve correctly)
    cache = {}
    def T(phrase):
        if phrase == 0: return 0.0
        if phrase is None: return total
        if phrase not in cache:
            cache[phrase] = words[find_anchor(words, phrase, 0)]["s2"]
        return cache[phrase]
    shots, idx = [], 0
    for anc, im, opt in SHOTS[p]:
        i = find_anchor(words, anc, idx); idx = i + 1
        st = 0.0 if not shots else max(words[i]["s2"] - 0.35, shots[-1][1] + 1.6)
        shots.append((im, st, opt))
    durs = [(shots[i + 1][1] if i + 1 < len(shots) else total) - shots[i][1] for i in range(len(shots))]

    # shots: slow push-in / pull-out, grade, grain
    AUDIO_ONLY = os.environ.get("AUDIO_ONLY") == "1" and os.path.exists(f"{OUT}/video.mp4")
    for i, ((im, st, opt), d) in enumerate(zip(shots, durs)):
        if AUDIO_ONLY: break
        n = int(round((d + (XF if i < len(shots) - 1 else 0)) * FPS))
        z0, z1 = opt.get("z", (1.0, 1.08) if i % 2 == 0 else (1.08, 1.0))
        fx, fy = opt.get("fx", 0.5), opt.get("fy", 0.5)
        z = f"{z0}+({z1}-{z0})*on/{n}"
        x = f"max(0,min(iw-iw/zoom,iw*{fx}-iw/zoom/2))"; y = f"max(0,min(ih-ih/zoom,ih*{fy}-ih/zoom/2))"
        flip = "hflip," if opt.get("flip") else ""
        vf = (f"{flip}scale=2880:-2:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1920x1080:fps={FPS},"
              f"eq=contrast=1.04:saturation=0.92,vignette=PI/4.5,noise=alls=6:allf=t,format=yuv420p")
        run(f"ffmpeg -v error -y -loop 1 -i {img(im)} -vf \"{vf}\" -frames:v {n} -c:v libx264 -preset ultrafast -crf 14 {OUT}/shot{i:02d}.mp4")

    # captions + end card
    def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"].rstrip('"”')[-1:] in ".,?!" or len(cur) >= 7: lines.append(cur); cur = []
    if cur: lines.append(cur)
    ev = []
    for ln in lines:
        s0, e0 = ln[0]["s2"] - 0.15, ln[-1]["e2"] + 0.35
        txt, t = "", s0
        for w in ln:
            txt += f"{{\\k{max(0,int(round((w['s2']-t)*100)))}}}{{\\kf{max(1,int(round((w['e2']-w['s2'])*100)))}}}{w['w']} "
            t = w["e2"]
        ev.append(f"Dialogue: 0,{ts(s0)},{ts(e0)},Cap,,0,0,0,,{{\\fad(150,200)}}{txt.strip()}")
    if card:
        c0 = narr_end + 1.0
        ev.append(f"Dialogue: 1,{ts(c0)},{ts(total-0.2)},Title,,0,0,0,,{{\\fad(1200,900)}}{card[0]}")
        ev.append(f"Dialogue: 1,{ts(c0+0.6)},{ts(total-0.2)},Sub,,0,0,0,,{{\\fad(1200,900)}}{card[1]}")
    if p == 6:
        ev.append(f"Dialogue: 1,{ts(2)},{ts(narr_end)},Src,,0,0,0,,{{\\fad(600,600)}}Sources: Inditales (inditales.com) · Amusing Planet (amusingplanet.com)")
    ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Lora,54,&H002E96E8,&H00D2E6EF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,2,2,2,200,200,90,1
Style: Title,Playfair Display,104,&H00D2E6EF,&H00D2E6EF,&H00000000,&H00000000,0,0,0,0,100,100,8,0,1,0,4,5,100,100,40,1
Style: Sub,Lora,40,&H002E96E8,&H002E96E8,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,3,5,100,100,-130,1
Style: Src,Lora,28,&H00D2E6EF,&H00D2E6EF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,0,2,7,60,60,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
    open(f"{OUT}/captions.ass", "w").write(ass)

    # crossfade chain + burned captions
    ins = " ".join(f"-i {OUT}/shot{i:02d}.mp4" for i in range(len(shots)))
    fc, prev, off = [], "[0:v]", 0.0
    for i in range(1, len(shots)):
        off += durs[i - 1]
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev = f"[v{i}]"
    fc.append(f"{prev}subtitles={OUT}/captions.ass:fontsdir={FONTS}[vout]")
    if not AUDIO_ONLY: run(f"ffmpeg -v error -y {ins} -filter_complex \"{';'.join(fc)}\" -map \"[vout]\" -c:v libx264 -preset veryfast -crf 19 -t {total:.3f} {OUT}/video.mp4")

    # audio mix
    ain, fa, labels = [f"-i {OUT}/narration.wav"], ["[0:a]apad[nar]"], ["[nar]"]
    k = 1
    for s, e, tr, vol in MUSIC.get(p, []):
        t0, t1 = T(s), T(e)
        L = t1 - t0
        ain.append(f"-stream_loop -1 -i {MUS}/{tr}")
        fa.append(f"[{k}:a]atrim=0:{L:.2f},asetpts=PTS-STARTPTS,volume={vol},afade=t=in:d=2,afade=t=out:st={max(0,L-2.5):.2f}:d=2.5,"
                  f"aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(t0*1000)}|{int(t0*1000)}[m{k}]")
        labels.append(f"[m{k}]"); k += 1
    for s, e, f, g, loop in SFX.get(p, []):
        t0 = T(s); L = (T(e) - t0) if isinstance(e, str) else e
        ain.append(("-stream_loop -1 " if loop else "") + f"-i {A}/{f}")
        fa.append(f"[{k}:a]atrim=0:{L:.2f},asetpts=PTS-STARTPTS,volume={g},afade=t=in:d=0.3,afade=t=out:st={max(0,L-0.4):.2f}:d=0.4,"
                  f"aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(t0*1000)}|{int(t0*1000)}[x{k}]")
        labels.append(f"[x{k}]"); k += 1
    if WIND.get(p):
        ain.append(f"-f lavfi -t {total:.2f} -i anoisesrc=color=brown:r=48000:a=0.5")
        fa.append(f"[{k}:a]lowpass=f=420,highpass=f=60,volume={WIND[p]*2},tremolo=f=0.15:d=0.5,afade=t=in:d=2,afade=t=out:st={total-2:.2f}:d=2,aformat=channel_layouts=stereo[w]")
        labels.append("[w]"); k += 1
    fa.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=0:{total:.3f}[aout]")
    run(f"ffmpeg -v error -y {' '.join(ain)} -filter_complex \"{';'.join(fa)}\" -map \"[aout]\" -ar 48000 -ac 2 {OUT}/mix.wav")
    run(f"ffmpeg -v error -y -i {OUT}/video.mp4 -i {OUT}/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest {E}/part{p}.mp4")
    print(f"part {p}: {total:.1f}s, {len(shots)} shots, longest hold {max(durs):.1f}s", flush=True)

if __name__ == "__main__":
    for p in [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]:
        build(p)
