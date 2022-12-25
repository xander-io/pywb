from os import environ, path, walk
from random import randint

from pywb import ENVIRON_DEBUG_KEY, VERSION


def read_ascii():
    ascii_path = generate_ascii_path()

    with open(ascii_path, "r", encoding="utf-8") as f:
        ascii = f.read()
    return ascii


def generate_ascii_path():
    ascii_folder = path.join(path.dirname(__file__), "banners")
    # Get filenames from ascii path
    fnames = next(walk(ascii_folder))[2]
    fname = fnames[randint(0, len(fnames) - 1)]
    # Exclude any python files
    while (path.splitext(fname)[1] == ".py"):
        fname = fnames[randint(0, len(fnames) - 1)]
    return path.join(ascii_folder, fname)


def generate_ascii_art():
    return (read_ascii() + "\n\n---%s") % (VERSION, ("\n" + "[DEBUG]"*13) if ENVIRON_DEBUG_KEY in environ else "")
