from pathlib import Path
from get_packs import get_packs
from functions import *
import zipfile
import shutil
import UnityPy
import json
import os
import gc
from pydub import AudioSegment
import msvcrt
import gzip
from create_info import create_info_v4
from create_playlist import create_playlist


def main():
    # get packs and pack names
    game_folder = Path("C:\\Users\\Administrator\\Downloads\\Beat Saber v1790+1.40.10_8486 -VRP\\com.beatgames.beatsaber")
    obb_file = game_folder / "main.1790.com.beatgames.beatsaber.obb"
    packs = get_packs(obb_file)

    pack_names = [cut_string(pack.replace("assets/aa/Android/", ""), "_pack_assets_all_") for pack in packs]

    # print all pack names and ask user to select one
    for pack in pack_names:
        print(pack)
    pack_id = input("\nPack name (or * for all): ")

    if pack_id == "*":
        for i, pack_name in enumerate(pack_names):
            extract(pack_name, obb_file, packs[i], game_folder)
        print("\nDone! Press any key to exit...")
        msvcrt.getch()
        sys.exit()
        return

    # normal single pack behavior
    if pack_id not in pack_names:
        fatal(f"{pack_id} is not a valid pack name")

    pack_index = pack_names.index(pack_id)
    pack_file = packs[pack_index]

    extract(pack_id, obb_file, pack_file, game_folder)
    print("\nDone! Press any key to exit...")
    msvcrt.getch()
    sys.exit()



def extract(pack_id, obb_file, pack_file, game_folder):
    script_dir = Path(__file__).parent
    packs_folder = script_dir/"extracted_packs"
    packs_folder.mkdir(exist_ok=True)
    pack_folder = packs_folder/pack_id
    pack_folder.mkdir(exist_ok=True) # create the folder

    cls()
    print(f"Pack ID: {pack_id}")
    print(f"OBB file: {obb_file}")
    print(f"Pack file: {pack_file}")
    print(f"Game Folder: {game_folder}\n")

    # extract pack.asset from obb
    print("Extracting pack assets")
    with zipfile.ZipFile(obb_file, "r") as obb:
        with obb.open(pack_file) as src, open(pack_folder/"pack.asset", "wb") as dst:
            shutil.copyfileobj(src, dst)

    pack_file = pack_folder/"pack.asset" # change pack_file to the extracted file instead of in the obb
    


    # extract BeatmapLevel/songPreview and gather song_ids
    song_ids = []

    print("Finding/extracting song info:")
    env = UnityPy.load(str(pack_file))
    for obj in env.objects:
        data = obj.read()

        try:
            file_name = data.m_Name
            file_type = obj.type.name

            if file_type == "MonoBehaviour" and file_name.endswith("BeatmapLevel"):
                if obj.serialized_type.node:
                    tree = obj.read_typetree()

                    song_id = cut_string(tree['m_Name'], "BeatmapLevel")
                    song_folder = pack_folder/song_id
                    song_folder.mkdir(exist_ok=True)
                    tmp_folder = song_folder/"tmp"
                    tmp_folder.mkdir(exist_ok=True)
                    fp = os.path.join(tmp_folder, "BeatmapLevel.json")
                    song_ids.append(song_id)
                    print(" - " + song_id)

                    with open(fp, "wt", encoding = "utf8") as f:
                        json.dump(tree, f, ensure_ascii = False, indent = 4)
            

            if file_type == "AudioClip" and file_name.endswith("Preview"):
                clip = obj.read()
                for name, data in clip.samples.items():

                    song_id = cut_string(name, "Preview.wav")
                    song_folder = pack_folder/song_id
                    song_folder.mkdir(exist_ok=True)
                    tmp_folder = song_folder/"tmp"
                    tmp_folder.mkdir(exist_ok=True)
                    fp = os.path.join(tmp_folder, "songPreview.wav")
                    
                    with open(fp, "wb") as f:
                        f.write(data)

            if file_type == "Texture2D" and file_name.endswith("Cover"):
                data.image.save(os.path.join(pack_folder, f"pack_cover.png"))
        except:
            continue
    print(f"Found {len(song_ids)} songs!")
    print()
    


    # garbage collect UnityPy's env and delete pack.asset
    print("Running garbage collection")
    del env
    gc.collect()
    os.remove(pack_file)
    


    # copy song asset files
    print("Copying song asset files")
    for song_id in song_ids:
        song_folder = pack_folder/song_id
        tmp_folder = song_folder/"tmp"

        shutil.copy(game_folder/song_id, tmp_folder/"song.asset")



    # Extract song asset files
    print()
    for i, song_id in enumerate(song_ids):
        print(f"[{i + 1}/{len(song_ids)}] Extracting song Beatmaps and Music (this may take a few moments)", end="\r")
        song_folder = pack_folder/song_id
        tmp_folder = song_folder/"tmp"

        # Extract song.asset
        env = UnityPy.load(str(tmp_folder/"song.asset"))
        for obj in env.objects:
            try:
                data = obj.read()
                if obj.type.name == "TextAsset":
                    path = os.path.join(song_folder, data.m_Name)
                    with open(path, "wb") as f:
                        f.write(data.m_Script.encode("utf-8", "surrogateescape"))
            
                if obj.type.name == "AudioClip" and data.m_Name == song_id:
                    clip = obj.read()
                    for name, data in clip.samples.items():
                        with open(tmp_folder/"song.wav", "wb") as f:
                            f.write(data)
            except:
                continue
        
        
        # Extract gzips
        for asset in os.listdir(song_folder):
            if not asset.endswith(".gz"): continue

            output = asset.replace(".gz", "").replace(song_id, "").replace(".lightshow", ".lightshow.dat").replace(".beatmap", ".dat")
            if output == ".audio": output = "BPMInfo.dat"
            output = song_folder/output
            asset = song_folder/asset

            with gzip.open(asset, "rb") as f_in:
                with open(output, "wb") as f_out:
                    f_out.write(f_in.read())
            os.remove(asset)
    
    print() # end recursive

    # garbage collect UnityPy's env and delete pack.asset
    print("Running garbage collection")
    del env
    gc.collect()
    for song_id in song_ids:
        tmp_folder = pack_folder/song_id/"tmp"

        for asset in os.listdir(tmp_folder):
            if asset == "song.asset":
                os.remove(tmp_folder/asset)



    # Convert .wav to .ogg
    print()
    for i, song_id in enumerate(song_ids):
        print(f"[{i + 1}/{len(song_ids)}] Converting \".wav\" to \".ogg\" (this may take quite a few moments)", end="\r")
        song_folder = pack_folder/song_id
        tmp_folder = song_folder/"tmp"

        AudioSegment.from_wav(tmp_folder/"song.wav").export(song_folder/"song.ogg", format="ogg")
        os.remove(tmp_folder/"song.wav")
        AudioSegment.from_wav(tmp_folder/"songPreview.wav").export(song_folder/"songPreview.ogg", format="ogg")
        os.remove(tmp_folder/"songPreview.wav")
    print() # end recursive



    for i, song_id in enumerate(song_ids):
        print(f"[{i + 1}/{len(song_ids)}] Creating Info.dat and cover.png", end="\r")
        song_folder = pack_folder/song_id
        tmp_folder = song_folder/"tmp"
        shutil.copyfile(pack_folder/"pack_cover.png", song_folder/"cover.png")
        create_info_v4(pack_id, song_id)
        os.remove(tmp_folder/"BeatmapLevel.json")
        os.rmdir(tmp_folder)
    print() # end recursive
        
    print("Generating playlist and cleaning up")
    create_playlist(pack_id)
    os.remove(pack_folder/"pack_cover.png")





if __name__ == "__main__":
    main()