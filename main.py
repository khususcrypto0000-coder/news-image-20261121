#!/usr/bin/env python3
"""Entry program for the make.fun bounty
"Sum up 21 November's world news in one image" (news-image-20261121).

The finished front page already ships in this repository as
output/entry.png (1024x1024 PNG, drawn earlier by a deterministic
program). This program only copies that file to the grader's output
directory, /output/entry.png.

It uses the Python standard library only -- no Pillow, no network,
no clock, no randomness -- because the grader runs main.py in a
fresh container with nothing installed beyond the standard library.
Running it twice produces a byte-identical output file.

Usage:
    python3 main.py

The output directory defaults to /output; set MAKEFUN_OUTPUT_DIR to
override it when testing locally, for example:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys

# The finished image, shipped beside this file.
SOURCE_NAME = "entry.png"

# Where the grader expects the image. MAKEFUN_OUTPUT_DIR is only a
# local-testing override; the grader itself always uses /output.
DEFAULT_OUTPUT_DIR = "/output"


def output_dir():
    """Return the directory the image must be written to."""
    override = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if override:
        return override
    return DEFAULT_OUTPUT_DIR


def copy_entry(source, destination):
    """Copy `source` to `destination`, creating folders as needed.

    Returns True when the copy landed and its size matches the
    source; False when anything about the write failed.
    """
    try:
        folder = os.path.dirname(destination)
        if folder:
            os.makedirs(folder, exist_ok=True)
        shutil.copyfile(source, destination)
    except OSError as err:
        print("could not write {}: {}".format(destination, err))
        return False
    try:
        if os.path.getsize(destination) != os.path.getsize(source):
            print("size mismatch after writing {}".format(destination))
            return False
    except OSError as err:
        print("could not verify {}: {}".format(destination, err))
        return False
    print("wrote {} ({} bytes)".format(
        destination, os.path.getsize(destination)))
    return True


def main():
    """Copy the bundled entry.png to the grader's output directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "output", SOURCE_NAME)
    if not os.path.isfile(source):
        print("missing source image: {}".format(source), file=sys.stderr)
        return 1

    targets = [
        os.path.join(output_dir(), SOURCE_NAME),
        os.path.join(here, "output", SOURCE_NAME),
    ]

    written = False
    for target in targets:
        # The second target is the source itself when this runs from
        # the repository: copying a file onto itself is pointless,
        # so skip it instead of reporting a spurious failure.
        try:
            if os.path.samefile(target, source):
                print("skipping {} (already the source)".format(target))
                continue
        except OSError:
            pass
        if copy_entry(source, target):
            written = True

    if not written:
        print("failed to write entry.png to any target",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
