from pathlib import Path
import os,subprocess,json,re,csv
R=Path(__file__).resolve().parents[1];F=os.environ.get('FFMPEG',str(R.parent/'catch_sim/vendor/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'));p=R/'public/assets/video/f1-power-unit-master.mp4'
def run(args):return subprocess.run([F,*args],capture_output=True,text=True)
r=run(['-hide_banner','-v','info','-xerror','-err_detect','explode','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-']);assert r.returncode==0,r.stderr
(R/'reports/film-decode.log').write_text(r.stderr)
frames=re.findall(r'frame=\s*(\d+)',r.stderr);assert int(frames[-1])==3600
assert '00:02:00.00' in r.stderr and '1280x720' in r.stderr and 'h264' in r.stderr and 'aac' in r.stderr and '48000 Hz' in r.stderr
r2=run(['-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);stats=json.loads(r2.stderr[r2.stderr.rfind('{'):r2.stderr.rfind('}')+1]);assert -18<float(stats['input_i'])<-14 and float(stats['input_tp'])<0,stats
rows=list(csv.DictReader((R/'data/timeline_audio_sync.csv').open()));assert len(rows)==3600 and rows[-1]['timecode']=='00:01:59:29'
report={'status':'passed','duration_s':120,'frames':3600,'fps':30,'dimensions':[1280,720],'codec':'H.264 / AAC','audio_sample_rate_Hz':48000,'strict_decode':'passed','integrated_loudness_LUFS':float(stats['input_i']),'true_peak_dBTP':float(stats['input_tp']),'clipping':False,'narration':'macOS Samantha system-generated','foley':'none','csv_rows':len(rows)}
(R/'reports/media-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
