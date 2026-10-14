# Buddy character kit — instructions for Claude

This file is project guidance for a coding assistant. The human user's current instructions take precedence.

## What this folder provides

A rendered 2D puppet generated from the original purple mascot reference. The visible artwork is raster imagery with cloth textures and soft 3D shading, not flat vector drawings. The companion orb uses generated fuzzy purple artwork with a turquoise face, rather than a CSS sphere. Limb images are calibrated with similarity transforms: BOTH source joint centers map exactly to the parent and child pivots in the rig. See `sourceAnchors` and `regions[*].matrix` in manifest.json. Do not change crop placements, scale, or pivots independently; recompute the transform from the two anchor pairs. New motions use code and these existing assets; no per-motion image generation is needed.

## Files

- `raster-parts/*.svg`: 16 independent transparent component assets. Each SVG wraps an embedded PNG and a crop viewport. Individual Site downloads embed their source PNG; in the compact ZIP the wrappers share closed-atlas.png and torso.png through relative paths, so keep the folder together. These are raster assets in SVG containers; you can animate them, but cannot edit their cloth texture or face by changing vector paths.
- `closed-atlas.png`: repaired head/limb/shoe/orb atlas. All limb ends are closed cloth rather than hollow socket artwork. Preserve the overlap beyond joint centers.
- `torso.png`: separately generated hoodie torso with a visible skin neck and trouser waist. A torso clip mask hides fixed sleeve stubs when arms rotate.
- `character.svg`: assembled rig containing nested SVG viewports of the source images. Its artboard is `0 0 320 480`.
- `manifest.json`: joint pivots, atlas regions, and placements. Individual component viewboxes use their own source pixel rectangles; do not assume the old vector kit's shared coordinates.
- `character.js`: `mountBuddy(element)`, `setPose`, `poseAt`, `showJoints`, `showParts`. Native joint transforms carry child assets.
- `motions.js`: deterministic pose functions for idle, run, walk, wave, jump, point, dance. `handOpen: true` switches to the open-hand asset. The preview includes a Pose time slider to inspect fixed times without playback.
- `demo.js`, `index.html`: preview and Lenis + GSAP scroll example.
- `vendor/`: included GSAP 3.13.0, ScrollTrigger, Lenis 1.3.11; preserve their upstream license headers.

The head, hair, hat, face, and headphones stay together in one rendered asset to preserve their appearance. This is a 2D puppet using rendered images, not a rigged 3D model. The authored poses were checked with closed overlap at joints. New extreme poses still need visual checking, and turning around or changing camera angle needs more artwork. Do not claim it provides animation quality identical to a finished 3D film.

## Run locally

Serve the folder over HTTP, since modules and the rig loader use fetch. Opening the HTML via `file://` will fail.

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080/`. You can use an existing project's dev server instead. The demo's Google Fonts import is optional; system fonts are the fallback. Runtime JavaScript and artwork are local.

## Animate

```js
import { mountBuddy } from './character.js';
const buddy = await mountBuddy(document.querySelector('#buddy'));

buddy.poseAt('run', seconds);
buddy.poseAt('wave', seconds);
buddy.setPose({ 'arm-right': -140, 'elbow-right': -20, head: -6 });
```

The host element needs width and height, for example `width:240px; height:360px`. The SVG scales proportionally and can overflow when a limb stretches.

`setPose` resets every unspecified joint to neutral. Angles are degrees clockwise. `x` and `y` translate the root in artboard units. `orbX`, `orbY`, and `orb` move or rotate the companion orb. Nested transforms carry child joints; do not flatten the hierarchy or independently place hands in screen coordinates.

Joint names:

```
root, body, head, orb
arm-left, elbow-left, wrist-left
arm-right, elbow-right, wrist-right
leg-left, knee-left, ankle-left
leg-right, knee-right, ankle-right
```

The body and head pivot at `(160,300)` and `(160,185)`. Legs belong to the root hips; arms belong to the body; head parts belong to the head. Left/right refer to the screen sides in the neutral illustration. Assets have generous overlapping joint edges.

## Add an action

Add a new branch in `poseAt` and add its name to `motionNames`. Compute every angle from the input time rather than adding to an existing transform. Keep poses deterministic so seeking and scrolling backward work. Use a paused GSAP timeline or a proxy value as a clock. For looping actions, sine/cosine functions are useful; for a single action, clamp normalized time. `jump` is a one-second action. The preview replays it on each click.

Example:

```js
if (name === 'celebrate') {
  const wave = Math.sin(seconds * Math.PI * 4);
  p['arm-left'] = 140;
  p['arm-right'] = -140;
  p['elbow-left'] = wave * 15;
  p['elbow-right'] = -wave * 15;
  p.y = -Math.abs(wave) * 8;
}
```

Use CSS transforms on the outer host for screen placement, scaling, or mirroring. Joint transforms remain within the SVG. Avoid setting transforms on a parent with two separate animation systems.

## Scroll example

`demo.js` includes Lenis synchronized with `gsap.ticker`, `ScrollTrigger.update`, and a pinned GSAP scrub timeline. The timeline moves a proxy from 0 to 1; its update callback derives the pose and horizontal placement from that value. Scroll back reverses the action. Respect `prefers-reduced-motion` by using static poses. Preserve keyboard controls, accessible labels, and resize refresh behavior.

## Verification

Serve locally, test run, wave, single jump, point, pause, speed, joint display, exploded parts, download, and scroll forward/backward. Inspect browser errors and both narrow/wide layouts. Check hand/elbow and shin/ankle attachment while rotated. Do not claim the vector kit looks identical to the rendered reference or provides all camera angles.

## Suggested user prompt

“Use the existing Buddy character kit and read CLAUDE.md. Add a [describe action] animation by changing the rig's joint angles. Keep the rendered parts and hierarchy, and do not call image/video generation APIs. Connect the character to my site's scroll using Lenis and a deterministic GSAP ScrollTrigger timeline. Show me the working result.”
