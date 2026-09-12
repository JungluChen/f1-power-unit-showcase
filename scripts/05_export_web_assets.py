import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
assert json.loads((R/'data/validation.json').read_text())['status']=='passed'
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if not o.name.startswith('proxy_') and (o.type=='MESH' or o.name in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']):o.select_set(True)
p=R/'public/assets/models/f1-power-unit.glb'
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=14,export_draco_normal_quantization=10,export_yup=True)
meshes=[o for o in bpy.context.selected_objects if o.type=='MESH'];report={'coordinates':'Blender x,y,z -> glTF x,z,-y','Draco':{'level':6,'position_bits':14,'normal_bits':10},'model_bytes':p.stat().st_size,'vertices':sum(len(o.data.vertices) for o in meshes),'draw_calls_estimate':sum(len(o.data.materials) for o in meshes),'textures':'none; procedural material colors','provenance':'original procedural schematic; user request authorizes generated project assets'}
(R/'data/web_export.json').write_text(json.dumps(report,indent=2));print(report)
from mathutils import Vector
s=bpy.context.scene
states=[{}, {'COVER':(0,0,1.2)}, {'COVER':(0,0,2.3),'CHASSIS':(-1,0,-1.2)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,-.65,.5)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,.5,.5),'MGUK':(0,-.65,.35)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.2,.5,.5),'MGUK':(0,.5,.25),'ES':(-.15,-.5,.5)}]
for i,state in enumerate(states):
 for name in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']:
  o=bpy.data.objects[name];o.location=state.get(name,(0,0,0))
  for ch in o.children:
   if not ch.name.startswith('proxy_'):ch.hide_render=i>=2 and name in ['CHASSIS','COVER']
 target=Vector((0,0,.45)) if i<2 else Vector((.6,0,.55));s.camera.location=target+Vector((-4,-6,3.5));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=6.5 if i<2 else 2.8
 s.render.filepath=str(R/f'public/assets/textures/plate-{i}.png');bpy.ops.render.render(write_still=True)
