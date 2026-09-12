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
 finish(o,n,m,parent,True)
 md=o.modifiers.new('Weighted_surface_normals','WEIGHTED_NORMAL');md.keep_sharp=True;md.weight=50;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=md.name)
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
# RA166E photographic study. Original geometry; measured bore/stroke and 80-degree bank.
cast=mat('RA_Black_cast_magnesium',(.012,.014,.016),.65,.28)
polished=mat('RA_Polished_exhaust',(.48,.49,.50),1,.19)
# Broad enclosed lower crankcase with a machined base plate.
box('Structural_crankcase',(.49,0,.38),(.76,.39,.42),cast,shell,.027)
box('Machined_sump_flange',(.49,0,.175),(.80,.43,.027),bright,shell,.008)
box('Dry_sump',(.49,0,.145),(.72,.35,.055),cast,shell,.012)
for side in [-1,1]:
 for x in [.16,.24,.32,.40,.48,.56,.64,.72,.80]:
  box('Lower_cast_rib',(x,side*.199,.32),(.016,.028,.25),cast,shell,.004)
  bolt((x,side*.216,.18),(0,0,-1),shell,.006)
 # Each bank has two rounded cam chambers, cast joining ribs, end caps and retained bolts.
 for yy,zz in [(.185,.66),(.325,.54)]:
  c=box('Black_cam_cover',(.49,side*yy,zz),(.78,.18,.17),cast,shell,.052);c.rotation_euler.x=-side*.6981
  for x in [.17,.31,.49,.67,.81]:
   c=box('Cam_cover_band',(x,side*yy,zz+.036),(.033,.192,.12),cast,shell,.018);c.rotation_euler.x=-side*.6981
  cyl('Cam_end_cap',(.087,side*yy,zz),(.104,side*yy,zz),.068,cast,shell,64)
  ring('Cam_end_machined_lip',(.087,side*yy,zz),.053,.004,bright,shell)
  cyl('Cam_end_recess',(.079,side*yy,zz),(.082,side*yy,zz),.026,rubber,shell)
  for x in [.16,.26,.36,.46,.56,.66,.76,.84]:
   bolt((x,side*(yy+.068),zz+.073),(0,side*.5,.86),shell,.0055)
 # Fine metal head gasket and multiple casting layers.
 c=box('Head_gasket',(.49,side*.253,.493),(.76,.28,.015),bright,shell,.007);c.rotation_euler.x=-side*.6981
 c=box('Cylinder_head_casting',(.49,side*.23,.52),(.76,.30,.17),cast,shell,.018);c.rotation_euler.x=-side*.6981
 for x in [.22,.36,.51,.66,.80]:
  for z in [.32,.41,.49]:
   ring('Service_bolt_washer',(x,side*.244,z),.009,.002,bright,shell,'Y');bolt((x,side*.248,z),(0,side,0),shell,.006)
 # Six throttle bodies, fuel rail and individual braided injector loops.
 for x in [.26,.49,.72]:
  cyl('Throttle_body',(x,side*.12,.70),(x,side*.16,.83),.041,cast,plenum)
  for z in [.73,.79]:ring('Throttle_clamp',(x,side*.15,z),.039,.003,bright,plenum,'Z')
  cyl('Injector_banjo',(x,side*.232,.80),(x,side*.267,.82),.014,gold,plenum,6)
  cyl('Injector_hex',(x,side*.255,.814),(x,side*.274,.825),.016,bright,plenum,6)
  tube('Fuel_injector_loop',[(x-.05,side*.195,.88),(x-.075,side*.29,.87),(x,side*.28,.815)],.0065,black,plenum)
  for j in range(5):ring('Braided_line_collars',(x-.048+j*.005,side*.195,.878),.007,.0015,steel,plenum,'X')
 tube('Fuel_rail',[(.13,side*.21,.86),(.48,side*.21,.86),(.83,side*.21,.86)],.008,bright,plenum)
 # Flexible wiring follows cover; clipped small hard lines create scale cues.
 tube('Ignition_harness',[(.11,side*.12,.70),(.20,side*.34,.69),(.55,side*.42,.61),(.84,side*.33,.61)],.008,rubber,shell)
 for x in [.23,.43,.63,.8]:
  tube('Spark_plug_lead',[(x,side*.33,.65),(x-.06,side*.36,.69),(x-.10,side*.42,.54)],.0045,rubber,shell)
  cyl('Plug_boot',(x,side*.33,.61),(x,side*.33,.655),.011,black,shell)
  tube('Oil_hard_line',[(x,side*.22,.20),(x,side*.30,.26),(x+.055,side*.31,.39)],.0045,bright,shell)
 # Cast mounting bosses.
 for x in [.12,.85]:
  box('Engine_mount_lug',(x,side*.28,.39),(.09,.14,.07),cast,shell,.014)
  ring('Mount_insert',(x,side*.30,.43),.018,.006,bright,shell,'Z')
# One broad black intake chamber with a rounded roof and a thick perimeter seam.
sections=[]
for wy,zlow,zhigh in [(.14,.88,1.0),(.205,.875,1.055),(.205,.875,1.055),(.145,.90,1.02)]:
 sections.append([(math.cos(j*math.tau/48)*wy,(zlow+zhigh)/2+math.sin(j*math.tau/48)*(zhigh-zlow)/2) for j in range(48)])
o=extrude('Broad_intake_plenum',[.12,.23,.76,.88],sections,cast,plenum)
for f in o.data.polygons:f.use_smooth=True
for side in [-1,1]:
 tube('Plenum_flange',[(.17,side*.15,.894),(.28,side*.204,.895),(.74,side*.204,.895),(.85,side*.15,.918)],.006,cast,plenum)
 for x in [.21,.33,.45,.57,.69,.81]:bolt((x,side*.17,.91),(0,side*.7,-.4),plenum,.004)
 tube('Plenum_charge_elbow',[(.83,side*.10,.97),(.94,side*.17,.94),(.98,side*.25,.83)],.062,cast,plenum)
 cyl('Intake_coupler',(.98,side*.25,.81),(.96,side*.23,.86),.066,rubber,plenum)
 for off in [0,.032]:ring('Intake_hose_clamp',(.98-off*.4,side*(.25-off*.4),.815+off),.065,.003,bright,plenum,'Z')
# Raised period-style lettering on the visible bank, matching the supplied photograph.
for side in [-1,1]:
 cu=bpy.data.curves.new('HONDA_cast_lettering','FONT');cu.body='HONDA';cu.align_x='CENTER';cu.size=.062;cu.extrude=.0009;cu.bevel_depth=.0003
 o=bpy.data.objects.new('HONDA_cast_lettering',cu);s.collection.objects.link(o);o.location=(.51,side*.235,.753);o.rotation_euler=(side*math.radians(43),0,0)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');finish(bpy.context.object,'Raised_HONDA',bright,shell)
# Front flywheel and clutch assembly: dark cutouts, machined rim and dense radial hardware.
cyl('Flywheel',(.026,0,.38),(.096,0,.38),.163,cast,shell,96)
ring('Flywheel_machined_rim',(.023,0,.38),.149,.009,steel,shell)
cyl('Clutch_center',(.008,0,.38),(.028,0,.38),.064,black,shell,64)
for j in range(18):
 a=j*math.tau/18;y=math.sin(a);z=math.cos(a)
 bolt((.005,y*.134,.38+z*.134),(-1,0,0),shell,.006)
 cyl('Clutch_vent',(.003,y*.095,.38+z*.095),(.011,y*.095,.38+z*.095),.012,rubber,shell,16)
 tube('Clutch_finger',[(.001,y*.043,.38+z*.043),(-.003,y*.072,.38+z*.072)],.0035,steel,shell,1)
# Two side-mounted turbochargers and sweeping exposed exhaust collectors.
for side in [-1,1]:
 turbo=group('PERIOD_TURBO_'+str(side),headers)
 center=Vector((.85,side*.54,.32))
 # True scroll section, differing cross section along its spiral.
 vs=[];fs=[];N=96;K=16
 for i in range(N+1):
  a=i/N*math.tau;rr=.095+.01*i/N;thick=.026+.02*i/N
  for j in range(K):
   b=j/K*math.tau;vs.append(tuple(center+Vector((math.sin(b)*.038,math.sin(a)*(rr+math.cos(b)*thick),math.cos(a)*(rr+math.cos(b)*thick)))))
 for i in range(N):
  for j in range(K):q=i*K+j;v=i*K+(j+1)%K;fs.append((q,v,v+K,q+K))
 me=bpy.data.meshes.new('IHI_scroll');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('IHI_scroll',me);s.collection.objects.link(o);finish(o,'IHI_compressor_scroll',al,turbo)
 cyl('Turbine_hot_housing',(.75,side*.54,.32),(.81,side*.54,.32),.104,cast,turbo,64)
 ring('Turbo_flange',(.82,side*.54,.32),.114,.009,steel,turbo)
 cyl('Turbo_inlet_recess',(.90,side*.54,.32),(.903,side*.54,.32),.065,rubber,turbo,64)
 ring('Turbo_inlet_lip',(.906,side*.54,.32),.066,.007,bright,turbo)
 for j in range(12):
  a=j*math.tau/12;bolt((.92,side*.54+math.sin(a)*.105,.32+math.cos(a)*.105),(1,0,0),turbo,.005)
 # Three polished primaries, joining just before the turbine. Outer sweep is a large-bore outlet.
 for idx,x in enumerate([.26,.49,.72]):
  tube('Exposed_exhaust_primary',[(x,side*.34,.46),(x+.035,side*(.40+idx*.015),.44),(.68,side*(.46+idx*.025),.40),(.76,side*.54,.32)],.027,polished,headers,5)
  cyl('Exhaust_flange',(x,side*.325,.46),(x,side*.358,.46),.036,steel,headers)
  for dx in [-.033,.033]:bolt((x+dx,side*.35,.46),(0,side,0),headers,.004)
 tube('Swept_turbo_tailpipe',[(.77,side*.54,.32),(.60,side*.59,.31),(.26,side*.57,.41),(-.15,side*.51,.58)],.058,polished,headers,6)
 tube('Turbo_oil_feed',[(.78,side*.54,.43),(.70,side*.44,.54),(.45,side*.30,.41)],.005,steel,shell)
 cyl('Wastegate_diaphragm',(.60,side*.56,.30),(.66,side*.56,.30),.048,cast,headers,48)
 for x in [.60,.66]:ring('Wastegate_rim',(x,side*.56,.30),.049,.004,steel,headers)
 tube('Wastegate_pipe',[(.62,side*.55,.27),(.58,side*.43,.24),(.74,side*.46,.28)],.02,polished,headers)
 tube('Boost_control_hose',[(.61,side*.56,.33),(.46,side*.46,.38),(.36,side*.38,.61)],.004,rubber,shell)
# Auxiliary pumps, brackets and fastener-dense front accessory drive.
for yy,zz,r in [(-.22,.57,.046),(.22,.57,.046),(-.15,.74,.031)]:
 cyl('Accessory_pump',(.005,yy,zz),(.13,yy,zz),r,cast,shell,48);ring('Pump_cover_seam',(.001,yy,zz),r*.9,.003,bright,shell)
 for j in range(6):
  a=j*math.tau/6;bolt((-.003,yy+math.sin(a)*r*.75,zz+math.cos(a)*r*.75),(-1,0,0),shell,.004)
 tube('Accessory_hose',[(.01,yy,zz+.03),(-.04,yy-.06,zz+.04),(.06,yy-.08,zz-.09)],.011,rubber,shell)
# Detailed mechanical core: interrupted main journals, three offset crankpins and paired rods.
def annulus(n,x0,x1,y,z,ro,ri,m,parent,N=64):
 vs=[]
 for x,r in [(x0,ro),(x1,ro),(x0,ri),(x1,ri)]:
  vs.extend([(x,y+math.cos(j*math.tau/N)*r,z+math.sin(j*math.tau/N)*r) for j in range(N)])
 fs=[]
 for j in range(N):
  k=(j+1)%N
  fs.extend([(j,k,N+k,N+j),(2*N+j,3*N+j,3*N+k,2*N+k),(j,2*N+j,2*N+k,k),(N+j,N+k,3*N+k,3*N+j)])
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);finish(o,n,m,parent)
 for i,f in enumerate(me.polygons):f.use_smooth=i%4<2
 return o
def subtract(ob,cutter):
 bpy.context.view_layer.objects.active=ob;md=ob.modifiers.new('Machined_recess','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=cutter;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(cutter,do_unlink=True)
for lo,hi in [(.13,.258),(.322,.458),(.522,.658),(.722,.86)]:
 cyl('Ground_main_bearing_journal',(lo,0,.30),(hi,0,.30),.019,bright,crank,96)
 for x in [lo+.004,hi-.004]:ring('Journal_edge_fillet',(x,0,.30),.018,.0015,steel,crank)
# Rear crank mounting flange with bolt-circle bores, front drive nose.
annulus('Crank_output_flange',.842,.865,0,.30,.048,.013,steel,crank)
for j in range(8):
 t=j*math.tau/8;cyl('Flange_bolt_bore',(.866,.034*math.cos(t),.30+.034*math.sin(t)),(.867,.034*math.cos(t),.30+.034*math.sin(t)),.004,rubber,crank,16)
cyl('Crank_drive_nose',(.092,0,.30),(.13,0,.30),.012,steel,crank,64)
for idx,x in enumerate([.29,.49,.69]):
 phase=idx*math.tau/3;cy=-.0254*math.sin(phase);cz=.30+.0254*math.cos(phase)
 cyl('Offset_crankpin',(x-.024,cy,cz),(x+.024,cy,cz),.0125,bright,crank,96)
 marker=group(f'CRANKPIN_{idx}',crank);marker.location=(x,cy,cz)
 # Asymmetric forged cheeks: broad counterbalance below axis, narrow crankpin nose above.
 profile=[(-.018,.040),(.018,.040),(.027,.023),(.026,.008),(.044,-.023),(.041,-.040),(.025,-.053),(-.025,-.053),(-.041,-.040),(-.044,-.023),(-.026,.008),(-.027,.023)]
 rotated=[(y*math.cos(phase)-z*math.sin(phase),.30+y*math.sin(phase)+z*math.cos(phase)) for y,z in profile]
 for off in [-.027,.027]:
  web=extrude('Forged_counterweight_cheek',[x+off-.006,x+off+.006],[rotated,rotated],steel,crank)
  for f in web.data.polygons:f.use_smooth=True
  md=web.modifiers.new('Weighted_cheek_normals','WEIGHTED_NORMAL');bpy.context.view_layer.objects.active=web;bpy.ops.object.modifier_apply(modifier=md.name)
 # Oil feed hole through the ground crankpin surface.
 cyl('Crankpin_oil_drilling',(x,cy-.0125,cz),(x,cy-.0129,cz),.002,rubber,crank,24)
 for side in [-1,1]:
  piston=group(f'PISTON_{idx}_{side}',core);rod=group(f'ROD_{idx}_{side}',core)
  # Revolved hollow piston, crown above wrist-pin origin. Actual ring-land relief grooves.
  profile=[(.037,-.027),(.039,-.019),(.0395,.012),(.0381,.013),(.0381,.015),(.0395,.016),(.0395,.019),(.0382,.0195),(.0382,.021),(.0395,.0215),(.0395,.024),(.0382,.0245),(.0382,.026),(.0395,.0265),(.0395,.031),(.0375,.033),(0,.033),(0,.027),(.033,.027),(.033,-.023),(.035,-.027)]
  N=96;vs=[(r*math.cos(j*math.tau/N),r*math.sin(j*math.tau/N),z) for r,z in profile for j in range(N)];fs=[]
  for k in range(len(profile)):
   for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j))
  me=bpy.data.meshes.new('Hollow_piston');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Forged_slipper_piston',me);s.collection.objects.link(o);finish(o,'Forged_slipper_piston',al,piston)
  for q in [-1,1]:
   cutter=box('Skirt_relief_cutter',(q*.039,0,-.024),(.026,.051,.034),al,piston,.008);subtract(o,cutter)
  bore=cyl('Pin_bore_tool',(-.06,0,0),(.06,0,0),.0095,al,piston,64);subtract(o,bore)
  for px in [-.016,.016]:
   for py in [-.016,.016]:
    cutter=cyl('Valve_pocket_tool',(px,py,.031),(px,py,.045),.0105,al,piston,48);subtract(o,cutter)
  for face in o.data.polygons:face.use_smooth=abs(face.normal.z)<.95
  # Ring pack and oil-control expander, separate from aluminium lands.
  for z in [.0203,.0252]:ring('Compression_ring',(0,0,z),.0389,.00065,steel,piston,'Z')
  for z in [.0132,.0148]:ring('Oil_control_rail',(0,0,z),.0388,.00045,steel,piston,'Z')
  for q in [-1,1]:annulus('Internal_pin_boss',q*.020-.006,q*.020+.006,0,0,.014,.0095,al,piston)
  annulus('Hollow_wrist_pin',-.034,.034,0,0,.0093,.0058,bright,piston)
  for q in [-1,1]:ring('Wrist_pin_circlip',(q*.0345,0,0),.0096,.0007,steel,piston,'X')
  # Connecting rod has true through bores, bronze small-end bushing, H section and split cap.
  annulus('Rod_big_end',-.007,.007,0,0,.0205,.0127,steel,rod)
  annulus('Big_end_bearing_shell',-.0072,.0072,0,0,.0134,.0126,gold,rod)
  annulus('Rod_small_end',-.006,.006,0,.11,.013,.0095,steel,rod)
  annulus('Small_end_bushing',-.0062,.0062,0,.11,.0102,.00935,gold,rod)
  outline=[(-.013,.013),(-.009,.027),(-.006,.082),(-.009,.100),(.009,.100),(.006,.082),(.009,.027),(.013,.013)]
  extrude('Forged_rod_web',[-.002,.002],[outline,outline],steel,rod)
  for q in [-1,1]:
   tube('H_beam_flange',[(q*.005,-.010,.018),(q*.005,-.006,.055),(q*.005,-.006,.082),(q*.005,-.009,.10)],.0028,steel,rod,2)
   tube('H_beam_flange',[(q*.005,.010,.018),(q*.005,.006,.055),(q*.005,.006,.082),(q*.005,.009,.10)],.0028,steel,rod,2)
   box('Cap_split_line',(0,q*.018,-.003),(.014,.006,.001),rubber,rod,.0002)
   cyl('Rod_cap_bolt',(0,q*.016,-.020),(0,q*.016,.010),.0027,bright,rod,24)
   cyl('Rod_cap_bolt_head',(0,q*.016,-.021),(0,q*.016,-.017),.0044,steel,rod,12)
  axis=Vector((0,side*math.sin(math.radians(40)),math.cos(math.radians(40))));origin=Vector((x+side*.008,0,.30));pin=Vector((0,cy,cz-.30));travel=pin.dot(axis)+math.sqrt(.11**2-(pin.length_squared-pin.dot(axis)**2));wrist=origin+axis*travel
  piston.location=wrist;piston.rotation_euler=axis.to_track_quat('Z','Y').to_euler();rod.location=origin+pin;rod.rotation_euler=(wrist-rod.location).to_track_quat('Z','Y').to_euler()
# UV unwrap custom generated textured surfaces. Tile at a fine scale to show weave, not stripes.
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name.startswith('RB19_'):continue
 if o.type=='MESH':
  if any(m and ('Carbon' in m.name or 'heatshield' in m.name) for m in o.data.materials):
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
   if o.data.uv_layers.active:
    for uv in o.data.uv_layers.active.data:uv.uv*=8
# Join stationary meshes per parent/material. Moving piston/rod groups remain separate and addressable.
for parent in [shell,plenum,headers,crank,G['MGUH'],G['MGUK'],G['ES']]+[o for o in core.children if o.name.startswith(('PISTON_','ROD_'))]:
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
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ra166e-reference.blend'))
bpy.ops.object.select_all(action='DESELECT')
for g in G.values():
 g.select_set(True)
 for o in g.children_recursive:o.hide_render=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'public/assets/models/ra166e-reference.glb'),export_format='GLB',use_selection=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=16,export_yup=True)
report={'basis':'User-supplied Honda RA166E photograph and Honda RA166E official specifications','reference_url':'https://global.honda/en/POWEREDbyHONDA/1986_ra166e/','accuracy':'reference-informed original reconstruction, not Honda CAD or RB19 exact engine','geometry':'black cast housings, broad intake plenum, twin turbos, exposed polished exhausts, flywheel, fuel rails, six articulated pistons','crank_radius_m':.0254,'rod_length_m':.110,'bore_m':.079,'mechanism_assumption':'illustrative slider crank; no claim to manufacturer firing order','GLB_bytes':(R/'public/assets/models/ra166e-reference.glb').stat().st_size,'vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH')}
(R/'data/ra166e-rebuild.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
# Studio engine beauty render: all casings fitted, no ghosting or artificial emissive glow.
for n in ['CHASSIS','COVER']:
 for o in G[n].children_recursive:o.hide_render=True
for o in core.children_recursive:o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=1.95;target=Vector((.40,0,.52));s.camera.location=target+Vector((-4.6,-6,2.9));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(R/'public/assets/textures/ra166e-beauty.png');bpy.ops.render.render(write_still=True)
for n in [shell,plenum,headers]:
 for o in n.children_recursive:o.hide_render=True
for o in core.children_recursive:o.hide_render=False
s.camera.data.ortho_scale=.95;target=Vector((.49,0,.34));s.camera.location=target+Vector((-3.5,-6,3.5));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(R/'public/assets/textures/ra166e-cutaway.png');bpy.ops.render.render(write_still=True)
