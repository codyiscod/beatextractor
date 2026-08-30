import json
from pathlib import Path
import os
import msvcrt
import sys
working_dir = Path(__file__).parent



def main():
    create_level_dat("babyonemoretime")



def create_level_dat(song_id):
    info = working_dir/"Exported"/song_id/"song_info"/f"{song_id}BeatmapLevel.json"

    if not os.path.exists(info):
        print(f"\"{song_id.upper()}\" has no \"BeatmapLevel.json\"! You may need to re-export or create a Level.dat yourself.\nPress any key to skip.")
        msvcrt.getch()
        return

    with open(info, "r", encoding="utf-8") as f:
        data = json.load(f)



    # song info
    song_name = data["_songName"]
    song_author = data["_songAuthorName"]
    mappers = data["_levelAuthorName"]

    # filenames
    song_filename = "song.wav"
    song_preview_filename = "songPreview.wav"
    cover_filename = "cover.png"

    # properties
    bpm = data["_beatsPerMinute"]
    song_duration = data["_songDuration"]
    environments = [env["_environmentName"] for env in data["_environmentNames"]]



    # make the base json structure (no dynamically adding yet)
    new_json = {
        "version": "4.0.0",
        "song": {
            "title": song_name,
            "subTitle": mappers,
            "author": song_author
        },
        "audio": {
            "songFilename": song_filename,
            "songDuration": song_duration,
            "bpm": bpm,
            "lufs": 0,
            "previewStartTime": 0,
            "previewDuration": 0
        },
        "songPreviewFilename": song_preview_filename,
        "coverImageFilename": cover_filename,
        "environmentNames": environments,
        "difficultyBeatmaps": [

        ]
    }







    for char_set in data["_previewDifficultyBeatmapSets"]:
        char_charistic = "Standard"  # or whatever you want

        for diff in char_set["_previewDifficultyBeatmaps"]:

            diff_difficulty = diff["_difficulty"]
            difficulty_map = {
                0: "Easy",
                1: "Normal",
                2: "Hard",
                3: "Expert",
                4: "ExpertPlus"
            }

            # make the beatmap dict
            beatmap = {
                "characteristic": char_charistic,
                "difficulty": difficulty_map[diff_difficulty],
                "beatmapDataFilename": difficulty_map[diff_difficulty] + ".dat",
                "lightshowDataFilename": "Common.lightshow.dat", # set later
                "environmentNameIdx": diff["_environmentNameIdx"],
                "beatmapColorSchemeIdx": 0,
                "noteJumpMovementSpeed": diff["_noteJumpMovementSpeed"],
                "noteJumpStartBeatOffset": diff["_noteJumpStartBeatOffset"]
            }

            # append the dict to the list
            new_json["difficultyBeatmaps"].append(beatmap)

        



    # new_json["difficultyBeatmaps"].append({
    #     "beatmapDataFilename": "Easy.dat",
    #     "lightshowDataFilename": "Lightshow.dat"
    # })








    # save it
    output_file = working_dir/"Info.dat"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_json, f, indent=4)

    print("json saved:", output_file)


if __name__ == "__main__":
    main()