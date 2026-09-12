"""120-second film: six Blender studio plates, editorial compositing and system narration.
No Foley; no claim of continuous Blender simulation rendering. Requires Pillow, NumPy and FFmpeg.
"""
from pathlib import Path
import os,json,subprocess,wave,csv,textwrap,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];F=os.environ.get('FFMPEG',str(R.parent/'catch_sim/vendor/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'))
assert json.loads((R/'data/validation.json').read_text())['status']=='passed'
A=R/'data/audio';A.mkdir(exist_ok=True);V=R/'public/assets/video'
chapters=[('ONE UNIT. TWO KINDS OF POWER.','The complete assembly','This study explores the Formula One hybrid architecture used from twenty fourteen through twenty twenty five. A small V six engine works alongside two motor generators and an energy store. The detailed exterior depicts the twenty twenty three Red Bull car, modeled by Redgrund. The internal assembly is educational.'),('UNDER THE BODYWORK','A tightly integrated system','Lift the bodywork to expose the power unit. The engine, turbocharger, electrical machines and battery form an integrated system. Their exact packaging varies by manufacturer. The separation shown here is an editorial animation, not a physical explosion or a service procedure.'),('THE V6 ENGINE','Pressure becomes shaft work','Six cylinders, arranged in a ninety degree V, displace one point six litres. Combustion drives the crankshaft. The reconstructed housings, carbon intake and insulated exhausts follow published Honda engine views. Open the web cutaway to run six pistons and their connecting rods in slow motion. The dimensions and phasing are illustrative.'),('MGU-H AND TURBO','Recover work from the exhaust','The exhaust turbine drives a shaft shared with the compressor and the heat motor generator. The generator converts shaft work into electricity. In motor mode it helps accelerate the compressor and reduce turbo lag. It does not directly convert heat into electricity.'),('THE MGU-K','Recover. Store. Deploy.','The kinetic motor generator couples to the crankshaft. It recovers energy under braking and supplies torque during acceleration. In this era its power limit is one hundred and twenty kilowatts. The energy routes have separate limits: two megajoules to the store and four megajoules from the store per lap.'),('THE ENERGY STORE','The quiet part of going fast','The battery buffers energy while control electronics manage charging and deployment. Four megajoules divided by one hundred and twenty kilowatts gives thirty three point three seconds before losses. Direct heat generator supply is separate. For twenty twenty six, the heat generator was removed and maximum kinetic generator power increased.')]
(R/'docs/film-transcript.md').write_text('# Narration transcript\n\nGeneric macOS Samantha system-generated speech. No Foley or field recordings.\n\n'+'\n\n'.join(f'## {i*20}–{i*20+20}s: {a}\n\n{c}' for i,(a,b,c) in enumerate(chapters)))
audio=np.zeros(120*48000,dtype=np.int16);vtt='WEBVTT\n\n'
def stamp(t):return f'00:{int(t)//60:02d}:{t%60:06.3f}'
for i,(title,subtitle,txt) in enumerate(chapters):
 aiff=A/f'{i}.aiff';wav=A/f'{i}.wav'
 subprocess.run(['say','-v','Samantha','-r','160','-o',str(aiff),txt],check=True)
 subprocess.run([F,'-v','error','-y','-i',str(aiff),'-ar','48000','-ac','1',str(wav)],check=True)
 with wave.open(str(wav)) as w:raw=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).copy()
 if len(raw)>19*48000:
  dest=A/f'{i}-fit.wav';subprocess.run([F,'-v','error','-y','-i',str(wav),'-af',f'atempo={len(raw)/(19*48000):.6f}',str(dest)],check=True)
  with wave.open(str(dest)) as w:raw=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).copy()
 assert 48000<len(raw)<=20*48000 and np.max(np.abs(raw.astype(np.int32)))>100
 start=i*20;audio[start*48000:start*48000+len(raw)]=raw
 sentences=[x.strip()+'.' for x in txt.split('.') if x.strip()];total=sum(map(len,sentences));t=start
 for sentence in sentences:
  end=t+len(raw)/48000*len(sentence)/total;vtt+=f'{stamp(t)} --> {stamp(end)}\n{sentence}\n\n';t=end
(V/'captions.vtt').write_text(vtt)
with wave.open(str(A/'raw.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(audio.tobytes())
subprocess.run([F,'-v','error','-y','-i',str(A/'raw.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','48000','-ac','2',str(A/'narration.wav')],check=True)
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
fonts={n:ImageFont.truetype(fontpath,n) for n in [12,14,16,18,20,24,32,38]}
plates=[Image.open(R/f'public/assets/textures/plate-{i}.png').convert('RGBA') for i in range(6)]
cache=json.loads((R/'data/solver_cache.json').read_text())['frames']
log=(R/'reports/film-encode.log').open('w')
proc=subprocess.Popen([F,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','-','-i',str(A/'narration.wav'),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-t','120','-movflags','+faststart',str(V/'f1-power-unit-master.mp4')],stdin=subprocess.PIPE,stderr=log)
f=(R/'data/timeline_audio_sync.csv').open('w');writer=csv.writer(f);writer.writerow(['frame','fps','timecode','physical_simulation_time_s','camera','phase','voiceover_cue','foley_cue','timing_distinction'])
for frame in range(3600):
 t=frame/30;i=min(5,frame//600);im=Image.new('RGB',(1280,720),(17,22,23));d=ImageDraw.Draw(im);title,subtitle,txt=chapters[i]
 # Slow editorial push on a static Blender plate; never labeled as physical trajectory.
 size=int(910+25*(frame%600)/600);plate=plates[i].resize((size,int(size*1000/1600)),Image.Resampling.BILINEAR);im.paste(plate,(410,115),plate)
 d.text((48,38),'FIELDNOTES / ENGINEERING SERIES 01',font=fonts[14],fill=(210,248,112));d.text((930,38),'2014–2025 HYBRID ARCHITECTURE',font=fonts[12],fill=(155,169,162))
 d.text((48,145),f'0{i+1} / ANATOMY',font=fonts[14],fill=(210,248,112));y=197
 for line in textwrap.wrap(title,19):d.text((48,y),line,font=fonts[32],fill=(238,240,233));y+=40
 for line in textwrap.wrap(subtitle,27):d.text((48,y+22),line,font=fonts[20],fill=(157,173,166));y+=29
 row=cache[frame];d.text((48,445),'ILLUSTRATIVE ENERGY LEDGER',font=fonts[12],fill=(210,248,112))
 for j,(k,val) in enumerate([('Stored energy',f'{row["store_J"]/1e6:.3f} MJ'),('K shaft power',f'{row["k_shaft_W"]/1000:+.0f} kW'),('H electric power',f'{row["h_electric_W"]/1000:.0f} kW')]):d.text((48,477+j*31),f'{k}:  {val}',font=fonts[16],fill=(175,190,182))
 d.text((48,600),'RB19 by Redgrund / CC BY 4.0 / system voice',font=fonts[14],fill=(140,155,147));d.line((48,652,1232,652),fill=(61,75,64));d.line((48,652,48+1184*frame/3599,652),fill=(210,248,112),width=3)
 tc=f'00:{int(t)//60:02d}:{int(t)%60:02d}:{frame%30:02d}';d.text((48,678),f'{tc}  /  FRAME {frame+1:04d}  /  30 FPS',font=fonts[12],fill=(170,182,173));d.text((755,678),'EDITORIAL PLATES · SYNTHETIC TELEMETRY · NOT A RACING LAP',font=fonts[12],fill=(170,182,173))
 if frame==1200:im.save(V/'poster.jpg',quality=92)
 proc.stdin.write(im.tobytes());writer.writerow([frame+1,30,tc,t,'Exhibit_camera / editorial plate push',subtitle,txt if frame%600==0 else '', 'none','ledger seconds; disassembly timing editorial, independent of ledger'])
 if frame%900==0:print('Film frame',frame,flush=True)
proc.stdin.close();assert proc.wait()==0;log.close();f.close();print('Master complete: 3600 frames',flush=True)
