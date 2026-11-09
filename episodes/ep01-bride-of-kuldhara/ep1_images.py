"""Generate Episode 1 stills. Usage: python ep1_images.py [keys...]"""
import sys, os, concurrent.futures as cf
sys.path.insert(0, "/home/claude/OpenMontage")
from dotenv import load_dotenv; load_dotenv("/home/claude/OpenMontage/.env")
from tools.graphics.google_imagen import GoogleImagen

OUT = "/home/claude/OpenMontage/projects/ep01/stills"
os.makedirs(OUT, exist_ok=True)
D = "/home/claude/OpenMontage/assets/characters/lantern-man/"
REFS = [D + "ref_back_fullbody.jpg", D + "ref_side_silhouette.jpg", D + "ref_lantern_closeup.jpg"]
STYLE = ("dark painterly cinematic still, deep indigo shadows, a single warm amber light source, fine film grain, "
         "quiet and eerie, no clear faces, no text, no letters, 16:9")
HERO = ("Using the exact same man from the reference images (ankle-length charcoal-black wool greatcoat, high turned-up collar, "
        "back half-belt with two buttons, frayed damp hem, short messy curly dark hair, brass hurricane lantern with one cracked "
        "glass pane held low in his LEFT hand), always seen from behind, face never visible. New scene: ")
KAMLA = "an old woman seen from behind, grey wool shawl over her head and shoulders, plain cream sari, a wooden walking stick in her right hand, face never visible"
GHOST = "a pale, blurred, translucent young woman seen from behind, a red shawl over her head, cream skirt, a small brown cloth bag on her shoulder, face never visible"
DEV = "a young man in a dark kurta seen as a silhouette from behind, short dark hair, face never visible"
VIL = "an abandoned desert village of low roofless Rajasthani sandstone houses (no columns, no Greek or Roman ruins)"

IMAGES = {
 # Part 1 - the call
 "p1_guesthouse": f"a desert road at dusk leading to a small yellow sandstone guesthouse with a faded blank wooden sign, beyond it the dark outline of {VIL}, deep blue dusk sky",
 "p1_stick_hand": "close-up of an old woman's wrinkled hand resting on the top of a wooden walking stick, a grey wool shawl over her arm, stone gateway behind, dusk light",
 "p1_kamla_gate": f"{KAMLA}, standing at the stone gate of a small desert guesthouse at dusk, a single lamp lit above the gate",
 "p1_hero_kamla": HERO + f"he stands at the stone gate of a desert guesthouse at dusk facing {KAMLA.replace('seen from behind', 'whose face is hidden in deep shadow under her shawl')}",
 "p1_empty_room": "an empty simple guest room, a neatly made bed with dust on the sheets, a small window showing dark ruins in the distance, moonlight",
 "p1_corridor": "a narrow corridor of a small desert guesthouse at night, a row of closed wooden doors, one small oil lamp on the wall",
 "p1_window_ruins": f"view through an open wooden window at night towards {VIL} in the distance under a starry sky, curtains moving in the wind",
 "p1_dawn_prints": f"early dawn, a sandy street inside {VIL}, a line of small bare footprints in the sand leading away, pale cold light",
 "p1_dev_window": f"{DEV}, standing at a window at night looking out towards dark unlit ruins of {VIL} in the far distance, no lights in the ruins, the room dark behind him",
 "p1_shaking_hand": "close-up of an old woman's hand gripping a wooden walking stick tightly, knuckles pale, dim amber lamp light, dark background",
 # Part 2 - the haunting
 "p2_courtyard": f"a ruined courtyard inside {VIL} at night, empty doorways, a small old stone temple at one side, mist on the ground",
 "p2_temple": "a small old sandstone Hindu temple standing alone among ruined houses at night, carved doorway in shadow, starry sky",
 "p2_lantern_ground": "an old brass hurricane lantern with one cracked glass pane set down on sand at the head of an empty ruined village street at night, its flame lighting the sand",
 "p2_prints_lantern": f"small bare footprints pressed into soft sand right beside a glowing brass hurricane lantern at night, the prints leading away down a sandy street of {VIL}",
 "p2_ghost_far": f"{GHOST}, far down a long sandy street between roofless stone houses at night, walking past a small temple, mist",
 "p2_ghost_well": f"{GHOST}, standing at the edge of an old open stone well at night with her back fully to the camera, the red shawl covering her head and hair completely, looking away into the dark, mist",
 "p2_well_down": "looking straight down into a deep dark stone well half covered with old grey planks and drifted sand, warm lantern light on the rim fading into blackness below",
 "p2_riverbed": "a wide dry riverbed of cracked earth and stones beyond a ruined desert village at night, deep darkness, faint starlight",
 "p2_hero_well": HERO + "he holds the lantern out over an old open stone well at night, half covered with planks and sand, looking down into it",
 "p2_hero_follow": HERO + f"he walks slowly down a sandy street of {VIL} at night, far ahead a pale blurred figure in a red shawl",
 # Part 3 - the search
 "p3_dawn_ruins": f"{VIL} at dawn, pale gold light on the stone walls, long shadows, empty",
 "p3_tea_gate": "a small roadside tea stall at the gate of a ruined desert village at dawn, a steaming kettle on a clay stove, a man seen from behind, no faces",
 "p3_old_village": "the same desert village two hundred years ago, alive at night, low sandstone houses with roofs, an oil lamp in every doorway, people seen from behind in traditional Rajasthani clothes, no faces",
 "p3_horseman": "a silhouetted man on horseback at a desert village gate at night, burning torches behind him, menacing, no face visible",
 "p3_exodus": "long lines of families seen from behind carrying bundles, with oxcarts, walking out of a desert village into the moonlit desert at night, no faces",
 "p3_empty_dawn": f"an empty street in {VIL} at dawn, silence, dust in the air, no people",
 "p3_curse": "an old man's silhouette at the edge of a desert village at night raising one hand back towards the empty houses, wind blowing sand, dramatic",
 "p3_bedroom": "a small simple bedroom, a wooden wardrobe door half open showing folded colourful saris, a small tin of glass bangles on a shelf, dim lamp light",
 "p3_bangles": "close-up of a small open tin of red and gold glass wedding bangles on a wooden shelf, dim warm lamp light, dust",
 "p3_dev_roof": f"{DEV}, sitting on the flat roof of a desert guesthouse at dusk looking out towards distant ruins",
 "p3_hero_dev": HERO + f"he stands on the flat roof of a desert guesthouse at dusk beside {DEV}, both looking out at distant ruins",
 "p3_dev_hands": "close-up of a young man's hands clasped tightly together, fingers twisting, dusk light, dark kurta sleeve",
 "p3_dev_street": f"{DEV}, standing alone at the end of a dark sandy street of {VIL} at night, waiting",
 # Part 4 - the twist
 "p4_hero_well": HERO + "he stands at the edge of an old open stone well at night, the lantern on the ground beside him, facing away from the camera towards a dark dry riverbed",
 "p4_riverbed_dark": "a dark dry riverbed at night seen from a slight height, stones and cracked earth, deep shadow, something unseen approaching, no figures",
 "p4_side_by_side": HERO + f"he stands at the edge of an old stone well at night and beside him stands {GHOST}, her back fully to the camera and the red shawl covering her head completely, both looking away into the dark towards a dry riverbed",
 "p4_stick_marks": "close-up of sand at night lit by lantern light: uneven dragging footprints and, beside them, small round holes left by a walking stick",
 "p4_planks": "close-up of the edge of an old stone well at night, weathered grey planks and drifted sand, a few grains of sand sliding into the dark gap",
 "p4_hero_alone": HERO + "he stands alone at the edge of an old stone well at night, the lantern flame flickering low, vast darkness around him",
 # Part 5 - the delivery
 "p5_kamla_door": f"{KAMLA}, standing in the doorway of a small desert guesthouse at dawn, pale light",
 "p5_temple_wall": "the dark side of an old ruined temple wall at night near an old stone well, deep shadow where someone could hide",
 "p5_walk_together": HERO + f"he walks into {VIL} at night beside {KAMLA}, both seen from behind, his lantern lighting the sand",
 "p5_kamla_well": f"{KAMLA}, standing at the edge of an old stone well at night looking down at the sand, lit by warm lantern light from the side",
 "p5_ghost_reveal": f"seen from behind an old woman in a grey shawl with a walking stick: {GHOST.replace('seen from behind', 'facing the old woman')} standing at the edge of an old stone well three steps away, the red shawl hanging over her face so it is hidden, moonlight, mist",
 "p5_stick_fallen": "a wooden walking stick lying fallen on the sand beside an old stone well at night, lantern light",
 "p5_kamla_kneel": f"{KAMLA}, kneeling in the sand at the edge of an old stone well at night, shoulders bowed, her stick on the ground",
 "p5_dev_step": f"{DEV}, stepping out from behind a dark ruined temple wall into the edge of warm lantern light at night",
 "p5_ghost_turn": f"{GHOST.replace('seen from behind', 'turning slowly')}, turning towards {DEV} who stands in the lantern light, her face still hidden by the shawl, at the edge of a well at night",
 "p5_empty_edge": "the edge of an old stone well at night, empty, the sand around it perfectly smooth, mist settling",
 "p5_dawn_rope": f"dawn over {VIL}, a rope hanging over the rim of an old stone well, far away on the desert road the faint blue flash of a police light",
 "p5_bag": "an old brown cloth bag lying open on sand at dawn, two blank paper train tickets showing at its mouth, no readable text",
 "p5_closed_house": "a small yellow sandstone desert guesthouse at dawn, all shutters closed, the gate shut, empty",
 "p5_city": f"{DEV}, standing on a rooftop at dusk looking over an old Indian city of pink walls and domes, lights coming on",
 "p5_smooth_sand": f"a sandy street of {VIL} at night, the sand perfectly smooth with no footprints, moonlight, total stillness",
 "p5_hero_road": HERO + "he walks slowly away down a long dark desert road at night, lantern low, the ruins small behind him",
 # Part 6 - the real legend
 "p6_wide_dusk": f"a wide view of {VIL} at dusk, orange and violet sky, long shadows, beautiful and quiet",
 "p6_doorway": "a carved sandstone doorway of an abandoned desert house at dusk, warm last light on the stone, empty interior",
 "p6_dry_river": "a dry riverbed at dusk near a ruined desert village, cracked earth, warm low light",
 "p6_daylight": f"{VIL} in soft late-afternoon light, a few distant visitors seen from behind walking among the ruins, no faces",
 "p6_hero_edge": HERO + f"he stands at the edge of {VIL} at dusk, silhouetted against the violet sky, lantern low",
}

def gen(k):
    p = IMAGES[k]
    inp = {"model": "gemini-3.1-flash-lite-image", "aspect_ratio": "16:9", "prompt": p + ", " + STYLE,
           "output_path": f"{OUT}/{k}.png"}
    if p.startswith("Using the exact same man"):
        inp.update(generation_mode="edit", image_paths=REFS)
    for attempt in range(2):
        r = GoogleImagen().execute(inp)
        if r.success: return k, True, ""
    return k, False, r.error

if __name__ == "__main__":
    keys = sys.argv[1:] or [k for k in IMAGES if not os.path.exists(f"{OUT}/{k}.png")]
    with cf.ThreadPoolExecutor(4) as ex:
        for k, ok, err in ex.map(gen, keys):
            print(k, ok, err[:200])
