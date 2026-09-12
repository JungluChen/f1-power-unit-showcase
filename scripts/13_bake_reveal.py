"""Bake the six editorial reveal states into the editable Blender project."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/rb19-exhibit.blend'))
s=bpy.context.scene
states=[{}, {'COVER':(0,0,1.0)}, {'COVER':(0,0,2.3),'CHASSIS':(-1,0,-1.2)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,-.65,.5)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,.5,.5),'MGUK':(0,-.65,.35)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.2,.5,.5),'MGUK':(0,.5,.25),'ES':(-.15,-.5,.5)}]
for i,state in enumerate(states):
 frame=i*600+1
 for name in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']:
  g=bpy.data.objects[name];g.location=state.get(name,(0,0,0));g.keyframe_insert(data_path='location',frame=frame)
  for o in g.children:
   o.hide_render=(i>=2 and name in ['CHASSIS','COVER']) or (i==0 and name in ['ICE','MGUH','MGUK','ES']);o.keyframe_insert(data_path='hide_render',frame=frame)
 target=Vector((0,0,.35)) if i<2 else Vector((.7,0,.55));s.camera.location=target+Vector((-5,-7,4));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=7 if i<2 else 3.4
 s.camera.keyframe_insert(data_path='location',frame=frame);s.camera.keyframe_insert(data_path='rotation_euler',frame=frame);s.camera.data.keyframe_insert(data_path='ortho_scale',frame=frame)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/rb19-exhibit.blend'));print('Editorial reveal keys baked; no rigid-body explosion simulated')
