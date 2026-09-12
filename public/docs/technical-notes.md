# Formula 1 power unit: technical notes

This independent educational model depicts the 2014–2025 hybrid architecture, using the FIA 2025 Issue 1 rules as the quantitative reference. It is not a team replica, homologation model, digital twin, or service procedure. The unrelated Streamlit/protein-viewer entries in the supplied concept were omitted in favor of its requested standalone Vite/Three.js experience.

## Architecture and evidence

The [FIA 2025 regulations](https://www.fia.com/sites/default/files/fia_2025_formula_1_technical_regulations_-_issue_01_-_2024-12-11_1.pdf), Article 5.2, specify a 1.6 L, 90-degree V6. Article 5.3.3 specifies 120 kW maximum MGU-K power and its mechanical connection upstream of the main clutch. Article 5.3.2 contains the energy-flow diagram: 2 MJ/lap on the K-to-store route and 4 MJ/lap on the store-to-K route. Direct H-to-K electrical flow is separate. These are not interchangeable limits on total recovery or total assistance time.

The MGU-H recovers mechanical shaft work extracted from exhaust gas by the turbine. In motor mode it can accelerate the compressor; it does not turn heat directly into electricity or guarantee instantaneous boost. The rebuilt model uses a front compressor, central MGU-H and rear turbine following Honda’s published split-turbo architecture.

[Mercedes reports](https://www.mercedesamgf1.com/team/location/brixworth) thermal efficiency above 50%. No team-independent horsepower, efficiency map, materials bill, or comparison with all road cars is inferred. Direct injection and high-temperature exhaust materials matter, but specific proprietary combustion strategies and alloy choices are not simulated.

For [2026](https://www.fia.com/news/new-era-competition-fia-showcases-future-focused-formula-1-regulations-2026-and-beyond), the MGU-H was removed and maximum MGU-K power increased to 350 kW. The exhibit is therefore explicitly historical.

## Geometry, constraints, and motion

The independently authored internal components are expressed in metres, with +Z up and +X along the vehicle. glTF converts coordinates as (x,y,z) → (x,z,-y), making +Y up. Six named parent groups form the articulated scene: CHASSIS, COVER, ICE, MGUH, MGUK, ES. Rigid child-parent transforms express assembly constraints. Piston and rod transforms use an analytic slider-crank constraint, not rigid-body dynamics. Rod length is 0.110 m and crank radius is 0.0265 m; these are display assumptions, not manufacturer dimensions.

Visible meshes and hidden 6 cm collision reference cores are separate. The cores have 9 cm initial separation and provide a deliberately limited nonpenetration check. This does not establish clearance for the complete visual housings; intended intersections at assembly interfaces remain. Gravity and illustrative mass properties are recorded for provenance but do not drive the reveal. Quintic smoothstep supplies zero endpoint speed and acceleration; this is editorial settling, not physical impact settling.

The web uses GSAP ScrollTrigger to interpolate six states. Bodywork lifts and disappears, The enclosed engine remains fully surfaced while electrical components separate. Assembled and Cutaway controls expose an articulated six-piston mechanism; Run/Pause and a 15–120 rpm demonstration slider control its motion. KaTeX typesets the formulas and a Canvas HUD projects component callouts. Orbit and reset controls change the view independently of scroll. Reduced motion snaps component states. If WebGL or asset loading fails, rendered plates and all text remain available.

## Independent energy ledger

A deterministic 120 Hz integration uses three identical 40 s illustrative cycles. Each has 5 s of 100 kW K-shaft recovery, 10 s of 30 kW H electrical input, 10 s of 100 kW K-shaft deployment, and 15 s idle. Constant K efficiency is an assumed 0.95, not an experimentally calibrated map. H power is already measured at the electrical boundary; no turbine efficiency is inferred.

With positive K power denoting propulsion:

`dE/dt = 0.95 max(-P_K,0) + P_H - max(P_K,0)/0.95`

The independent energy residual checks `E - E_initial + integrated_K_shaft + losses - integrated_H_electrical = 0`. Charge starts at 2 MJ. The ledger checks finite values, a 0–4 MJ illustrative storage window, route totals, and accounting residual. No combustion, temperature, tire, battery cell, or optimized lap dynamics are modeled. `data/solver_cache.json` records the 30 Hz film samples; the integration runs at 120 Hz. It is not a reproduction of Limebeer, Perantoni and Rao's optimal-control study.

## Film

The 1280×720 H.264/AAC master has 3,600 frames at 30 fps, lasting 120 seconds. Six Blender-rendered studio plates receive an editorial camera push and per-frame ledger overlays. This is not 3,600 continuously rendered Blender simulation frames. The saved Blender scene includes six camera markers, shutter 0.25, and motion blur enabled; the static plate compositor itself does not create physically based motion blur. Generic macOS Samantha provides system-generated narration. No Foley or field recordings are present. English WebVTT captions and the complete transcript accompany the film. CSV timecodes map every frame, narration cue, ledger time, and editorial distinction.

## Payload and deployment

The Draco export uses level 6, 16-bit position and 10-bit normal quantization. The RB19 GLB retains three 1024×1024 PBR texture maps. Replacement studio plates are 1600×1000. Runtime vertex counts can exceed Blender mesh counts due to normal and UV splits; actual browser measurements are in `reports/web-validation.json`. The initial model loads eagerly; video uses metadata preload. Film and fallback images are separate payloads.

GitHub Pages publication was requested. The included workflow publishes the Vite production build. When publication is requested, authenticate `gh`, inspect the destination repository, configure Pages workflow mode, push, monitor the exact run, and verify the live URL and assets before claiming deployment.

## Detailed exterior revision

The first procedural car exterior has been replaced with **Oracle Red Bull F1 Car RB19 2023** by **Redgrund**, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Original model](https://sketchfab.com/3d-models/oracle-red-bull-f1-car-rb19-2023-e4afe46f3aab4b23a418da06fc163821). The model's embedded glTF metadata confirms author, source and license. `source-assets/ATTRIBUTION.md` records the distribution mirror and modifications; `data/web_export.json` records the original SHA-256.

The artistic exterior has been normalized uniformly to a 2.0 m display width. It is not official team CAD or certified 1:1 engineering geometry. The aft shell is a geometric partition for the editorial reveal, not a verified set of actual removable service panels. The power-unit internals remain independently authored educational geometry, with added fasteners, injector wiring and HV cable detail. They are hidden in the assembled opening so they do not protrude through the accurate exterior.

The earlier exterior revision used: the export is approximately 4 MB, with about 432,000 Blender vertices, three 1024×1024 PBR maps, 16-bit Draco position quantization and 1600×1000 studio plates. The web retains source livery, neutral studio lighting and a receiving shadow plane. Exact runtime metrics are reported separately. Rebuild with `blender --background --python scripts/11_rebuild_real_car.py` after generating the archived educational internals. The original small procedural model is retained only in `archive-v1/` for reproducibility.


## Detailed engine revision

The current `blender/detailed-power-unit.blend` and GLB replace the primitive internals with an original reconstruction informed by [Honda RA621H photographs](https://global.honda/en/POWEREDbyHONDA/2021_ra621h/) and [Honda’s architecture article](https://global.honda/en/tech/motorsports/Formula-1/Powertrain_V6_power_unit/). It includes enclosed crankcase and cylinder heads, carbon plenums, insulated exhaust runners, split turbo hardware, wiring, fasteners, MGU-K and sealed energy store. Honda images are references only and are not redistributed. This is not exact RB19 engine CAD.

Assembled mode hides the mechanism inside opaque housings. Cutaway removes the heads, intake and exhaust to show six pistons and connecting rods. The slider-crank equation is `s = r cos(a) + sqrt(L² - r² sin²(a))`, projected into each 45-degree bank. Demonstration phasing is illustrative, not a Honda firing-order claim. The browser verification checks six pistons, changing crank angle, and connecting-rod length closure to 1e-10 m. It does not validate combustion or full visual collision clearance.

Rebuild in order: `scripts/14_engine_materials.py`, Blender `scripts/15_build_engine.py`, Blender `scripts/16_render_engine_plates.py`, then the film and packaging scripts. The approved exterior scene used as input is preserved in `archive-v2/`. Current model and geometry counts are in `data/engine-rebuild.json`; browser performance is in `reports/web-validation.json`.


## Honda RA166E photographic study

Open `?engine=ra166e` for the separate 1986 engine study, reconstructed from the user-supplied photograph. Its black cast cam covers, broad intake, exposed polished exhausts, twin turbos, clutch and accessory plumbing are original model geometry. It has no MGU-H, MGU-K or energy store. Honda specifies 80 degrees, 1,494 cm³, 79 mm bore and 50.8 mm stroke. Browser kinematics use that bank angle and stroke, with an assumed 110 mm rod length. Hidden geometry, installation envelope and firing phasing remain illustrative. The RB19/hybrid exhibit remains separately accessible.

Editable source: `blender/ra166e-reference.blend`. Rebuild: Blender `scripts/17_build_ra166e.py`; validate: `scripts/18_verify_ra166e.mjs`. The supplied reference image is retained under source-assets for local reproduction, not served publicly.

The RA166E view now retains the RB19 car opening and six-stage GSAP scrollytelling: complete car, cover lift, engine, intake lift, exhaust/turbo separation, and moving core. Its historical distinction is displayed in the reveal chapter. `scripts/19_verify_reference_scroll.mjs` verifies all six chapters and responsive controls.


## Reconstructed moving core

The reference-engine cutaway now uses interrupted main journals, three offset crankpins, asymmetric counterweights and pairs of axially staggered rods. Each rod includes a big-end bearing, split cap and bolts, H-section shank, small-end bushing and hollow wrist pin. Hollow pistons have skirt reliefs, a separate ring pack and shallow valve pockets. Piston feature references: MAHLE forged piston features (https://www.us.mahle.com/en/motorsports/forged-pistons-features-and-benefits/) and ProSeries pistons (https://www.us.mahle.com/en/motorsports/proseries-pistons/). These inform generic mechanical detail, not proprietary RA166E internals. Rod length, journal sizes, crown shape, counterweight contours and crank phasing remain reconstruction assumptions.

Browser validation compares exported crankpin markers to rod big-end positions, and transformed small ends to piston wrist-pin origins over more than a complete revolution, with a 1 micrometre numerical closure threshold. This tests articulated joint alignment, not dynamic stresses, lubrication, combustion or complete collision clearance.
