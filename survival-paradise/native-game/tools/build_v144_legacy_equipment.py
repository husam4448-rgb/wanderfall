#!/usr/bin/env python3
"""V144 deterministic legacy gear artwork. Original pixels/alpha are never modified on disk."""
from PIL import Image, ImageDraw
from pathlib import Path
import json, zipfile, io, hashlib
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source'
OUT=ROOT/'generated'
NATIVE_ASSETS=ROOT.parent/'app'/'src'/'main'/'assets'
PROFILES=[
 ('canvas_work_jacket','torsos','10_workwear.png','#292b20','#787b55','#b7ab72','#647779'),
 ('weatherproof_field_coat','torsos','17_winter.png','#172d32','#3a6263','#8da59a','#354550'),
 ('plate_carrier','torsos','07_armor.png','#222a24','#546253','#a2a489','#647477'),
 ('cargo_trousers','pants','11_military.png','#352e24','#71664c','#b6a16b','#726957'),
 ('ripstop_trousers','pants','19_ranger.png','#283437','#526868','#92a29b','#727d7d'),
 ('tactical_trousers','pants','07_armor.png','#1e272c','#424f53','#8d9792','#6c7a81'),
 ('steel_toe_work_boots','boots','03_Reinforced_Work.png','#292b30','#646264','#a89b85','#a5afb1'),
 ('trail_boots','boots','04_Trail.png','#29302d','#696d56','#a5ac84','#7daca0'),
 ('tactical_combat_boots','boots','01_Combat.png','#1b2428','#3e4b50','#869294','#778b86'),
]
def rgb(h):return tuple(bytes.fromhex(h.replace('#','')))
def ramp(lo,mid,hi,x):
    x=np.clip(x,0,1)
    if x<.5:t=x*2;a=lo;b=mid
    else:t=(x-.5)*2;a=mid;b=hi
    return np.array([round(a[k]*(1-t)+b[k]*t) for k in range(3)],np.uint8)
def load_source(group,file):
    local=SOURCE/group/file
    if local.is_file():return Image.open(local).convert('RGBA')
    archive=NATIVE_ASSETS/('sp_v133_boots.zip' if group=='boots' else 'sp_v139_outfits.zip')
    member=file if group=='boots' else f'{group}/{file}'
    with zipfile.ZipFile(archive) as z:
        return Image.open(io.BytesIO(z.read(member))).convert('RGBA')
def generate(profile):
    name,group,source,pal_dark,pal_mid,pal_light,metal=profile
    src=load_source(group,source)
    arr=np.array(src).copy();h,w=arr.shape[:2]
    alpha=arr[:,:,3].copy()
    old=arr[:,:,:3].astype(np.float32)
    ylum=.2126*old[:,:,0]+.7152*old[:,:,1]+.0722*old[:,:,2]
    maxv=old.max(axis=2);minv=old.min(axis=2)
    sat=np.divide(maxv-minv,np.maximum(1,maxv))
    shadow=rgb(pal_dark);middle=rgb(pal_mid);light=rgb(pal_light);metal=rgb(metal)
    norm=np.clip((ylum-28)/192,0,1)
    out=np.zeros((h,w,3),dtype=np.uint8)
    for yy in range(h):
        for xx in range(w):
            if alpha[yy,xx]==0:continue
            level=float(norm[yy,xx]);px=old[yy,xx]
            if ylum[yy,xx]<55:
                out[yy,xx]=px;continue
            mapped=ramp(shadow,middle,light,level)
            if sat[yy,xx]<.23 and ylum[yy,xx]>95:
                mapped=np.array([min(255,int(c*(.66+.65*level))) for c in metal],dtype=np.uint8)
            out[yy,xx]=np.clip(mapped*.93+px*.07,0,255).astype(np.uint8)
    arr[:,:,:3]=out
    internal=(alpha>200)&(ylum>58)
    canvas=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(canvas)
    def r(x1,y1,x2,y2,color):
        d.rectangle((round(x1*w),round(y1*h),round(x2*w),round(y2*h)),fill=rgb(color)+(255,))
    def line(pts,color,width=2):
        d.line([(round(x*w),round(y*h)) for x,y in pts],fill=rgb(color)+(255,),width=width,joint='curve')
    if name=='canvas_work_jacket':
        r(.08,.15,.27,.27,'#615b43');r(.70,.15,.89,.27,'#615b43')
        line([(.49,.09),(.49,.82)],'#3d4034',3);line([(.51,.12),(.51,.81)],'#b0a178',2)
        r(.13,.51,.33,.57,'#c4b06e');r(.66,.51,.84,.57,'#c4b06e')
        line([(.12,.65),(.37,.65)],'#292e2a',3);line([(.64,.65),(.85,.65)],'#292e2a',3)
        r(.14,.17,.26,.21,'#b9a676');r(.74,.17,.85,.21,'#b9a676')
    elif name=='weatherproof_field_coat':
        line([(.51,.13),(.51,.87)],'#243e43',4);line([(.54,.19),(.54,.85)],'#85aaa0',2)
        r(.16,.58,.29,.63,'#273b3c');r(.74,.58,.86,.63,'#273b3c')
        line([(.20,.60),(.33,.52)],'#9aafa3',2)
        line([(.70,.52),(.83,.61)],'#9aafa3',2)
        r(.67,.30,.79,.36,'#596c6a');r(.40,.79,.58,.83,'#2c444a')
    elif name=='plate_carrier':
        r(.32,.34,.65,.43,'#697b71')
        line([(.35,.34),(.44,.24),(.57,.24),(.64,.34)],'#c2b69d',2)
        r(.15,.62,.32,.68,'#566c58');r(.69,.62,.84,.68,'#566c58')
        for xi in [.16,.24,.33,.66,.75,.83]:line([(xi,.72),(xi,.81)],'#9ca18b',2)
        r(.45,.56,.56,.61,'#b0a081')
        line([(.12,.88),(.88,.88)],'#302f2b',4)
    elif name=='cargo_trousers':
        r(.13,.39,.37,.45,'#a59a68');r(.64,.40,.87,.46,'#a59a68')
        r(.16,.49,.36,.54,'#685e46');r(.68,.5,.85,.54,'#685e46')
        line([(.15,.58),(.37,.58)],'#2f332c',2)
        line([(.63,.59),(.85,.59)],'#2f332c',2)
        r(.27,.29,.33,.33,'#b5a97b');r(.72,.29,.78,.33,'#b5a97b')
        line([(.46,.17),(.55,.17)],'#c6b385',3)
    elif name=='ripstop_trousers':
        for xx in np.arange(.12,.91,.075):line([(xx,.45),(xx,.92)],'#6e8783',1)
        for yy in np.arange(.47,.94,.105):line([(.12,yy),(.90,yy)],'#374a4b',1)
        line([(.13,.74),(.38,.74)],'#a7b5a6',2)
        line([(.62,.74),(.86,.74)],'#a7b5a6',2)
        r(.64,.31,.83,.35,'#3c514e')
    elif name=='tactical_trousers':
        r(.16,.35,.37,.44,'#596e72');r(.64,.35,.85,.44,'#596e72')
        line([(.12,.66),(.36,.66)],'#949e9f',2)
        line([(.64,.66),(.90,.66)],'#949e9f',2)
        r(.17,.75,.34,.81,'#26343b');r(.68,.75,.83,.81,'#26343b')
        r(.47,.16,.54,.22,'#a39c82')
    elif name=='steel_toe_work_boots':
        r(.69,.66,.91,.74,'#8a999a')
        line([(.66,.59),(.96,.59)],'#c0b9a6',2)
        line([(.27,.31),(.36,.49)],'#909b92',2)
        line([(.16,.76),(.87,.76)],'#313a41',3)
    elif name=='trail_boots':
        line([(.33,.23),(.43,.30),(.36,.38),(.46,.44)],'#b3c7b0',2)
        r(.28,.15,.35,.23,'#4a8a81')
        line([(.42,.60),(.79,.60)],'#b5ac81',2)
        line([(.18,.79),(.88,.79)],'#3c4946',3)
    elif name=='tactical_combat_boots':
        line([(.35,.21),(.44,.25),(.34,.32),(.43,.36),(.34,.43)],'#9da8a0',2)
        r(.37,.12,.45,.18,'#647d75')
        line([(.14,.75),(.87,.75)],'#81908c',2)
        line([(.13,.83),(.84,.83)],'#303b42',2)
    detail=np.array(canvas)
    active=internal&(detail[:,:,3]>0)
    arr[active,:3]=detail[active,:3]
    arr[:,:,3]=alpha
    dark=(ylum<55)&(alpha>0)
    arr[dark,:3]=np.array(src)[dark,:3]
    final=Image.fromarray(arr,'RGBA')
    assert final.size==src.size
    assert final.getchannel('A').tobytes()==src.getchannel('A').tobytes()
    assert np.array_equal(np.array(final)[:,:,:3][dark],np.array(src)[:,:,:3][dark])
    return final
def main():
    OUT.mkdir(exist_ok=True)
    report={}
    for i,prof in enumerate(PROFILES):
        name,group,file,*_=prof
        target=OUT/group/(name+'.png')
        target.parent.mkdir(parents=True,exist_ok=True)
        src=load_source(group,file);image=generate(prof)
        image.save(target,optimize=True)
        count=int(np.count_nonzero(np.any(np.array(src)[:,:,:3]!=np.array(image)[:,:,:3],axis=2)&(np.array(src)[:,:,3]>0)))
        report[name]={'type':group,'source':file,'width':src.width,'height':src.height,
                      'alpha_exact':src.getchannel('A').tobytes()==image.getchannel('A').tobytes(),
                      'different_pixels':count,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2))
    archive=NATIVE_ASSETS/'sp_v144_legacy_equipment.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,9) as z:
        for i,prof in enumerate(PROFILES):
            name,group,*_=prof
            index=20+i if group=='torsos' else 17+i if group=='pants' else i-1
            z.write(OUT/group/(name+'.png'),f'{group}/{index:02d}_{name}.png')
        z.write(OUT/'validation.json','validation.json')
    return report
if __name__=='__main__':
    print(json.dumps(main(),indent=2))
