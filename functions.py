import os
import msvcrt
import sys
from pathlib import Path



def cls():
    os.system("cls")


def fatal(reason):
    cls()
    print(f"A fatal error has occurred:\n{reason}\n")
    print("Press any key to exit the program")
    msvcrt.getch()
    sys.exit()


def check_validity(file, fatality: bool = False):
    file = Path(file)
    if os.path.exists(file):
        return file.resolve()
    else:
        if (fatality):
            fatal(f"Missing file \"{file}\"")


def array_blacklist(array:list, blacklist:list):
    return [x for x in array if not any(b in x for b in blacklist)]


def cut_string(s: str, marker: str, half: int = 0):
    if marker in s:
        return s.split(marker)[half]
    return s