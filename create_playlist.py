from pathlib import Path
import json
import base64
import hashlib

script_dir = Path(__file__).parent
packs_folder = script_dir/"extracted_packs"

def create_playlist(pack_id):
    pack_folder = packs_folder/pack_id
    playlist_template = script_dir/"templates"/"playlist.bplist"


    # import stuff

    with open(playlist_template, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(pack_folder/"pack_cover.png", "rb") as f:
        b64_string = base64.b64encode(f.read()).decode("utf-8")

    data["image"] = b64_string
    

    authors = []
    for folder in pack_folder.iterdir():
        if folder.is_dir():
            info_file = folder/"Info.dat"

            # get hash
            with open(info_file, "rb") as f:
                sha1 = hashlib.sha1(f.read()).hexdigest()

            with open(info_file, "r", encoding="utf-8") as f:
                info = json.load(f)

                # add to authors array
                author = info["song"]["author"]
                if author not in authors:
                    authors.append(author)
                
                # create song item in playlist songs array
                data["songs"].append({
                    "hash": sha1,
                    "songName": info["song"]["title"]
                })

    data["playlistAuthor"] = ", ".join(authors)
    data["playlistTitle"] = ", ".join(authors)


    # save to new location
    with open(pack_folder/f"{pack_id}.bplist", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
