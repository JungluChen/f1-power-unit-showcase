import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/detailed-power-unit.blend'))
s=bpy.context.scene;G={n:bpy.data.objects[n] for n in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']}
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
states=[{}, {'COVER':(0,0,1)}, {}, {'MGUH':(.15,-.65,.5)}, {'MGUH':(.15,.5,.5),'MGUK':(0,-.65,.35)}, {'MGUH':(.2,.5,.5),'MGUK':(0,.5,.25),'ES':(-.15,-.5,.5)}]
for i,state in enumerate(states):
 for name,g in G.items():
  g.location=state.get(name,(0,0,0))
  for o in g.children_recursive:o.hide_render=(i>=2 and name in ['CHASSIS','COVER']) or (i==0 and name not in ['CHASSIS','COVER'])
 for o in bpy.data.objects['MOVING_CORE'].children_recursive:o.hide_render=True
 target=Vector((0,0,.35)) if i<2 else Vector((.35,0,.6));s.camera.location=target+Vector((-5,-7,4));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=7 if i<2 else 3.1
 s.render.filepath=str(R/f'public/assets/textures/plate-{i}.png');bpy.ops.render.render(write_still=True)
