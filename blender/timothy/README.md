# Timothy — Blender 3D model

A procedural, fully modeled 3D interpretation of the supplied Timothy reference. The silhouette, face, clothing and footwear are approximate; this is an editable first modeling pass, not a sculpted replica of the rendered reference. Facial expressions and individually articulated fingers are not included.

## Deliverables

- `timothy.blend`: editable Blender 5.2.2 project, studio lighting, camera, materials, 18-bone armature, weighted character geometry and five actions.
- `timothy.glb`: glTF 2.0 binary export with one skin and the five animation clips. About 6 MB.
- `renders/`: front, three-quarter and back studio renders.
- `viewer.html`: interactive 3D preview, animation selector and Lenis + GSAP scroll control. All runtime scripts are included in `vendor/`.
- `build_timothy.py`: reproducible model builder; uses Blender's Python API and the Python standard library.
- `verify_timothy.py`, `verification.json`: neutral saved pose, manifold sleeve/leg geometry, 25 sampled deformation poses, and GLB skin/clip checks.
- `reference-timothy.png`: supplied pose/reference sheet.

## Open in Blender

Open `timothy.blend`. The file opens with a neutral pose and a studio camera. Select `Timothy_Rig` for pose controls.

The actions are `Idle`, `Run`, `Wave`, `Jump`, `Celebrate`. In the NLA editor all tracks are muted in the saved neutral scene. Unmute only the action track you want to preview, keep the others muted, and play frames 1–61 (Run: 1–31). The named actions are also available in the Action Editor. Save a copy before changing the studio setup.

Sleeves and trouser legs are continuous closed meshes with blended weights across elbows/knees. The face, hat, headphones and embroidery are separate modeled accessories attached to the head/chest bones. The companion orb uses real fur geometry and its own bone. Studio cameras/lights/ground are excluded from the GLB.

## View in a browser

From this folder:

```sh
python3 -m http.server 8080
```

Open http://localhost:8080/viewer.html. Scroll rotates the camera around the model and scrubs the selected animation. Turn scroll off to play the animation normally. Drag to orbit. The model also loads with Three.js GLTFLoader and its animation clips can be scrubbed by a GSAP ScrollTrigger timeline.

## Rebuild

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python build_timothy.py
```

The builder writes the blend, GLB and renders beside itself. Rendering uses Cycles CPU at 40 samples. The Blender knit material uses procedural noise bump; that procedural detail is not baked into the GLB, which keeps the base material colors and modeled knit ribs. Further optimization, texture baking, sculpting and facial rigging are separate production steps.

The included model-viewer distribution comes from Google's published model-viewer 4.1.0 build, and GSAP/Lenis distributions retain their license headers. The asset is an editable starting point for the requested scroll-driven character.
