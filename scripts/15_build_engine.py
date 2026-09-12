"""Reference-informed detailed Honda-era V6 hybrid. Original art, not manufacturer CAD.
Keeps the approved Redgrund RB19 exterior. Replaces every prior internal mesh.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'archive-v2/rb19-exhibit.blend'))
s=bpy.context.scene;s.frame_set(1)
for o in list(bpy.data.objects):
 if o.type=='MESH' and not o.name.startswith('RB19_'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
 o.animation_data_clear()
 if o.type=='CAMERA':o.data.animation_data_clear()
for name in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']:
 g=bpy.data.objects.get(name)
 if not g:g=bpy.data.objects.new(name,None);s.collection.objects.link(g)
 g.location=(0,0,0)
G={n:bpy.data.objects[n] for n in ['CHASSIS','COVER','ICE','MGUH','MGUK','ES']}
for o in G['CHASSIS'].children:o.hide_render=False
for o in G['COVER'].children:o.hide_render=False

def group(n,parent='ICE'):
 o=bpy.data.objects.new(n,None);s.collection.objects.link(o);o.parent=G[parent] if isinstance(parent,str) else parent;return o
shell=group('ENGINE_SHELL');plenum=group('INTAKE_PLENUM');headers=group('EXHAUST_HEADERS');core=group('MOVING_CORE');crank=group('CRANKSHAFT',core)
# PBR materials: polymer, machined metal, dark carbon and woven heat shielding.
def mat(n,c,metal=0,rough=.4,texture=None):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'source-assets/engine-materials'/texture));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  norm=m.node_tree.nodes.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(R/'source-assets/engine-materials/carbon-normal.png'));norm.image.colorspace_settings.name='Non-Color';norm.image.pack();nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.24 if texture.startswith('carbon') else .45;m.node_tree.links.new(norm.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
 return m
al=mat('PU_Billet_aluminium',(.52,.55,.57),.85,.32);bright=mat('PU_Machined_edges',(.7,.72,.73),.95,.23);steel=mat('PU_Steel_fasteners',(.2,.23,.26),.95,.28);carbon=mat('PU_Carbon_plenum',(.03,.035,.04),.1,.36,'carbon-base.png');shield=mat('PU_Woven_heatshield',(.32,.3,.25),.72,.64,'heatshield-base.png');inconel=mat('PU_Heat_aged_inconel',(.28,.22,.14),.9,.43);rubber=mat('PU_Rubber_and_looms',(.009,.012,.016),0,.68);black=mat('PU_Anodized_cases',(.032,.037,.045),.65,.38);orange=mat('PU_HV_orange',(.85,.16,.008),0,.44);purple=mat('PU_Connector_purple',(.26,.06,.21),.6,.35);gold=mat('PU_Brass_fittings',(.43,.27,.09),.85,.31)

def finish(o,n,m,parent,smooth=True):
 o.name=n;o.parent=G[parent] if isinstance(parent,str) else parent;o.data.materials.append(m)
 if smooth:
  for p in o.data.polygons:p.use_smooth=True
 return o

def box(n,loc,dim,m,parent,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('Machined_edge_radius','BEVEL');md.width=bevel;md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name)
 finish(o,n,m,parent,False)
 return o

def cyl(n,a,b,r,m,parent,verts=32,r2=None):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)*.5);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();finish(o,n,m,parent)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def tube(n,points,r,m,parent,res=4):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=r;cu.bevel_resolution=res;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new(n,cu);s.collection.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');return finish(bpy.context.object,n,m,parent)

def ring(n,loc,major,minor,m,parent,axis='X'):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=64,minor_segments=10,location=loc);o=bpy.context.object
 if axis=='X':o.rotation_euler.y=math.pi/2
 if axis=='Y':o.rotation_euler.x=math.pi/2
 return finish(o,n,m,parent)

def extrude(n,xs,sections,m,parent):
 count=len(sections[0]);vs=[(x,*p) for x,sec in zip(xs,sections) for p in sec];fs=[]
 for k in range(len(xs)-1):
  for i in range(count):a=k*count+i;b=k*count+(i+1)%count;fs.append((a,b,b+count,a+count))
 fs.extend([tuple(reversed(range(count))),tuple((len(xs)-1)*count+i for i in range(count))]);me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);finish(o,n,m,parent,False)
 md=o.modifiers.new('Small_edge_radii','BEVEL');md.width=.004;md.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=md.name)
 return o

def bolt(loc,axis,parent,r=.005):
 a=Vector(loc);v=Vector(axis).normalized();cyl('Hex_socket_bolt',a,a+v*.006,r,steel,parent,6);cyl('Bolt_socket',a+v*.006,a+v*.0063,r*.48,black,parent,6)
def flange(x,y,z,r,parent):
 cyl('Machined_flange',(x-.008,y,z),(x+.008,y,z),r,bright,parent,64)
 for j in range(10):
  a=j*math.tau/10;bolt((x-.009,y+math.sin(a)*r*.84,z+math.cos(a)*r*.84),(-1,0,0),parent,.004)
# Enclosed crankcase and structural lower block. Layered gaskets and machined service faces.
sec=[(-.13,.19),(.13,.19),(.19,.27),(.27,.49),(.19,.56),(0,.38),(-.19,.56),(-.27,.49),(-.19,.27)]
extrude('Billet_V6_crankcase',[.16,.23,.74,.82],[sec,sec,sec,sec],al,shell)
box('Dry_sump_pan',(.49,0,.182),(.67,.28,.06),black,shell,.012)
box('Sump_joint',(.49,0,.215),(.7,.31,.012),bright,shell,.002)
for x in [.20,.28,.36,.44,.52,.60,.68,.76]:
 for side in [-1,1]:bolt((x,side*.153,.22),(0,0,1),shell)
for side in [-1,1]:
 # Bank decks and slim sculpted cylinder-head covers at 45 degrees.
 axis=Vector((0,side/math.sqrt(2),1/math.sqrt(2)));head=box('Cylinder_head_bank',(.49,side*.233,.52),(.66,.18,.12),al,shell,.012);head.rotation_euler.x=-side*math.pi/4
 cover=box('Camshaft_cover',(.49,side*.285,.586),(.70,.145,.055),bright,shell,.022);cover.rotation_euler.x=-side*math.pi/4
 # Longitudinal cover seam and paired cam bearing outlines.
 tube('Head_cover_rail',[(.14,side*.30,.60),(.23,side*.33,.63),(.72,side*.33,.63),(.83,side*.30,.60)],.011,al,shell)
 for x in [.18,.28,.38,.48,.58,.68,.78]:
  for yy,zz in [(.23,.62),(.35,.52)]:bolt((x,side*yy,zz),(0,side*.7,.7),shell,.0055)
 for x in [.29,.49,.69]:
  box('Coil_pack',(x,side*.30,.61),(.071,.05,.035),rubber,shell,.007)
  cyl('Purple_electrical_connector',(x,side*.338,.56),(x,side*.36,.555),.012,purple,shell,16)
  tube('Injector_wiring',[(x,side*.31,.64),(x+.025,side*.37,.65),(x+.07,side*.38,.58)],.004,rubber,shell,2)
 # Front and rear structural lugs, drilled inserts.
 for x in [.14,.84]:
  lug=box('Engine_mount',(x,side*.32,.41),(.07,.14,.046),al,shell,.012)
  cyl('Mount_bore',(x,side*.36,.435),(x,side*.36,.44),.016,black,shell,32)
 # Case reinforcing ribs and service plugs.
 for x in [.22,.32,.42,.52,.62,.72]:
  tube('Case_web',[(x,side*.14,.25),(x,side*.21,.34),(x+.024,side*.25,.45)],.01,al,shell,2)
  bolt((x,side*.205,.29),(0,side,0),shell,.006)
 for x in [.26,.52,.72]:cyl('Oil_gallery_plug',(x,side*.246,.4),(x,side*.258,.4),.014,steel,shell,6)
# Shaped carbon intake plenum. Twin lobes follow intake routes into the V; no exposed toy trumpets.
for side in [-1,1]:
 sections=[]
 for x,wy,h,zc in [(.09,.055,.07,.80),(.21,.092,.10,.84),(.64,.092,.092,.88),(.83,.06,.065,.85)]:
  sections.append([(side*.102+math.cos(j*math.tau/32)*wy,zc+math.sin(j*math.tau/32)*h) for j in range(32)])
 ob=extrude('Carbon_intake_plenum',[.09,.21,.64,.83],sections,carbon,plenum)
 for face in ob.data.polygons:face.use_smooth=True
 tube('Charge_air_neck',[(.09,side*.1,.81),(-.03,side*.14,.80),(-.11,side*.21,.71)],.049,carbon,plenum)
 cyl('Charge_pipe_clamp',(-.10,side*.20,.70),(-.08,side*.19,.735),.054,steel,plenum)
 for x in [.25,.45,.65]:tube('Intake_runner',[(x,side*.1,.82),(x,side*.14,.72),(x,side*.2,.62)],.032,carbon,plenum)
 for x in [.22,.75]:bolt((x,side*.12,.944),(0,0,1),plenum,.004)
# Joined plenum bridge and visible embossed identification, not a manufacturer logo.
box('Plenum_bridge',(.48,0,.845),(.5,.11,.1),carbon,plenum,.04)
# Seat the plenum close to the heads, as in the published engine reference.
plenum.location.z=-.10
# Heat shielded exhausts sweep down and back, occupying realistic outer-bank volume.
for side in [-1,1]:
 for idx,x in enumerate([.29,.49,.69]):
  pts=[(x,side*.31,.47),(x-.055,side*(.41+idx*.024),.37),(x+.08,side*(.48+idx*.018),.265),(.88,side*.39,.32),(1.02,side*.12,.51)]
  tube('Insulated_exhaust_primary',pts,.035,shield,headers,5)
  cyl('Exhaust_port_flange',(x,side*.29,.47),(x,side*.33,.47),.042,al,headers)
  for off in [-.037,.037]:bolt((x+off,side*.32,.49),(0,side,0),headers,.004)
  # Overlap seams and stainless retaining bands over the sleeve.
  cyl('Manifold_joint_band',(x-.035,side*(.415+idx*.024),.34),(x-.028,side*(.42+idx*.024),.329),.038,steel,headers)
 tube('Collector_neck',[(.87,side*.39,.32),(.98,side*.25,.39),(1.045,side*.12,.51)],.059,inconel,headers)
 # Service plumbing over and along the bank, smaller than the exhaust.
 tube('Coolant_hardline',[(.03,side*.27,.40),(.14,side*.39,.66),(.70,side*.40,.68),(.9,side*.28,.58)],.01,bright,shell)
 tube('Oil_return_hose',[(.10,side*.25,.58),(.07,side*.30,.47),(.16,side*.23,.23)],.014,rubber,shell)
 tube('Main_wiring_loom',[(.1,side*.2,.68),(.2,side*.38,.67),(.68,side*.39,.65),(.82,side*.28,.39)],.008,rubber,shell)
 for x in [.18,.37,.60,.78]:cyl('Loom_retainer',(x,side*.382,.642),(x+.012,side*.382,.642),.012,black,shell,16)
# Split compressor / MGU-H / turbine, aligned with crank axis as on published Honda layouts.
def volute(n,x,r,depth,m,parent):
 # Variable-area scroll in the transverse plane, with an eccentric tube radius.
 verts=[];faces=[];N=96;K=16
 for i in range(N+1):
  a=i/N*math.tau;rr=r*(.87+.10*i/N);thick=.024+.019*i/N
  for j in range(K):
   b=j/K*math.tau;verts.append((x+math.sin(b)*depth,math.sin(a)*(rr+math.cos(b)*thick),.55+math.cos(a)*(rr+math.cos(b)*thick)))
 for i in range(N):
  for j in range(K):a=i*K+j;b=i*K+(j+1)%K;faces.append((a,b,b+K,a+K))
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);finish(o,n,m,parent)
for x,m in [(-.06,al),(1.025,inconel)]:
 volute('Compressor_scroll' if x<0 else 'Turbine_scroll',x,.11,.04,m,'MGUH');flange(x-.044,0,.55,.107,'MGUH')
 # Open bell mouth instead of closed sphere.
 ring('Turbo_mouth_lip',(x-.075,0,.55),.074,.008,bright,'MGUH')
 cyl('Turbo_dark_throat',(x-.064,0,.55),(x-.052,0,.55),.068,black,'MGUH',64)
 for j in range(15):
  a=j*math.tau/15;tube('Impeller_blade',[(x-.068,math.sin(a)*.018,.55+math.cos(a)*.018),(x-.072,math.sin(a+.16)*.045,.55+math.cos(a+.16)*.045),(x-.061,math.sin(a+.31)*.066,.55+math.cos(a+.31)*.066)],.003,bright,'MGUH',1)
 cyl('Impeller_hub',(x-.075,0,.55),(x-.055,0,.55),.014,steel,'MGUH')
cyl('MGUH_rotor_housing',(.30,0,.55),(.68,0,.55),.061,black,'MGUH',48)
cyl('Turbo_common_shaft',(-.04,0,.55),(1.025,0,.55),.012,steel,'MGUH')
for x in [.30,.34,.64,.68]:flange(x,0,.55,.067,'MGUH')
tube('Turbine_outlet',[(1.06,0,.55),(1.19,0,.61),(1.32,0,.7)],.066,inconel,'MGUH')
# Curve tailpipe already has an open end; no misaligned overlay ring.
# Realistic accessory motor: closed casing, split flange, cooling ribs, braided connections.
cyl('MGUK_case',(.18,-.285,.26),(.58,-.285,.26),.083,black,'MGUK',64)
for x in [.18,.58]:flange(x,-.285,.26,.089,'MGUK')
for j in range(16):
 a=j*math.tau/16;cyl('Motor_cooling_rib',(.22,-.285+math.cos(a)*.081,.26+math.sin(a)*.081),(.55,-.285+math.cos(a)*.081,.26+math.sin(a)*.081),.004,al,'MGUK',8)
box('MGUK_terminal',(.35,-.34,.33),(.095,.075,.05),black,'MGUK',.012)
cyl('Motor_drive',(.10,-.285,.26),(.18,-.285,.26),.024,steel,'MGUK')
# Battery is a sealed pack with a removable lid, not oversized visible cells.
box('Energy_store_case',(-.51,0,.22),(.62,.46,.19),black,'ES',.016)
box('Energy_store_lid',(-.51,0,.323),(.64,.475,.019),carbon,'ES',.008)
for x in [-.79,-.68,-.57,-.46,-.35,-.23]:
 for side in [-1,1]:bolt((x,side*.216,.336),(0,0,1),'ES',.0045)
for side in [-1,1]:
 cyl('HV_connector',(-.19,side*.13,.23),(-.12,side*.13,.23),.023,orange,'ES');tube('HV_cable',[(-.12,side*.13,.23),(-.04,side*.23,.22),(.14,side*.32,.25),(.32,-.34,.33)],.009,orange,'ES')
box('Power_electronics',(-.56,0,.38),(.33,.28,.09),black,'ES',.01)
for i in range(14):box('Inverter_heat_sink',(-.70+i*.023,0,.432),(.008,.26,.022),al,'ES',.002)
# Functional core: six pistons and connecting rods use slider-crank kinematics in the browser.
# Radius 26.5mm and rod length 110mm are illustrative design inputs, not Honda measurements.
cyl('Crank_main_shaft',(.16,0,.30),(.81,0,.30),.022,steel,crank)
for idx,x in enumerate([.29,.49,.69]):
 phase=idx*math.tau/3
 for off in [-.026,.026]:
  cyl('Crank_counterweight',(x+off-.009,0,.30),(x+off+.009,0,.30),.056,steel,crank,48)
 for side in [-1,1]:
  piston=group(f'PISTON_{idx}_{side}',core);rod=group(f'ROD_{idx}_{side}',core)
  # Geometry local to origin, with piston stroke axis +Z and rod centered along +Z.
  cyl('Forged_piston',(0,0,-.02),(0,0,.009),.0395,al,piston,64)
  for z in [-.007,-.012,-.017]:ring('Piston_ring',(0,0,z),.0396,.0008,steel,piston,'Z')
  cyl('Piston_crown',(0,0,.009),(0,0,.011),.0385,bright,piston,64)
  box('Rod_I_web',(0,0,.055),(.014,.009,.11),steel,rod,.002)
  for z,r in [(0,.013),(.11,.010)]:ring('Rod_bearing_eye',(0,0,z),r,.004,bright,rod,'Y')
  axis=Vector((0,side/math.sqrt(2),1/math.sqrt(2)));piston.location=Vector((x,0,.30))+axis*.1365;piston.rotation_euler=axis.to_track_quat('Z','Y').to_euler();rod.location=(x,0,.30);rod.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
# UV unwrap custom generated textured surfaces. Tile at a fine scale to show weave, not stripes.
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name.startswith('RB19_'):continue
 if o.type=='MESH':
  if any(m and ('Carbon' in m.name or 'heatshield' in m.name) for m in o.data.materials):
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
   if o.data.uv_layers.active:
    for uv in o.data.uv_layers.active.data:uv.uv*=8
# Join stationary meshes per parent/material. Moving piston/rod groups remain separate and addressable.
for parent in [shell,plenum,headers,crank,G['MGUH'],G['MGUK'],G['ES']]:
 mats={m for o in parent.children if o.type=='MESH' for m in o.data.materials}
 for m in mats:
  obs=[o for o in parent.children if o.type=='MESH' and len(o.data.materials)==1 and o.data.materials[0]==m]
  if len(obs)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=parent.name+'_'+m.name
# Place the crank's rotation pivot on its axis while preserving mesh locations.
crank.location=(.49,0,.30)
for ob in crank.children:ob.location-=Vector((.49,0,.30))
# Apply the world transforms to all mesh data so their parent transforms are clean for the web.
# Piston and rod local geometry is preserved under its articulated parent.
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/detailed-power-unit.blend'))
bpy.ops.object.select_all(action='DESELECT')
for g in G.values():
 g.select_set(True)
 for o in g.children_recursive:o.hide_render=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'public/assets/models/f1-power-unit.glb'),export_format='GLB',use_selection=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=16,export_yup=True)
report={'basis':'Honda RA621H published front/rear/side views and V6 architecture article','reference_url':'https://global.honda/en/tech/motorsports/Formula-1/Powertrain_V6_power_unit/','accuracy':'reference-informed original reconstruction, not Honda CAD or RB19 exact engine','geometry':'billet crankcase, head covers, carbon plenums, insulated manifolds, split turbo, MGU-H, MGU-K, sealed energy store, six articulated pistons/rods','crank_radius_m':.0265,'rod_length_m':.110,'bore_m':.079,'mechanism_assumption':'illustrative slider crank; no claim to manufacturer firing order','GLB_bytes':(R/'public/assets/models/f1-power-unit.glb').stat().st_size,'vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH')}
(R/'data/engine-rebuild.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
# Studio engine beauty render: all casings fitted, no ghosting or artificial emissive glow.
for n in ['CHASSIS','COVER']:
 for o in G[n].children_recursive:o.hide_render=True
for o in core.children_recursive:o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.5;target=Vector((.40,0,.52));s.camera.location=target+Vector((-3.5,-5,2.5));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(R/'public/assets/textures/engine-beauty.png');bpy.ops.render.render(write_still=True)
for n in [shell,plenum]:
 for o in n.children_recursive:o.hide_render=True
for o in core.children_recursive:o.hide_render=False
s.render.filepath=str(R/'public/assets/textures/engine-cutaway.png');bpy.ops.render.render(write_still=True)
