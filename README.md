# Inside the Formula 1 Power Unit

A six-chapter Vite / Three.js / GSAP scrollytelling exhibit for the **2014–2025 hybrid architecture**, with a detailed licensed RB19 exterior and educational internal model, sourced technical notes, independent energy ledger, and a narrated two-minute film.

## Run locally

```sh
npm ci
npm run dev
```

For the production build: `npm run build`, then `npm run preview`. The project uses relative asset paths and can be served from a GitHub Pages repository subpath. Do not open `dist/index.html` directly with a file URL.

## Deliverables

- `blender/detailed-power-unit.blend`: detailed textured RB19 assembly and studio setup.
- `public/assets/models/f1-power-unit.glb`: Draco-compressed six-subsystem model.
- `public/assets/video/f1-power-unit-master.mp4`: 120-second narrated film with English captions.
- `data/`: sourced facts, academic citation, milestones, solver cache, validation and frame/audio CSV.
- `docs/technical-notes.md`: source attribution, mechanisms, assumptions and implementation.
- `reports/`: model, media, browser and package verification.
- `.github/workflows/deploy.yml`: GitHub Pages workflow, ready for an authorized deployment.

## Reproduce the package

Use Python 3 with NumPy and Pillow, Blender 5.2+, FFmpeg with libx264, and macOS `say` with the generic Samantha voice. Set `FFMPEG` to the FFmpeg executable on your system. If unavailable, the renderer's fallback path refers to the existing sibling workspace dependency. Web build dependencies are pinned by the lockfile.

```sh
python3 scripts/build_research.py
python3 scripts/03_bake_and_verify.py
python3 scripts/14_engine_materials.py
blender --background --python scripts/15_build_engine.py
blender --background --python scripts/16_render_engine_plates.py
FFMPEG=/path/to/ffmpeg python3 scripts/06_render_film.py
FFMPEG=/path/to/ffmpeg python3 scripts/08_verify_media.py
python3 scripts/09_package.py
npm run build
npm run preview
# Optional browser QA: set PLAYWRIGHT_MODULE to your Playwright index.mjs
PREVIEW_URL=http://127.0.0.1:4173/ node scripts/07_verify_web.mjs
```

Research, energy, media and web gates must pass before publication. Film narration is system-generated, not a human recording. Visual disassembly is editorial; no rigid-body explosion, validated lap model, thermal simulation or exact team CAD is claimed. See the technical notes for the deliberately limited collision checks.

GitHub Pages deployment uses the included Actions workflow. The default page opens the latest RB19-to-RA166E scroll exhibit; `?engine=hybrid` opens the earlier hybrid study.

## Exterior model credit

Oracle Red Bull F1 Car RB19 2023 by Redgrund, CC BY 4.0. See `source-assets/ATTRIBUTION.md` for the original source, license, distribution mirror and changes. The detailed exterior replaces the first procedural car. The supplied `archive-v1/power-unit.blend` is used only as the source of educational internal components. The exterior is an artistic model of a real car, not official 1:1 CAD.

The latest engine reconstruction uses Honda’s published RA621H views. Chapter 02 offers an opaque Assembled view and a close-up Cutaway with six articulated pistons, Run/Pause, and demonstration speed control. The approved exterior input is preserved in `archive-v2/`. See `data/engine-rebuild.json` for its reference and dimensional assumptions.

## RA166E photograph study

Open `?engine=ra166e` for the requested 1986 Honda reconstruction with assembled/cutaway motion. Edit `blender/ra166e-reference.blend` or rebuild with `scripts/17_build_ra166e.py`. It is separate from the modern hybrid exhibit and its film.

The GitHub repository includes the runnable website, compressed models, rendered assets, research records and build scripts. Large Blender editing archives and the user-supplied reference photograph remain in the local project package.
