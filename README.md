# Scroll Buddy

Complete website and rendered character kit, including the original scroll demo and repaired revision 4 rig.

## Run locally

No installation or build step is required. From this repository, run:

```sh
python3 -m http.server 8080 --directory dist
```

Open:
- http://localhost:8080/ — original sprite animation with Lenis + GSAP
- http://localhost:8080/character-kit/ — rendered component rig, 7 actions, pause/speed/pose controls
- http://localhost:8080/character-kit/rig-check.html — fixed poses for visual inspection

Use an HTTP server; file:// does not support the module/fetch loading used by the rig. Google Fonts are optional and have system font fallbacks. Runtime JS and character images are included locally.

## Files

- `dist/index.html`, `app.js`, `style.css`: original scroll website.
- `dist/assets/`: original generated sprite sheet, GSAP, ScrollTrigger and Lenis.
- `dist/character-kit/`: revision 4 rig and standalone downloadable kit.
- `dist/character-kit/raster-parts/`: 16 rendered component assets in SVG image wrappers.
- `dist/character-kit/closed-atlas.png`, `torso.png`: current source artwork.
- `dist/character-kit/manifest.json`: crop rectangles, joint pivots and calibrated transforms.
- `dist/character-kit/character.js`, `motions.js`: rig loader/controller and deterministic movements.
- `dist/character-kit/CLAUDE.md`: instructions for Claude to add animations and reuse the character.
- `build-raster-rig.py`: rebuilds the revision 4 rig from the source artwork, using Python's standard library. Running it recalibrates all limb endpoint pairs and rewrites the rig, manifest and independent SVG parts. It does not regenerate the downloadable ZIP.
- `references/original-mascot.jpeg`: supplied character reference.

The earlier `dist/character-kit/parts/` vector assets and `atlas.png` with unfinished sockets are historical source assets. They are retained for completeness but the current demo does not use them. Use `raster-parts/` and `closed-atlas.png` for animation work.

## Claude prompt

“Read dist/character-kit/CLAUDE.md. Use the current rendered rig, preserve the artwork and joint overlap, and add [describe movement]. Connect the movement to a deterministic Lenis + GSAP scroll timeline so scrolling backward works.”

## Validation

Revision 4 closed the hollow cloth ends and calibrated source image anchors to shoulder/elbow/wrist and hip/knee/ankle pivots. All seven actions were inspected at fixed phases. Loop/landing checks, SVG references, mobile layout and forward/reverse scroll were verified. This is a 2D rig using rendered images, not a rigged 3D model; new extreme poses should be checked visually.

Vendor distributions retain their upstream license headers. Character imagery was generated using ImageGen with the supplied mascot reference. Asset prompts and instructions are recorded in the character kit README and CLAUDE.md.
