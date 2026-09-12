from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
for name in ['ground_truth_physics.json','academic_citations.json','milestone_history.json','validation.json','web_export.json','engine-rebuild.json']:
 (R/'public/data').mkdir(exist_ok=True);shutil.copy2(R/'data'/name,R/'public/data'/name)
(R/'public/docs').mkdir(exist_ok=True);shutil.copy2(R/'docs/technical-notes.md',R/'public/docs/technical-notes.md')
assets=[p for p in (R/'public').rglob('*') if p.is_file()]
manifest={'deployment':{'status':'GitHub Pages configured','url':'https://jungluchen.github.io/f1-power-unit-showcase/'},'assets':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(assets)],'total_public_bytes':sum(p.stat().st_size for p in assets),'limits':{'GLB_bytes':10000000,'texture_max_dimension':2048,'public_payload_bytes':60000000}}
assert (R/'public/assets/models/f1-power-unit.glb').stat().st_size<10000000 and manifest['total_public_bytes']<60000000
(R/'data/artifact_manifest.json').write_text(json.dumps(manifest,indent=2));print('Packaged',manifest['total_public_bytes'],'public bytes')
