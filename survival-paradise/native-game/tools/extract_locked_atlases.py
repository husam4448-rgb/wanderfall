#!/usr/bin/env python3
"""Decode ONLY the exact two PNG bitstreams embedded in approved V31.
No image processing, regeneration, scaling or pixel mutation is performed.
"""
import re,base64,hashlib, pathlib,sys,struct,json
base=pathlib.Path(__file__).resolve().parents[2]
src=base/'V31_original.html'
if not src.exists(): raise SystemExit('Approved V31 baseline missing: '+str(src))
raw=src.read_text(encoding='utf-8')
matches=re.findall(r"const (BODY_PNG|GEAR_PNG)='data:image/png;base64,([A-Za-z0-9+/=]+)'",raw)
assets=dict(matches)
assert len(assets)==2 and {'BODY_PNG','GEAR_PNG'}==set(assets), 'V31 canonical atlas data unavailable'
dst=pathlib.Path(__file__).resolve().parents[1]/'app/src/main/assets'
dst.mkdir(parents=True,exist_ok=True)
out={}
for key,name,expect in [('BODY_PNG','body.png',(1040,160)),('GEAR_PNG','gear.png',(3120,480))]:
    blob=base64.b64decode(assets[key],validate=True)
    assert blob[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',blob[16:24]); assert (w,h)==expect, (key,w,h)
    (dst/name).write_bytes(blob)
    out[name]={'sha256':hashlib.sha256(blob).hexdigest(),'width':w,'height':h,'size':len(blob)}
(dst/'atlas_provenance.json').write_text(json.dumps(out,indent=2)+'\n')
print('VERIFIED LOCKED V31 PNG ASSETS',out)
