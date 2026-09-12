"""Deterministic tileable engineering material maps, not photographs."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'source-assets/engine-materials';D.mkdir(exist_ok=True)
n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(2026)
u=(x+y)%64;v=(x-y)%64;over=((x+y)//64+(x-y)//64)%2
fiber=np.where(over==0,.5+.5*np.sin(u/64*np.pi),.5+.5*np.sin(v/64*np.pi));micro=np.where(over==0,np.sin(v*2.7),np.sin(u*2.7));h=.5+.22*fiber+.018*micro
shade=19+fiber*22+micro*2
rgb=np.stack([shade*.89,shade*.95,shade],-1).clip(0,255).astype('uint8');Image.fromarray(rgb).save(D/'carbon-base.png')
dy,dx=np.gradient(h);normal=np.stack([-dx*4,-dy*4,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1)[...,None];Image.fromarray(((normal*.5+.5)*255).astype('uint8')).save(D/'carbon-normal.png')
# Fine metallic woven thermal sleeve, much lighter and rougher than carbon.
shade=48+fiber*24+micro*3;Image.fromarray(np.stack([shade,shade*.97,shade*.88],-1).clip(0,255).astype('uint8')).save(D/'heatshield-base.png')
Image.fromarray(np.clip(165+rng.normal(0,8,(n,n)),0,255).astype('uint8')).save(D/'metal-roughness.png')
print('Four reproducible 512px material maps generated')
