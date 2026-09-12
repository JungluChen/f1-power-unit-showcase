"""Original metric schematic. Run with Blender background. All packaging is illustrative."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
assert (R/'data/ground_truth_physics.json').exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats={}
for name,color,metal,rough in [('carbon',(0.022,0.033,0.044,1),.65,.3),('red',(.65,.018,.008,1),.6,.28),('silver',(.42,.5,.55,1),.8,.24),('dark',(.075,.085,.095,1),.75,.3),('copper',(.7,.28,.08,1),.8,.25),('cyan',(.04,.65,.55,1),.6,.28),('rubber',(.009,.011,.014,1),0,.65)]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;mats[name]=m
groups={}
for n in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']:
 o=bpy.data.objects.new(n,None);s.collection.objects.link(o);groups[n]=o

def finish(o,name,mat,group):
 o.name=name;o.data.materials.append(mats[mat]);o.parent=groups[group]
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o

def box(name,loc,dim,mat,group,bevel=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('machined edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat,group)
def cyl(name,a,b,r,mat,group,verts=24):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,mat,group)
def ell(name,loc,scale,mat,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.scale=scale;return finish(o,name,mat,group)
def pipe(name,pts,r,mat,group):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False);return finish(o,name,mat,group)
box('carbon_floor',(-.15,0,.15),(4.3,1.35,.06),'carbon','CHASSIS')
ell('survival_cell',(-.95,0,.48),(1.2,.32,.32),'carbon','CHASSIS')
ell('nose',(-1.95,0,.34),(.85,.17,.14),'red','CHASSIS')
ell('cockpit_opening',(-.82,0,.70),(.43,.24,.08),'rubber','CHASSIS')
pipe('halo',[(-1.2,-.24,.77),(-.6,-.29,.9),(-.42,0,.94),(-.6,.29,.9),(-1.2,.24,.77)],.025,'carbon','CHASSIS')
cyl('halo_pillar',(-1.2,0,.56),(-1.2,0,.83),.025,'carbon','CHASSIS')
for x in [-1.75,1.8]:
 for side in [-1,1]:
  y=side*.85;cyl('tyre',(x,y-.17,.36),(x,y+.17,.36),.35,'rubber','CHASSIS',40)
  cyl('wheel_rim',(x,y-side*.175,.36),(x,y+side*.179,.36),.225,'dark','CHASSIS',32)
  cyl('hub',(x,y,.36),(x,y+side*.185,.36),.07,'silver','CHASSIS')
  for k in range(8):
   a=k*math.tau/8;cyl('spoke',(x,y+side*.185,.36),(x+math.cos(a)*.21,y+side*.185,.36+math.sin(a)*.21),.015,'silver','CHASSIS',8)
  for xx in [x-.35,x+.35]:cyl('suspension',(xx,side*.23,.35),(x,side*.72,.36),.018,'carbon','CHASSIS',8)
for x,width in [(-2.55,1.85),(2.22,1.05)]:
 for k in range(3):box('wing_element',(x+k*.105,0,.20 if x<0 else .86),( .16,width,.035),'carbon','CHASSIS',.01)
 for side in [-1,1]:box('wing_endplate',(x+.1,side*width/2,.28 if x<0 else .82),(.43,.025,.25),'red','CHASSIS',.01)
box('rear_wing_support',(2.15,0,.55),(.06,.04,.55),'carbon','CHASSIS')
for side in [-1,1]:ell('sidepod',(.0,side*.5,.43),(.95,.24,.23),'red','COVER')
ell('engine_cowl',(.65,0,.63),(.85,.32,.46),'red','COVER')
box('fin',(.85,0,.97),(.85,.025,.25),'red','COVER',.01)
box('crankcase',(.48,0,.4),(.65,.36,.28),'silver','ICE')
cyl('crankshaft',(.08,0,.36),(.92,0,.36),.045,'dark','ICE')
for side in [-1,1]:
 for i in range(3):
  x=.23+i*.22;cyl('cylinder_liner',(x,side*.06,.42),(x,side*.25,.61),.084,'dark','ICE')
  cyl('piston',(x,side*.15,.51),(x,side*.20,.56),.071,'silver','ICE')
  cyl('injector',(x,side*.28,.66),(x,side*.33,.73),.021,'copper','ICE',12)
  pipe('exhaust_header',[(x,side*.29,.54),(x+.02,side*.46,.49),(.98,side*.40,.48),(1.12,side*.1,.58)],.026,'copper','ICE')
 head=box('cam_cover',(.46,side*.26,.68),(.72,.18,.12),'dark','ICE');head.rotation_euler.x=side*math.pi/4
 for i in range(8):box('head_rib',(.16+i*.085,side*.265,.745),(.012,.17,.02),'silver','ICE',.002)
 for x in [.18,.75]:
  for y in [side*.20,side*.31]:cyl('head_bolt',(x,y,.72),(x,y,.75),.018,'silver','ICE',8)
box('plenum',(.45,0,.81),(.62,.18,.13),'carbon','ICE')
for x in [.20,.43,.66]:
 for side in [-1,1]:pipe('intake_runner',[(x,0,.84),(x,side*.16,.8),(x,side*.24,.70)],.038,'silver','ICE')
# Turbo compressor, shaft-coupled MGU-H and turbine are deliberately co-located.
for x,mat in [(1.03,'silver'),(1.43,'copper')]:
 ell('turbo_housing',(x,0,.59),(.11,.17,.17),mat,'MGUH');cyl('turbo_inlet',(x-.13,0,.59),(x+.13,0,.59),.082,'dark','MGUH')
 for k in range(12):
  a=k*math.tau/12;cyl('turbine_blade',(x-.135,0,.59),(x-.135,math.cos(a)*.071,.59+math.sin(a)*.071),.009,'silver','MGUH',6)
cyl('turbo_shaft',(.9,0,.59),(1.58,0,.59),.022,'silver','MGUH')
cyl('MGUH_motor',(1.15,0,.59),(1.31,0,.59),.095,'copper','MGUH')
pipe('tailpipe',[(1.49,0,.59),(1.68,0,.64),(2.15,0,.62)],.06,'copper','MGUH')
cyl('MGUK_motor',(.2,-.44,.3),(.58,-.44,.3),.115,'cyan','MGUK')
for i in range(10):cyl('MGUK_fin',(.23+i*.031,-.44,.3),(.24+i*.031,-.44,.3),.123,'dark','MGUK')
cyl('MGUK_drive',(.2,-.44,.3),(.07,-.44,.3),.037,'silver','MGUK')
box('battery_case',(-.30,0,.27),(.6,.5,.15),'dark','ES')
for i in range(10):
 for j in range(3):box('battery_module',(-.55+i*.055,-.16+j*.16,.355),(.045,.14,.027),'cyan','ES',.004)
pipe('HV_cable',[(-.15,-.24,.34),(-.05,-.49,.29),(.20,-.46,.3)],.013,'copper','ES')
box('control_electronics',(-.62,0,.32),(.16,.35,.10),'silver','ES')
# Merge visual objects per material within each subsystem to bound draw calls.
for name,g in groups.items():
 for mat in mats:
  objs=[o for o in g.children if o.type=='MESH' and o.data.materials and o.data.materials[0].name==mat]
  if not objs:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name=name+'_'+mat
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/power-unit.blend'))
print('Metric schematic generated')
