# Naver SmartEditor helpers

Scripts for posting the drafts in `marketing/naver/` through Naver's SmartEditor with `orca computer`, in a Chrome window of our own. They used to live only in a session scratchpad. macOS deleted them along with other old files in `/private/tmp` (2026-10-27), so they are kept here now.

- `chunk.py <draft.html> <dir>`: splits a draft at each `<!--IMG:…-->` mark into `cN.html` and `cN.txt` paste chunks, and copies `setclip.js` into the folder.
- `post.sh <win> <dir> <title> <small-img|-> <img1> [img2 …]`: types the title, then for each image uploads it with the editor's 사진 button (`img.sh`) and pastes the matching chunk as rich text (`setclip.js`). With a small-img name, `small.sh` sets that image to 작게 and centres it.
- `finish11.sh <win> <day> <tag…>`: opens the 발행 panel, adds the tags (`tag1.py` stops on the first one that fails), schedules November `<day>` at 08:00 (`sched11.sh`), checks the panel, and then publishes. Pass tags as literal words. zsh does not split an unquoted `$TAGS`.
- `k.sh <win> <action…>`: brings the window back, checks that Chrome is frontmost, and only then sends the action. `c.py` runs one action and prints the matching lines of the accessibility tree. `nav.py` sets the address bar.

Coordinates assume the editor window size used so far. The full step-by-step and the pitfalls are in HANDOFF.md (2-28 to 2-31).
