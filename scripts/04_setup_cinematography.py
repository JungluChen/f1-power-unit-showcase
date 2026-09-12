import bpy,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
assert json.loads((R/'data/validation.json').read_text())['status']=='passed'
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=30;s.frame_start=1;s.frame_end=3600
s.render.use_motion_blur=True;s.render.motion_blur_shutter=.25;s.world.color=(.06,.06,.06)
bpy.ops.object.camera_add(location=(-6,-8,5));cam=bpy.context.object;cam.name='Exhibit_camera';cam.data.type='ORTHO';cam.data.ortho_scale=7;cam.rotation_euler=(Vector((0,0,.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
for loc,power,size in [((-2,-4,7),1800,5),((2,4,4),2200,4),((4,-1,2),1200,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
for i,title in enumerate(['Assembly','Reveal','ICE','MGU-H','MGU-K','Energy store']):
 m=s.timeline_markers.new(title,frame=i*600+1);m.camera=cam
s.render.image_settings.file_format='PNG';s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/power-unit.blend'))
