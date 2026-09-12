"""Prepare Redgrund's CC BY 4.0 RB19 for the exhibit. Detailed exterior; educational internals."""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector,Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'source-assets/rb19-original.glb'))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
width=max(v.x for v in points)-min(v.x for v in points);scale=2/width;ycenter=(min(v.y for v in points)+max(v.y for v in points))/2;zmin=min(v.z for v in points)
rot=Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
for o in meshes:
 world=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Identity(4)
 for v in o.data.vertices:
  p=world@v.co;p.y-=ycenter;p.z-=zmin;v.co=(rot@p)*scale
for o in list(bpy.data.objects):
 if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();car=bpy.context.object;car.name='RB19_Exterior'
groups={}
for name in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']:
 g=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(g);groups[name]=g
# Physical finish adjustment preserves all source texture maps.
for mat in car.data.materials:
 if mat.use_nodes:
  bs=mat.node_tree.nodes.get('Principled BSDF')
  if bs:
   bs.inputs['Metallic'].default_value=.08;bs.inputs['Coat Weight'].default_value=.12;bs.inputs['Coat Roughness'].default_value=.24
# Preserve the source's UVs and livery. Divide the aft shell geometrically for an editorial reveal.
cover=car.copy();cover.data=car.data.copy();bpy.context.scene.collection.objects.link(cover);cover.name='RB19_Aft_shell';car.name='RB19_Chassis_and_aero'
def is_cover(c):return -.32<c.x<1.60 and abs(c.y)<.69 and c.z>.31
for o,keep in [(car,False),(cover,True)]:
 bm=bmesh.new();bm.from_mesh(o.data);kill=[f for f in bm.faces if is_cover(f.calc_center_median())!=keep];bmesh.ops.delete(bm,geom=kill,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();o.parent=groups['COVER' if keep else 'CHASSIS']
# Append the independently authored power-unit internals only.
with bpy.data.libraries.load(str(R/'archive-v1/power-unit.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if any(n.startswith(g+'_') for g in ['ICE','MGUH','MGUK','ES'])]
for o in dst.objects:
 if o is None:continue
 bpy.context.scene.collection.objects.link(o);name=o.name.split('_')[0];world=o.matrix_world.copy();o.parent=groups[name];o.matrix_world=world
 # Source internal materials are schematic. Use restrained engineering finishes.
 for mat in o.data.materials:
  if mat and mat.use_nodes:
   p=mat.node_tree.nodes.get('Principled BSDF')
   if p:
    p.inputs['Roughness'].default_value=.32
    if mat.name.startswith('cyan'):p.inputs['Base Color'].default_value=(.08,.13,.15,1);p.inputs['Metallic'].default_value=.7
    if mat.name.startswith('copper'):p.inputs['Base Color'].default_value=(.23,.13,.075,1);p.inputs['Roughness'].default_value=.43
# Add realistic-scale fastening and drive details, separate from the sourced exterior.
def material(n,c,metal,rough):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
steel=material('Machined_titanium',(.24,.27,.29),.85,.28);black=material('Black_anodized',(.015,.019,.025),.65,.34);rubber=material('Hose_rubber',(.012,.013,.015),0,.75);orange=material('HV_insulation',(.65,.11,.009),0,.4)
def cyl(n,a,b,r,mat,group,verts=20):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);o.parent=groups[group]
 for p in o.data.polygons:p.use_smooth=True
 return o
def box(n,loc,size,mat,group):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o.parent=groups[group];mod=o.modifiers.new('edge_radius','BEVEL');mod.width=.006;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return o
for side in [-1,1]:
 for x in [.18,.28,.38,.48,.58,.68,.78]:
  cyl('Cam_cover_hex_bolt',(x,side*.27,.725),(x,side*.27,.741),.007,steel,'ICE',6)
 for i in range(12):
  cyl('Stud',( .12+i*.055,side*.175,.42),(.12+i*.055,side*.18,.45),.006,steel,'ICE',6)
 # Looms follow the cylinder banks and end at three injector connectors.
 cyl('Injector_loom',(.15,side*.33,.74),(.8,side*.33,.74),.009,rubber,'ICE')
 for x in [.23,.45,.67]:
  box('Injector_connector',(x,side*.33,.75),(.035,.035,.034),black,'ICE')
  cyl('Connector_lead',(x,side*.33,.73),(x,side*.25,.65),.006,rubber,'ICE',12)
for x in [.22,.28,.34,.4,.46,.52]:
 for ang in [0,math.pi/2,math.pi,math.pi*1.5]:
  y=-.44+math.cos(ang)*.105;z=.3+math.sin(ang)*.105;cyl('Motor_fastener',(x,y,z),(x+.012,y,z),.006,steel,'MGUK',6)
for x in [-.54,-.05]:
 for y in [-.22,.22]:cyl('ES_fastener',(x,y,.352),(x,y,.363),.008,steel,'ES',6)
for side in [-1,1]:
 cyl('HV_orange_cable',(-.2,side*.24,.3),(.16,side*.43,.3),.012,orange,'ES')
# Consolidate internal details by material to control draw calls.
for group in ['ICE','MGUH','MGUK','ES']:
 mats=set(m for o in groups[group].children if o.type=='MESH' for m in o.data.materials)
 for mat in mats:
  obs=[o for o in groups[group].children if o.type=='MESH' and len(o.data.materials)==1 and o.data.materials[0]==mat]
  if len(obs)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join()
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
# Blender saves the editable full-resolution textured model at metric display scale.
R.joinpath('blender').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/rb19-exhibit.blend'))
bpy.ops.object.select_all(action='SELECT')
p=R/'public/assets/models/f1-power-unit.glb'
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=16,export_draco_normal_quantization=10,export_yup=True)
report={'source':'Redgrund / Oracle Red Bull F1 Car RB19 2023','license':'CC BY 4.0','source_sha256':hashlib.sha256((R/'source-assets/rb19-original.glb').read_bytes()).hexdigest(),'exterior_width_m':2,'scale_method':'uniform normalization to 2m regulatory width; not a verified team CAD dimension','model_bytes':p.stat().st_size,'vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH'),'texture_dimensions':[[*im.size] for im in bpy.data.images if im.size[0]],'coordinates':'Blender Z up -> glTF Y up','draco':{'level':6,'position_bits':16,'normal_bits':10},'reveal':'aft shell geometric partition; illustrative internals; not service-panel topology'}
(R/'data/web_export.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
# Studio plates: metric contact shadow, broad softboxes, restrained highlights.
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.fps=30;s.frame_start=1;s.frame_end=3600;s.render.use_motion_blur=True;s.render.motion_blur_shutter=.25
s.world=bpy.data.worlds.new('Studio_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.16,.20,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.25
floorMat=material('Studio_floor',(.023,.028,.035),.2,.44)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));floor=bpy.context.object;floor.name='Studio_floor';floor.data.materials.append(floorMat)
bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='Studio_camera';s.camera.data.type='ORTHO';s.camera.data.ortho_scale=7.2
for loc,power,size in [((-3,-4,6),1100,5),((2,1,5),1600,4),((-1,4,2.5),900,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='RECTANGLE';l.data.size=size;l.data.size_y=size*.35;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
for i,n in enumerate(['Assembly','Reveal','ICE','MGU-H','MGU-K','Energy store']):s.timeline_markers.new(n,frame=i*600+1).camera=s.camera
states=[{}, {'COVER':(0,0,1.0)}, {'COVER':(0,0,2.3),'CHASSIS':(-1,0,-1.2)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,-.65,.5)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.15,.5,.5),'MGUK':(0,-.65,.35)}, {'COVER':(0,0,3),'CHASSIS':(-1,0,-2),'MGUH':(.2,.5,.5),'MGUK':(0,.5,.25),'ES':(-.15,-.5,.5)}]
for i,state in enumerate(states):
 for name,g in groups.items():
  g.location=state.get(name,(0,0,0))
  for ch in g.children:ch.hide_render=(i>=2 and name in ['CHASSIS','COVER']) or (i==0 and name in ['ICE','MGUH','MGUK','ES'])
 target=Vector((0,0,.35)) if i<2 else Vector((.7,0,.55));s.camera.location=target+Vector((-5,-7,4.0));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=7.0 if i<2 else 3.4
 s.render.filepath=str(R/f'public/assets/textures/plate-{i}.png');bpy.ops.render.render(write_still=True)
 if i==0:
  bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/rb19-exhibit.blend'))
