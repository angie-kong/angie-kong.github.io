#!/usr/bin/env python3
"""
Scans images/gallery/ for photo files and updates images/gallery/photos.json.

- Existing entries in photos.json (order + captions) are left untouched.
- Any new image files found in the folder that aren't already in photos.json
  get appended at the end, sorted by capture date (newest first among the
  new ones), with a blank caption for you to fill in.
- Any entries in photos.json whose file no longer exists in the folder are
  dropped, with a warning printed.

Run this after dragging new photos into images/gallery/, then reorder or
add captions by hand-editing photos.json (no need to touch gallery.html).

Usage:
    python3 generate_gallery.py
    (needs Pillow: pip install Pillow --break-system-packages)
"""

import glob
import json
import os

GALLERY_DIR = os.path.join("images", "gallery")
JSON_PATH = os.path.join(GALLERY_DIR, "photos.json")
EXTENSIONS = ("*.jpg", "*.jpeg", "*.png", "*.webp")


def get_capture_date(path):
    try:
        from PIL import Image, ExifTags
        img = Image.open(path)
        exif = img._getexif()
        if exif:
            for tag_id, val in exif.items():
                if ExifTags.TAGS.get(tag_id) == "DateTimeOriginal":
                    return val
    except Exception:
        pass
    # Fall back to file modified time if there's no EXIF date.
    return None


def main():
    if not os.path.isdir(GALLERY_DIR):
        print(f"Folder not found: {GALLERY_DIR}")
        return

    found_files = set()
    for pattern in EXTENSIONS:
        found_files.update(os.path.basename(f) for f in glob.glob(os.path.join(GALLERY_DIR, pattern)))
        found_files.update(os.path.basename(f) for f in glob.glob(os.path.join(GALLERY_DIR, pattern.upper())))

    existing = []
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH) as f:
            existing = json.load(f)

    existing_filenames = {os.path.basename(item["src"]) for item in existing}

    # Drop entries whose file was deleted from the folder.
    kept = []
    for item in existing:
        fname = os.path.basename(item["src"])
        if fname in found_files:
            kept.append(item)
        else:
            print(f"Removing missing file from photos.json: {fname}")

    # Add new files not yet in photos.json.
    new_filenames = sorted(found_files - existing_filenames)
    new_items = []
    for fname in new_filenames:
        path = os.path.join(GALLERY_DIR, fname)
        new_items.append({
            "src": f"images/gallery/{fname}",
            "alt": "",
            "date": get_capture_date(path),
        })
    new_items.sort(key=lambda x: x["date"] or "", reverse=True)

    if new_items:
        print(f"Adding {len(new_items)} new photo(s):")
        for item in new_items:
            print(f"  {item['src']}")
    else:
        print("No new photos found.")

    result = kept + new_items
    with open(JSON_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"photos.json now has {len(result)} entries.")


if __name__ == "__main__":
    main()
