import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'source-assets/rb19-original.glb'))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'min':[min(p[k] for p in pts) for k in range(3)],'max':[max(p[k] for p in pts) for k in range(3)],'materials':[m.name for m in o.data.materials]})
(R/'reports/import-inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
print('IMAGES',[(x.name,list(x.size)) for x in bpy.data.images])
