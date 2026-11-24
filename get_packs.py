from pathlib import Path
import zipfile

def get_packs(obb_path):
    ignore = [
        "environment_",
        "core_",
        "_unitybuildinassets_",
        "scenes_",
        "textmeshprofonts_",
        "promobannerconfig_",
        "metaremoteassets_",
        "default_assets_",
        "debug_pack_",
        "coretrackdefinitions_",
        "extras_"
    ]

    packs = []

    with zipfile.ZipFile(obb_path, "r") as obb:
        for file in obb.namelist():
            if file.startswith("assets/aa/Android/") and not any(x in file for x in ignore) and "_pack" in file:
                name = file.replace("assets/aa/Android/", "")
                name = name.split("_pack_assets_")[0]  # cut at "_pack_assets_" and drop the rest
                packs.append(file)
    
    return packs
            



            # dump directly into script_dir
            # with obb.open(file) as src, open(script_dir / Path(file).name, "wb") as dst:
            #     dst.write(src.read())
            # print(f"extracted {file} to {script_dir}")

            

# extract just that one file into script_dir
# with zipfile.ZipFile(obb_path, "r") as obb:
#     obb.extract(target_file, script_dir)

# print(f"extracted {target_file} to {script_dir}")