"""Reference proxies and editorial articulation. Rigid bodies do not drive any trajectory."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
collection=bpy.data.collections.new('COLLISION_PROXIES');bpy.context.scene.collection.children.link(collection)
for i,name in enumerate(['ICE','MGUH','MGUK','ES']):
 bpy.ops.mesh.primitive_cube_add(size=.06,location=(i*.15,0,0));o=bpy.context.object;o.name='proxy_'+name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.hide_render=True;o.hide_viewport=True;o['scope']='disjoint reference cores; not complete housing collision geometry'
 o.parent=bpy.data.objects[name]
 # Parent hierarchy is the articulation constraint for this kinematic assembly.
 o['constraint']='rigid child of subsystem; editorial transform only'
bpy.context.scene.gravity=(0,0,-9.81)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/power-unit.blend'))
