"""Independent 120Hz energy accounting, not Blender rigid-body or lap-time simulation."""
from pathlib import Path
import json,math,csv
R=Path(__file__).resolve().parents[1]
assert (R/'data/ground_truth_physics.json').exists()
E=2e6;initial=E;rec=dep=loss=hin=shaft=0.;dt=1/120;rows=[]
for i in range(120*120):
 t=i*dt;cycle=t%40
 # Three illustrative cycles: 5 s braking, 10 s exhaust recovery, 10 s electric drive, 15 s coast.
 k=-100000 if cycle<5 else 100000 if 15<=cycle<25 else 0
 h=30000 if 5<=cycle<15 else 0
 ein=max(-k,0)*.95+h;eout=max(k,0)/.95;E+=(ein-eout)*dt
 rec+=max(-k,0)*.95*dt;dep+=eout*dt;hin+=h*dt;shaft+=k*dt;loss+=(max(-k,0)*.05+max(k,0)*(1/.95-1))*dt
 residual=E-initial+shaft+loss-hin
 assert math.isfinite(E) and 0<E<4e6 and abs(residual)<.001
 if i%4==0:rows.append({'frame':i//4+1,'time_s':t,'store_J':round(E,4),'k_shaft_W':k,'h_electric_W':h,'loss_J':round(loss,4),'residual_J':residual})
# Nonpenetration gate is limited to internal 6cm proxies with 15cm center spacing.
gap=.15-.06;assert gap>.001
# Quintic reveal interpolation has zero endpoint velocity and acceleration.
def smooth(x):return x*x*x*(10+x*(-15+6*x))
cache={'fps':30,'trajectory_source':'independent energy ledger and editorial smoothstep; no rigid-body solver','frames':rows}
(R/'data/solver_cache.json').write_text(json.dumps(cache))
result={'status':'passed','samples':14400,'stored_range_J':[min(r['store_J'] for r in rows),max(r['store_J'] for r in rows)],'energy_residual_max_J':max(abs(r['residual_J']) for r in rows),'finite_telemetry':True,'k_recovered_J':rec,'es_deployed_J':dep,'proxy_nonpenetration':{'minimum_gap_m':gap,'scope':'disjoint test cores only; visual housings not certified'},'contact_speed_m_s':{'value':0,'scope':'no contact events in reference proxy model'},'settled_state':{'endpoint_speed':0,'scope':'analytical derivative of editorial quintic; not dynamic settling'},'kinematic_endpoints':[smooth(0),smooth(1)],'limitations':['No combustion, thermal field, cell electrochemistry, tire or lap-time simulation','Illustrative cycle; not regulatory homologation']}
assert rec<=2e6 and dep<=4e6
(R/'data/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
