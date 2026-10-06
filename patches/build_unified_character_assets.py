#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFilter
import base64, json, re, hashlib, sys, math
import numpy as np

repo = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
game = Path(sys.argv[2] if len(sys.argv) > 2 else 'game')
runtime = game / 'scripts' / 'art' / 'd2d29_minimal_token_runtime.gd'
if not runtime.is_file():
    raise SystemExit('PC22 runtime not found: ' + str(runtime))
text = runtime.read_text(encoding='utf-8')
if 'PLAYER CHARACTERS V22' not in text:
    raise SystemExit('Expected PlayerCharacters_v22 canonical runtime')

src_spec = repo / 'assets' / 'authored2d' / 'npc_specializations'
src_faces = repo / 'assets' / 'authored2d' / 'npc_faces'
out = repo / 'assets' / 'authored2d' / 'unified_character'
roles = ['Trader','Medic','Mechanic','Guard','Bandit','Civilian']
sexes = ['Male','Female']

for d in [
    out/'core'/'male', out/'core'/'female', out/'generic', out/'roles'
]:
    d.mkdir(parents=True, exist_ok=True)

def embedded(name):
    m = re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"', text)
    if not m:
        raise SystemExit('Missing embedded asset '+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')

pack = embedded('GEAR_PACK_B64')
vest = embedded('GEAR_VEST_B64')
leg_rear = embedded('GEAR_LEGS_B64')
leg_front = embedded('GEAR_LEGS_FRONT_B64')
boot = embedded('GEAR_BOOT_B64')
glove = embedded('GEAR_GLOVE_B64')
helmet = embedded('GEAR_HELMET_B64')
head_m = embedded('HEAD_RIGHT_B64')
female_boot = embedded('FEMALE_BASE_BOOT_B64')

pc = game / 'assets' / 'playercharacters'
required = [
    pc/'female_head_right_pc21.png', pc/'female_torso_right_pc21.webp',
    pc/'female_leg_base_right_pc21.webp', pc/'female_leg_base_front_right_pc21.webp',
    pc/'female_leg_gear_right_pc21.webp', pc/'female_leg_gear_front_right_pc21.webp'
]
for p in required:
    if not p.is_file():
        raise SystemExit('Missing PC22 generated asset '+str(p))

female_head = Image.open(required[0]).convert('RGBA')
female_torso = Image.open(required[1]).convert('RGBA')
female_leg_base_rear = Image.open(required[2]).convert('RGBA')
female_leg_base_front = Image.open(required[3]).convert('RGBA')
female_leg_gear_rear = Image.open(required[4]).convert('RGBA')
female_leg_gear_front = Image.open(required[5]).convert('RGBA')

def solid_from_alpha(img, rgb):
    a = np.array(img.convert('RGBA'))
    o = np.zeros_like(a)
    o[:,:,:3] = np.array(rgb, dtype=np.uint8)
    o[:,:,3] = a[:,:,3]
    return Image.fromarray(o, 'RGBA')

male_torso_base = solid_from_alpha(vest, (78,89,75))
male_leg_base_rear = solid_from_alpha(leg_rear, (57,66,71))
male_leg_base_front = solid_from_alpha(leg_front, (57,66,71))
male_boot_base = solid_from_alpha(boot, (45,48,48))
male_hand_base = solid_from_alpha(glove, (201,142,104))
female_hand_base = solid_from_alpha(glove, (208,154,117))

core = {
    out/'core'/'male'/'head_right.png': head_m,
    out/'core'/'male'/'torso_base.png': male_torso_base,
    out/'core'/'male'/'leg_rear_base.png': male_leg_base_rear,
    out/'core'/'male'/'leg_front_base.png': male_leg_base_front,
    out/'core'/'male'/'boot_base.png': male_boot_base,
    out/'core'/'male'/'hand_base.png': male_hand_base,
    out/'core'/'female'/'head_right.png': female_head,
    out/'core'/'female'/'torso_base.png': female_torso,
    out/'core'/'female'/'leg_rear_base.png': female_leg_base_rear,
    out/'core'/'female'/'leg_front_base.png': female_leg_base_front,
    out/'core'/'female'/'boot_base.png': female_boot,
    out/'core'/'female'/'hand_base.png': female_hand_base,
}
for path,img in core.items():
    img.save(path, optimize=True)

for name,img in {
    'pack.png':pack,'torso.png':vest,'leg_rear.png':leg_rear,'leg_front.png':leg_front,
    'boot.png':boot,'glove.png':glove,'helmet.png':helmet
}.items():
    img.save(out/'generic'/name, optimize=True)

ROLE_COLORS = {
    'Trader':   {'main':(137,101,62), 'accent':(183,145,91), 'dark':(67,54,39)},
    'Medic':    {'main':(154,157,150), 'accent':(184,43,49), 'dark':(65,70,69)},
    'Mechanic': {'main':(68,89,105), 'accent':(202,125,42), 'dark':(48,50,48)},
    'Guard':    {'main':(66,73,67), 'accent':(86,98,74), 'dark':(35,39,39)},
    'Bandit':   {'main':(108,69,54), 'accent':(137,52,42), 'dark':(50,38,34)},
    'Civilian': {'main':(77,88,95), 'accent':(108,119,123), 'dark':(52,49,45)},
}

def obj_crop(img):
    b = img.getchannel('A').getbbox()
    return img.crop(b) if b else img

def transfer(target, source, strength=0.78):
    tgt = target.convert('RGBA')
    tb = tgt.getchannel('A').getbbox()
    if not tb:
        return tgt
    src = obj_crop(source.convert('RGBA'))
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    src = ImageOps.fit(src, (tw,th), method=Image.Resampling.LANCZOS)
    sa = np.array(src).astype(np.float32)
    ta = np.array(tgt).astype(np.float32)
    tc = ta[tb[1]:tb[3],tb[0]:tb[2],:]
    alpha = sa[:,:,3:4]/255.0
    pix = sa[:,:,:3][sa[:,:,3]>30]
    med = np.median(pix,axis=0) if len(pix) else np.array([100,90,75],dtype=np.float32)
    srgb = sa[:,:,:3]*alpha + med.reshape(1,1,3)*(1-alpha)
    crgb = tc[:,:,:3]
    lum = 0.2126*crgb[:,:,0]+0.7152*crgb[:,:,1]+0.0722*crgb[:,:,2]
    active = tc[:,:,3]>20
    mean = float(lum[active].mean()) if np.any(active) else 128.0
    shade = np.clip(lum/max(mean,1.0),0.55,1.45)[:,:,None]
    textured = np.clip(srgb*shade,0,255)
    out_rgb = np.clip(strength*textured+(1-strength)*crgb,0,255)
    outa = ta.copy()
    outa[tb[1]:tb[3],tb[0]:tb[2],:3] = out_rgb
    outa[:,:,3] = ta[:,:,3]
    return Image.fromarray(outa.astype(np.uint8),'RGBA')

def tint_canonical(target, main, accent, kind, sex):
    arr = np.array(target.convert('RGBA')).astype(np.float32)
    alpha = arr[:,:,3]
    lum = (0.2126*arr[:,:,0]+0.7152*arr[:,:,1]+0.0722*arr[:,:,2])/255.0
    main = np.array(main,dtype=np.float32)
    rgb = main.reshape(1,1,3)*(0.55+0.75*lum[:,:,None])
    rgb = np.clip(rgb,0,255)
    outa = np.dstack([rgb,alpha]).astype(np.uint8)
    img = Image.fromarray(outa,'RGBA')
    d = ImageDraw.Draw(img,'RGBA')
    if kind == 'pack':
        w,h=img.size
        if main.tolist() == list(ROLE_COLORS['Medic']['main']):
            d.rectangle((w*0.42,h*0.30,w*0.58,h*0.36), fill=accent+(220,))
            d.rectangle((w*0.47,h*0.25,w*0.53,h*0.41), fill=accent+(220,))
        elif main.tolist() == list(ROLE_COLORS['Mechanic']['main']):
            d.rectangle((w*0.22,h*0.38,w*0.28,h*0.70), fill=accent+(190,))
            d.rectangle((w*0.68,h*0.44,w*0.74,h*0.72), fill=accent+(190,))
        elif main.tolist() == list(ROLE_COLORS['Bandit']['main']):
            d.polygon([(w*.18,h*.36),(w*.42,h*.30),(w*.46,h*.46),(w*.25,h*.52)], fill=accent+(135,))
        elif main.tolist() == list(ROLE_COLORS['Trader']['main']):
            d.rectangle((w*.18,h*.55,w*.78,h*.62), fill=accent+(85,))
    elif kind == 'glove':
        w,h=img.size
        d.rectangle((w*.06,h*.46,w*.27,h*.59), fill=accent+(90,))
    a = target.getchannel('A')
    img.putalpha(a)
    return img

def normalize_head(src):
    src=src.convert('RGBA')
    a=np.array(src.getchannel('A'))
    counts=(a>10).sum(axis=1)
    arr=np.array(src)
    for y,c in enumerate(counts):
        if c > src.width*0.85:
            arr[y,:,:]=0
    src=Image.fromarray(arr,'RGBA')
    b=src.getchannel('A').getbbox()
    if not b:
        raise RuntimeError('empty head')
    obj=src.crop(b)
    scale=min(92/obj.width,90/obj.height)
    obj=obj.resize((max(1,int(obj.width*scale)),max(1,int(obj.height*scale))),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(96,96),(0,0,0,0))
    canvas.alpha_composite(obj,((96-obj.width)//2,max(1,92-obj.height)))
    return canvas

def utility_canvas(role, sex):
    im=Image.new('RGBA',(128,128),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    dark=(38,42,41,255); metal=(112,118,117,255)
    r=role; female=sex=='Female'
    if r=='Trader' and not female:
        d.rounded_rectangle((25,25,62,102),radius=5,fill=(133,95,58,255),outline=dark,width=4)
        d.rectangle((31,34,56,94),fill=(213,202,171,255))
        d.rounded_rectangle((37,20,51,31),radius=3,fill=metal,outline=dark,width=2)
        for y in range(44,90,8): d.line((34,y,53,y),fill=(110,100,81,210),width=2)
        d.rectangle((58,48,64,78),fill=(69,72,68,255))
    elif r=='Trader':
        d.rounded_rectangle((48,28,81,101),radius=8,fill=(55,63,61,255),outline=dark,width=4)
        d.rectangle((55,39,74,51),fill=(169,112,38,255))
        d.line((59,28,54,10),fill=metal,width=4)
        for yy in range(60,90,8):
            for xx in range(55,75,8): d.ellipse((xx,yy,xx+4,yy+4),fill=(125,132,128,255))
    elif r=='Medic':
        x0,x1=(22,106) if not female else (29,101)
        y0,y1=(45,103) if not female else (48,101)
        d.rounded_rectangle((x0,y0,x1,y1),radius=10,fill=(164,42,48,255),outline=(84,28,31,255),width=5)
        d.arc((49,32,79,58),180,360,fill=(83,76,67,255),width=5)
        d.rectangle((59,58,69,88),fill=(230,227,210,255)); d.rectangle((49,68,79,78),fill=(230,227,210,255))
    elif r=='Mechanic' and not female:
        pts=[(8,48),(26,48),(37,57),(87,57),(99,45),(112,50),(101,66),(87,69),(37,69),(26,78),(8,78),(18,64)]
        d.polygon(pts,fill=(142,147,143,255),outline=dark)
        d.ellipse((14,57,28,71),fill=(47,52,51,255))
    elif r=='Mechanic':
        d.line((64,64,42,96),fill=(178,52,43,255),width=10); d.line((64,64,84,97),fill=(178,52,43,255),width=10)
        d.line((64,64,49,30),fill=metal,width=8); d.line((64,64,80,30),fill=metal,width=8)
        d.ellipse((58,58,70,70),fill=dark)
    elif r=='Guard' and not female:
        d.rectangle((17,55,108,65),fill=(52,57,56,255),outline=dark,width=3)
        d.rectangle((46,64,60,85),fill=(45,49,48,255),outline=dark,width=3)
        d.rectangle((68,64,77,77),fill=(44,48,47,255))
        d.rectangle((20,48,55,56),fill=(63,69,67,255))
        d.rectangle((91,51,117,59),fill=(40,44,43,255))
    elif r=='Guard':
        d.rounded_rectangle((42,36,87,71),radius=8,fill=(59,63,62,255),outline=dark,width=4)
        d.polygon([(58,68),(78,68),(73,106),(57,106)],fill=(48,52,51,255),outline=dark)
        d.rectangle((83,47,106,56),fill=(45,49,48,255))
    elif r=='Bandit' and not female:
        d.rectangle((12,55,112,66),fill=(77,52,38,255),outline=(40,32,27,255),width=3)
        d.rectangle((29,51,69,59),fill=(93,62,43,255))
        d.rectangle((52,64,67,86),fill=(65,45,35,255))
        d.rectangle((89,52,119,60),fill=(60,48,42,255))
    elif r=='Bandit':
        d.polygon([(25,58),(90,47),(116,58),(90,68)],fill=(128,132,127,255),outline=dark)
        d.rounded_rectangle((16,55,43,72),radius=4,fill=(89,57,40,255),outline=dark,width=3)
        d.ellipse((21,59,27,65),fill=(184,137,75,255))
    elif r=='Civilian' and not female:
        d.rounded_rectangle((22,55,106,73),radius=9,fill=(67,73,72,255),outline=dark,width=4)
        d.polygon([(101,52),(118,58),(118,71),(101,76)],fill=(194,157,61,255))
        d.line((33,58,33,70),fill=(130,137,134,255),width=3)
    else:
        d.rounded_rectangle((48,22,82,106),radius=10,fill=(189,198,194,230),outline=(75,88,88,255),width=4)
        d.rectangle((53,58,77,90),fill=(91,135,165,180))
        d.rectangle((55,13,75,28),fill=(80,86,84,255)); d.rectangle((58,8,72,15),fill=(65,70,69,255))
    return im

utility_sizes = {
    ('Trader','Male'):[14,18],('Trader','Female'):[10,15],
    ('Medic','Male'):[16,13],('Medic','Female'):[15,13],
    ('Mechanic','Male'):[21,7],('Mechanic','Female'):[13,14],
    ('Guard','Male'):[30,10],('Guard','Female'):[15,11],
    ('Bandit','Male'):[30,10],('Bandit','Female'):[20,7],
    ('Civilian','Male'):[19,8],('Civilian','Female'):[9,15]
}

role_entries={}
for role in roles:
    role_key=role.lower()
    role_entries[role_key]={}
    for sex in sexes:
        sex_key=sex.lower()
        target=out/'roles'/role_key/sex_key
        target.mkdir(parents=True, exist_ok=True)
        face=src_faces/f'SP_NPC_{role}_{sex}_Face_Right.png'
        if not face.is_file():
            raise SystemExit('Missing role face '+str(face))
        normalize_head(Image.open(face)).save(target/'head.png', optimize=True)
        torso_src=src_spec/f'SP_NPC_{role}_{sex}_Torso_Right.png'
        pants_src=src_spec/f'SP_NPC_{role}_{sex}_Pants_Right.png'
        boots_src=src_spec/f'SP_NPC_{role}_{sex}_Boots_Right.png'
        for p in [torso_src,pants_src,boots_src]:
            if not p.is_file(): raise SystemExit('Missing specialization source '+str(p))
        torso_target=female_torso if sex=='Female' else vest
        transfer(torso_target,Image.open(torso_src).convert('RGBA'),0.82).save(target/'torso.png',optimize=True)
        pants=Image.open(pants_src).convert('RGBA')
        rear_target=female_leg_gear_rear if sex=='Female' else leg_rear
        front_target=female_leg_gear_front if sex=='Female' else leg_front
        transfer(rear_target,pants,0.60).save(target/'pants_rear.png',optimize=True)
        transfer(front_target,pants,0.60).save(target/'pants_front.png',optimize=True)
        transfer(boot,Image.open(boots_src).convert('RGBA'),0.78).save(target/'boots.png',optimize=True)
        palette=ROLE_COLORS[role]
        tint_canonical(pack,palette['main'],palette['accent'],'pack',sex).save(target/'backpack.png',optimize=True)
        tint_canonical(glove,palette['main'],palette['accent'],'glove',sex).save(target/'glove.png',optimize=True)
        utility_canvas(role,sex).save(target/'utility.png',optimize=True)
        role_entries[role_key][sex_key]={
            'head':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/head.png',
            'torso':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/torso.png',
            'pants_rear':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/pants_rear.png',
            'pants_front':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/pants_front.png',
            'boots':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/boots.png',
            'backpack':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/backpack.png',
            'glove':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/glove.png',
            'utility':f'res://assets/authored2d/unified_character/roles/{role_key}/{sex_key}/utility.png',
            'utility_draw_size':utility_sizes[(role,sex)],
            'utility_grip_px':[64,64]
        }

canonical={
  'standard_id':'PlayerCharacters_v22','source_commit':'9304254920ad732c2522384b91822618931347bd',
  'facing':{'authored':'right','left':'runtime_mirror'},
  'shared_motion':{'walk_stride':5.0,'run_stride':8.0,'walk_bob':1.3,'run_bob':2.2,'walk_sway':1.0,'run_sway':1.8,'idle_breath_amplitude':0.42,'head_tilt_clamp_rad':0.34,'aim_angle_clamp_rad':1.53938},
  'weapon_socket':{'pivot_from_base':[6.0,-2.0],'dominant_hand_from_pivot':[3.0,4.0],'support_hand_from_pivot':[16.0,2.0],'recoil_local_x':-1.45},
  'male':{'torso_center':[0.0,-4.0],'torso_size':[26.2,29.6],'neck_socket':[1.6,-16.0],'head_size':[16.9,18.4],'backpack_center':[-10.5,-4.0],'backpack_size':[25.0,31.0],'hip_span':3.8,'knee_span':4.9,'ankle_span':5.4,'hip_y':11.0,'knee_y':18.0,'ankle_y':25.0,'leg_size':[16.5,26.5],'boot_offset':[0.4,6.8],'boot_size':[17.0,12.8],'hand_size':[10.9,10.5]},
  'female':{'torso_center':[0.05,-3.05],'torso_size':[27.0,27.5],'neck_socket':[1.6,-14.55],'head_size':[16.9,18.4],'backpack_center':[-8.4,-4.0],'backpack_size':[19.8,28.8],'hip_span':3.05,'knee_span':4.15,'ankle_span':4.60,'hip_y':10.05,'knee_y':18.8,'ankle_y':26.4,'leg_size':[19.8,26.5],'boot_offset':[1.0,6.2],'boot_size':[14.4,10.6],'hand_size':[10.0,9.8]}
}
manifest={'version':'1.0','canonical':canonical,'roles':role_entries,'policy':{'same_player_npc_rig':True,'base_body_always_drawn':True,'equipment_overlay':True,'role_is_default_loadout':True,'left_is_runtime_mirror':True}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(out/'canonical_pc22.json').write_text(json.dumps(canonical,indent=2),encoding='utf-8')

files=[]; failures=[]
for p in sorted(out.rglob('*.png')):
    im=Image.open(p).convert('RGBA')
    bb=im.getchannel('A').getbbox()
    rec={'path':str(p.relative_to(repo)),'size':list(im.size),'alpha_bbox':list(bb) if bb else None,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    files.append(rec)
    if bb is None: failures.append({'path':rec['path'],'reason':'empty alpha'})
(out/'qa_asset_report.json').write_text(json.dumps({'files':files,'failures':failures},indent=2),encoding='utf-8')
if failures:
    raise SystemExit('Asset QA failures: '+json.dumps(failures))
print('UNIFIED_ASSETS_OK count=%d' % len(files))
