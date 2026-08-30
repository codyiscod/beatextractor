from pathlib import Path
import json
from mutagen.oggvorbis import OggVorbis
import math

script_dir = Path(__file__).parent
packs_folder = script_dir/"extracted_packs"

def create_info_v4(pack_id, song_id):
    pack_folder = packs_folder/pack_id
    song_folder = pack_folder/song_id
    beatmaplevel = song_folder/"tmp"/"BeatmapLevel.json"
    src_json = script_dir / "templates" / "4-0-0.dat"

    # load stuff
    with open(beatmaplevel, "r", encoding="utf-8") as f:
        bmldata = json.load(f)
    with open(src_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    song_audio = OggVorbis(song_folder/"song.ogg")
    song_duration = song_audio.info.length
    preview_audio = OggVorbis(song_folder/"songPreview.ogg")
    preview_duration = preview_audio.info.length


    char_map = {
        -7286399427822119286: "Standard",
        -8583864861369561029: "NoArrows",
        -5623662769225589684: "OneSaber",
        4533580413116749821: "360Degree",
        -5995858427784384822: "90Degree",
        -837073142869603409: "Legacy"
    }

    diff_map = {
        0: "Easy",
        1: "Normal",
        2: "Hard",
        3: "Expert",
        4: "ExpertPlus"
    }


    # modify values however u want
    data["song"]["title"] = bmldata["_songName"]
    data["song"]["subTitle"] = bmldata["_songSubName"]
    data["song"]["author"] = bmldata["_songAuthorName"]
    data["audio"]["songDuration"] = math.ceil(song_duration)
    data["audio"]["bpm"] = bmldata["_beatsPerMinute"]
    data["audio"]["previewDuration"] = math.ceil(preview_duration)

    for environment in bmldata["_environmentNames"]:
        data["environmentNames"].append(environment["_environmentName"])
    
    for scheme in bmldata["_colorSchemes"]:
        data["colorSchemes"].append({
            "useOverride": scheme["_overrideNotes"] == 1, # False/True via 0/1
            "colorSchemeName": scheme["_colorSchemeId"],
            "saberAColor": scheme["_saberAColor"],
            "saberBColor": scheme["_saberBColor"],
            "obstaclesColor": scheme["_obstaclesColor"],
            "environmentColor0": scheme["_environmentColor0"],
            "environmentColor1": scheme["_environmentColor1"],
            "environmentColor0Boost": scheme["_environmentColor0Boost"],
            "environmentColor1Boost": scheme["_environmentColor1Boost"]
        })

    # char = characteristic
    # diff = difficulty
    data["difficultyBeatmaps"] = []
    for i, char in enumerate(bmldata["_previewDifficultyBeatmapSets"]):
        for j, diff in enumerate(char["_previewDifficultyBeatmaps"]):
            
            characteristic = char_map.get(char["_beatmapCharacteristic"]["m_PathID"], "Standard")
            difficulty = diff_map.get(j, "ExpertPlus")

            # beatmap filename
            if characteristic != "Standard":
                beatmap_filename = song_id + characteristic + difficulty + ".beatmap"
            else:
                beatmap_filename = difficulty + ".dat"

            # lightshow filename
            lightshow_file = Path(song_folder/f"{difficulty}.lightshow.dat")
            lightshow_filename = f"{difficulty}.lightshow.dat" if lightshow_file.exists() else "Common.lightshow.dat"

            # make data
            data["difficultyBeatmaps"].append({
                "characteristic": characteristic,
                "difficulty": difficulty,
                "beatmapAuthors": {
                    "mappers": [bmldata["_levelAuthorName"]],
                    "lighters": [bmldata["_levelAuthorName"]]
                },
                "environmentNameIdx": diff["_environmentNameIdx"],
                "beatmapColorSchemeIdx": diff["_beatmapColorSchemeIdx"],
                "noteJumpMovementSpeed": diff["_noteJumpMovementSpeed"],
                "noteJumpStartBeatOffset": diff["_noteJumpStartBeatOffset"],
                "beatmapDataFilename": beatmap_filename,
                "lightshowDataFilename": lightshow_filename
            })


    # save to new location
    dest_json = song_folder / "Info.dat"
    with open(dest_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)