import '../css/style.css';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import gsap from 'gsap';import {ScrollTrigger} from 'gsap/ScrollTrigger';import katex from 'katex';
gsap.registerPlugin(ScrollTrigger);
for(const el of document.querySelectorAll('[data-tex]'))katex.render(el.dataset.tex.replaceAll('\\\\','\\'),el,{throwOnError:false});
const historic=new URLSearchParams(location.search).get('engine')!=='hybrid';
if(historic){
 document.body.classList.add('historic');document.title='Honda RA166E — Engine Study';
 document.querySelector('.stage-top').innerHTML='<span><i></i> HONDA RA166E / REFERENCE STUDY</span><span>1986 / TWIN TURBO V6</span>';
 document.querySelector('.model-note span:last-child').textContent='ORIGINAL RECONSTRUCTION / PHOTO REFERENCE';
 document.querySelector('.era-note').innerHTML='<span>AN EDITORIAL ENGINE STUDY</span><p>The 2023 RB19 exterior introduces the 1986 Honda RA166E reference engine. These are separate generations, combined here for the visual reveal.</p>';
 document.querySelector('#film').remove();
 const text=document.querySelector('#chapter-2 .chapter-content');text.innerHTML='<p class="eyebrow">1986 / HONDA RA166E</p><h2>Built under<br>pressure.</h2><p>Black cast housings. Exposed exhausts. Twin turbochargers. An engine study built around your Honda reference photograph.</p><div class="detail"><span>80° V6 · TWIN TURBO · DRY SUMP</span><strong>1,494 cm³</strong><p>Inspect the assembled engine, or select Cutaway and run the six-piston mechanism in slow motion.</p><a class="reference-link" href="?engine=hybrid">Return to the modern hybrid exhibit ↗</a></div>';
 document.querySelector('#sources').innerHTML='<p class="eyebrow">THE REFERENCE</p><h2>Honda RA166E, 1986.</h2><p>Original 3D reconstruction from your supplied photograph. Honda specifies an 80° V6, 1,494 cm³, twin turbochargers, and a 79 × 50.8 mm bore and stroke. Hidden geometry and connecting-rod dimensions are approximations.</p><a class="reference-link" href="https://global.honda/en/F1/machine/1986_WilliamsHondaFW11/">Honda technical specifications ↗</a><br><a class="reference-link" href="assets/textures/ra166e-beauty.png">Open the full-resolution studio render ↗</a>';
 document.querySelector('header nav').innerHTML='<a href="#chapter-0">The anatomy</a><a href="?engine=hybrid">Hybrid exhibit</a><a href="#sources">Reference</a>';
 document.querySelector('#chapter-0 h1').innerHTML='Inside the car.<br><em>Into the</em><br>engine.';
 document.querySelector('#chapter-0 .lead').textContent='Scroll from the detailed RB19 exterior into the Honda RA166E reference study, then separate its major assemblies.';
 document.querySelector('#chapter-0 .hero-stats').innerHTML='<div><strong>1986</strong><small>HONDA ENGINE REFERENCE</small></div><div><strong>V6</strong><small>TWIN TURBO</small></div>';
 document.querySelector('#chapter-1 .chapter-content').innerHTML='<p class="eyebrow">01 / UNDER THE BODYWORK</p><h2>Lift the cover.<br>Look closer.</h2><p>The bodywork lifts away as the camera closes in on the engine study.</p><div class="detail"><span>TWO GENERATIONS / ONE VISUAL JOURNEY</span><p>The RB19 exterior and 1986 Honda engine are combined for this editorial reveal. The RA166E was not the engine installed in the RB19.</p></div>';
 const chapters=[['03 / INTAKE ASSEMBLY','Air, under<br>pressure.','The broad plenum feeds six intake runners. Scroll to lift the intake away from the cylinder heads and reveal the fuel rails and throttle bodies.'],['04 / EXHAUST + TWIN TURBOS','Follow the<br>exhaust.','Exposed exhaust runners feed the two turbochargers. The pipework separates from the engine so you can inspect the paired assemblies.'],['05 / THE MOVING CORE','Six pistons.<br>One crankshaft.','Offset crankpins carry paired connecting rods. Hollow pistons, wrist pins, split bearing caps and shaped counterweights reveal how the mechanism fits together. Select Run mechanism to follow its motion.']];
 chapters.forEach((c,j)=>{document.querySelector(`#chapter-${j+3} .chapter-content`).innerHTML=`<p class="eyebrow">${c[0]}</p><h2>${c[1]}</h2><p>${c[2]}</p>`;});
 ['Complete car','Bodywork reveal','Honda engine','Intake assembly','Twin turbos','Moving core'].forEach((label,i)=>document.querySelectorAll('.chapter-nav a')[i].setAttribute('aria-label',label));

}
const viewport=document.querySelector('#viewport'),hud=document.querySelector('#hud'),ctx=hud.getContext('2d'),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const metrics=window.__F1__={loaded:false,error:null,chapter:0,drawCalls:0,vertices:0};
let renderer,scene,camera,root,orbit=false,angle=0;const groups={},nav=[...document.querySelectorAll('.chapter-nav a')];
const names=['CHASSIS','COVER','ICE','MGUH','MGUK','ES'];
const labels=['COMPLETE ASSEMBLY','BODYWORK REMOVED','V6 / INTERNAL COMBUSTION','MGU-H / TURBO SHAFT','MGU-K / CRANKSHAFT DRIVE','ES / ENERGY STORE'];
const targetStates=[{},{COVER:[0,1.2,0]},{COVER:[0,2.2,0],CHASSIS:[-1,-1.3,0]},{COVER:[0,3,0],CHASSIS:[-1,-2,0],MGUH:[.15,.5,.65]},{COVER:[0,3,0],CHASSIS:[-1,-2,0],MGUH:[.15,.5,-.5],MGUK:[0,.35,.65]},{COVER:[0,3,0],CHASSIS:[-1,-2,0],MGUH:[.2,.5,-.5],MGUK:[0,.25,-.5],ES:[-.15,.5,.5]}];
const state={p:0};
let cutaway=false,running=false,theta=0;const engine={};
const modeButtons=[...document.querySelectorAll('[data-engine-mode]')];
modeButtons.forEach(button=>button.onclick=()=>{cutaway=button.dataset.engineMode==='cutaway';modeButtons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelector('#engine-run').disabled=!cutaway;});
document.querySelector('#engine-run').onclick=e=>{running=!running;e.currentTarget.textContent=running?'Pause mechanism':'Run mechanism';e.currentTarget.setAttribute('aria-pressed',String(running));};
function animateEngine(dt){
 if(!engine.core)return;
 engine.shell.visible=!cutaway;engine.plenum.visible=!cutaway;engine.headers.visible=!cutaway;engine.core.visible=cutaway;
 if(cutaway&&metrics.chapter===2)for(const n of ['MGUH','MGUK','ES'])groups[n].visible=false;
 if(cutaway&&running)theta+=dt*Math.PI*2*Number(document.querySelector('#engine-speed').value)/60;
 engine.crank.rotation.x=theta;let error=0;const axisY=new THREE.Vector3(0,1,0);
 for(const item of engine.pistons){const axis=new THREE.Vector3(0,Math.cos(historic?40*Math.PI/180:Math.PI/4),-item.side*Math.sin(historic?40*Math.PI/180:Math.PI/4)),a=theta+item.idx*Math.PI*2/3;
 const radius=historic?.0254:.0265,pin=new THREE.Vector3(0,radius*Math.cos(a),radius*Math.sin(a)),project=pin.dot(axis),travel=project+Math.sqrt(.11**2-(radius**2-project**2)),origin=new THREE.Vector3(.29+.20*item.idx+(historic?item.side*.008:0),.30,0),wrist=origin.clone().addScaledVector(axis,travel);
 item.piston.position.copy(wrist);item.piston.quaternion.setFromUnitVectors(axisY,axis);item.rod.position.copy(origin).add(pin);const rodVector=wrist.clone().sub(item.rod.position);item.rod.quaternion.setFromUnitVectors(axisY,rodVector.clone().normalize());error=Math.max(error,Math.abs(rodVector.length()-.11));}
 let jointError=0;
 if(historic&&engine.pins?.every(Boolean)){root.updateMatrixWorld(true);for(const item of engine.pistons){const actualPin=engine.pins[item.idx].getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(item.side*.008,0,0));jointError=Math.max(jointError,actualPin.distanceTo(item.rod.getWorldPosition(new THREE.Vector3())),item.rod.localToWorld(new THREE.Vector3(0,.11,0)).distanceTo(item.piston.getWorldPosition(new THREE.Vector3())));}}
 Object.assign(metrics,{jointError,engineMode:cutaway?'cutaway':'assembled',running,crankAngle:theta,pistonCount:engine.pistons.length,rodLengthError:error});
}

function fallback(e){document.querySelector('#loading-model')?.remove();metrics.error=String(e);document.querySelector('#fallback').hidden=false;document.querySelector('.stage').classList.add('failed');document.querySelector('.view-controls').hidden=true}
try{
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));renderer.setClearColor(0,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;viewport.append(renderer.domElement);
 scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(34,1,.05,80);const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;scene.environmentIntensity=.65;pmrem.dispose();scene.add(new THREE.HemisphereLight(0xc8dbff,0x121721,.65));const light=new THREE.DirectionalLight(0xfff8ef,2.5);light.position.set(-3,7,5);light.castShadow=true;light.shadow.mapSize.set(2048,2048);light.shadow.camera.left=-4;light.shadow.camera.right=4;light.shadow.camera.top=4;light.shadow.camera.bottom=-4;light.shadow.normalBias=.012;light.shadow.bias=-.00015;scene.add(light);const rim=new THREE.DirectionalLight(0xc7d8ff,1.2);rim.position.set(3,1,-4);scene.add(rim);
 const floor=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({opacity:.38}));floor.rotation.x=-Math.PI/2;floor.position.y=-.01;floor.receiveShadow=true;scene.add(floor);
 const draco=new DRACOLoader();draco.setDecoderPath(`${import.meta.env.BASE_URL}assets/draco/`);const loader=new GLTFLoader();loader.setDRACOLoader(draco);
 loader.load(`${import.meta.env.BASE_URL}assets/models/${historic?'ra166e-reference':'f1-power-unit'}.glb`,g=>{root=g.scene;scene.add(root);for(const n of names)groups[n]=root.getObjectByName(n);root.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;o.material.forceSinglePass=true;o.userData.baseColor=o.material.color.clone();o.castShadow=true;o.receiveShadow=true;metrics.vertices+=o.geometry.attributes.position.count}});Object.assign(engine,{shell:root.getObjectByName('ENGINE_SHELL'),plenum:root.getObjectByName('INTAKE_PLENUM'),headers:root.getObjectByName('EXHAUST_HEADERS'),core:root.getObjectByName('MOVING_CORE'),crank:root.getObjectByName('CRANKSHAFT'),pistons:[],pins:[0,1,2].map(i=>root.getObjectByName(`CRANKPIN_${i}`))});for(let idx=0;idx<3;idx++)for(const side of [-1,1])engine.pistons.push({idx,side,piston:root.getObjectByName(`PISTON_${idx}_${side}`),rod:root.getObjectByName(`ROD_${idx}_${side}`)});metrics.loaded=true;document.querySelector('#loading-model')?.remove();resize();},undefined,fallback);
}catch(e){fallback(e)}
function resize(){const w=viewport.clientWidth,h=viewport.clientHeight;if(renderer){renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()}hud.width=hud.clientWidth*devicePixelRatio;hud.height=hud.clientHeight*devicePixelRatio}
window.addEventListener('resize',resize);resize();
function updateChapter(i){metrics.chapter=i;if(historic){cutaway=i===5;modeButtons.forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.engineMode==='cutaway')===cutaway)));document.querySelector('#engine-run').disabled=!cutaway;}document.querySelector('.engine-controls').hidden=i<2;document.querySelector('#model-label').textContent=historic?['RB19 / COMPLETE CAR','BODYWORK / EDITORIAL REVEAL','HONDA RA166E / 1986','INTAKE / PLENUM & FUEL RAILS','EXHAUST / TWIN TURBOS','V6 / MOVING CORE'][i]:`0${i+1} / ${labels[i]}`;nav.forEach((a,j)=>a.setAttribute('aria-current',String(i===j)));document.querySelector('#fallback img').src=historic&&i>=2?`${import.meta.env.BASE_URL}assets/textures/ra166e-beauty.png`:`${import.meta.env.BASE_URL}assets/textures/plate-${i}.png`}
updateChapter(0);
const timeline=gsap.timeline({scrollTrigger:{trigger:'.chapters',start:'top top',end:'bottom bottom',scrub:reduced?true:.65,onUpdate:self=>{const i=Math.min(5,Math.round(self.progress*5));if(i!==metrics.chapter)updateChapter(i)}}});timeline?.to(state,{p:5,ease:'none'});
document.querySelector('#rotate').onclick=e=>{orbit=!orbit;e.currentTarget.setAttribute('aria-pressed',String(orbit));e.currentTarget.textContent=orbit?'Stop orbit ◼':'Orbit view ↻'};
document.querySelector('#reset').onclick=()=>{angle=0;orbit=false;document.querySelector('#rotate').setAttribute('aria-pressed','false');document.querySelector('#rotate').textContent='Orbit view ↻'};
const clock=new THREE.Clock();
function draw(){requestAnimationFrame(draw);const dt=Math.min(clock.getDelta(),.05);if(document.hidden)return;const p=reduced?metrics.chapter:state.p,lo=Math.floor(p),hi=Math.min(5,lo+1),u=p-lo,t=u*u*u*(10+u*(-15+6*u));
 if(root){
  for(const n of names){const a=targetStates[lo][n]||[0,0,0],b=targetStates[hi][n]||[0,0,0],o=groups[n];if(!o)continue;o.position.set(...a.map((v,i)=>THREE.MathUtils.lerp(v,b[i],t)));let opacity=n==='COVER'?1-THREE.MathUtils.smoothstep(p,1,1.8):n==='CHASSIS'?1-THREE.MathUtils.smoothstep(p,1.15,2):THREE.MathUtils.smoothstep(p,.35,.95);o.visible=opacity>.015;o.traverse(m=>{if(m.isMesh){m.material.opacity=opacity;m.material.wireframe=false;m.material.emissive?.setHex(0)}})}
  animateEngine(dt);
  if(historic){engine.plenum.position.y=.45*THREE.MathUtils.smoothstep(p,2,3);engine.headers.position.y=.30*THREE.MathUtils.smoothstep(p,3,4);}

  if(orbit)angle+=dt*.25;const zoom=THREE.MathUtils.smoothstep(p,.85,2),distance=THREE.MathUtils.lerp(innerWidth<600?8.2:7.6,cutaway&&(metrics.chapter===2||historic)?1.5:historic?(p>2.5?3.3:2.6):3.5,zoom);const target=cutaway&&(metrics.chapter===2||historic)?new THREE.Vector3(.49,.35,0):new THREE.Vector3(.35*zoom,.4+.16*zoom,0);camera.position.set(target.x+Math.sin(-.7+angle)*distance,target.y+distance*.43,Math.cos(-.7+angle)*distance);camera.lookAt(target);renderer.render(scene,camera);metrics.drawCalls=renderer.info.render.calls;metrics.triangles=renderer.info.render.triangles;metrics.progress=p;
 }
 const w=hud.width,h=hud.height,dpr=devicePixelRatio;ctx.clearRect(0,0,w,h);ctx.strokeStyle='#a3b99924';ctx.lineWidth=dpr;ctx.setLineDash([3*dpr,6*dpr]);ctx.beginPath();ctx.ellipse(w*.53,h*.7,w*.33,h*.12,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
 if(metrics.loaded&&metrics.chapter>1){const n=historic?['','','ICE','INTAKE','TWIN TURBOS','PISTONS'][metrics.chapter]:['','','ICE','MGUH','MGUK','ES'][metrics.chapter],o=historic?(metrics.chapter===3?engine.plenum:metrics.chapter===4?engine.headers:metrics.chapter===5?engine.core:groups.ICE):groups[n];const box=new THREE.Box3().setFromObject(cutaway&&metrics.chapter===2?engine.core:o),v=box.getCenter(new THREE.Vector3()).project(camera);const vx=(v.x*.5+.5)*viewport.clientWidth+viewport.offsetLeft-hud.offsetLeft,vy=(-v.y*.5+.5)*viewport.clientHeight+viewport.offsetTop-hud.offsetTop;ctx.strokeStyle='#d2f87099';ctx.fillStyle='#d2f870';ctx.beginPath();ctx.arc(vx*dpr,vy*dpr,4*dpr,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(vx*dpr,vy*dpr);ctx.lineTo((vx+35)*dpr,(vy-35)*dpr);ctx.lineTo((vx+130)*dpr,(vy-35)*dpr);ctx.stroke();ctx.font=`${11*dpr}px monospace`;ctx.fillText(n==='MGUH'?'TURBO + MGU-H':n,Math.min(vx+42,hud.clientWidth-140)*dpr,Math.max(20,vy-43)*dpr)}
}
draw();
new IntersectionObserver(([e])=>{document.querySelector('.chapter-nav').style.visibility=e.isIntersecting?'visible':'hidden'},{threshold:0}).observe(document.querySelector('#experience'));
