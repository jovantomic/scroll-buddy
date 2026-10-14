# Buddy rendered character kit

16 transparent component assets made with ImageGen from the original reference, a joint rig, seven animations, and a Lenis + GSAP scroll example. Includes the textured 3D-style head, hoodie, limbs, shoes, and fuzzy purple orb.

Give Claude the whole folder and ask it to read CLAUDE.md. Add movements by changing joint angles; no new image/video generation is needed for each action.

Serve over HTTP with `python3 -m http.server 8080`, then open http://localhost:8080/. Opening index.html via file:// will not load JavaScript modules.

Source artwork: closed-atlas.png and torso.png. Independent assets: raster-parts/*.svg (embedded raster images in SVG containers). Rig: character.svg and manifest.json. Animations: motions.js. Loader: character.js.

This replaces the earlier vector approximation. These are rendered 2D parts, not a 3D model. Extreme poses can show layer seams. Head details are grouped to keep their appearance consistent.

Suggested prompt: “Read CLAUDE.md. Make this buddy run with scroll, stop to wave at section two, and jump over the next heading. Keep the rendered artwork and use Lenis + a deterministic GSAP timeline.”

ImageGen prompts: (1) generate a transparent 4×4 atlas preserving the original purple boy’s rendered face, knit texture, headphones, cyan hoodie details, sneakers, and original fuzzy purple/cyan orb; isolate head, torso, limb segments, hands and shoes. (2) generate an isolated matching hoodie torso with a skin neck, filled shoulders, and trouser waist. Assets were generated using the built-in ImageGen tool. Atlas cropping uses SVG viewports without resampling the original pixels.

Revision 4: closed cloth ends, calibrated two-anchor placement at every articulated joint, child-over-parent overlaps, revised motion curves, and a pose inspection slider. All 7 actions checked at fixed phases, plus responsive preview and reverse scroll.
ImageGen repair prompt: replace all limb sockets and rimmed openings with closed rounded cloth ends, keep the atlas layout and face/orb unchanged.
