from PIL import Image, ImageDraw
from pathlib import Path
import hashlib, json, zipfile
HERE=Path(__file__).resolve().parent
SRC=HERE/'heads/133.png'
OUT=HERE/'head133-production'
OUT.mkdir(parents=True,exist_ok=True)
original=Image.open(SRC).convert('RGBA')
W,H=original.size
assert (W,H)==(124,135), (W,H)
INK='#0e0d0c'; DARK='#292820'; O1='#746c51'; O2='#978b65'; O3='#b9a77d'; HIGHLIGHT='#d1c49e'
BLACK='#0b0c0f'; SHADOW='#202127'; GRAPH='#36383f'; GREY='#52555d'; STEEL='#96989a'; LIGHT='#c3c1b7'
def new():return Image.new('RGBA',(W,H),(0,0,0,0))
def shape(im,pts,fill,stroke=INK,width=2):
 d=ImageDraw.Draw(im);d.polygon(pts,fill=fill);d.line(pts+[pts[0]],fill=stroke,width=width,joint='curve')
def line(im,pts,color,width=1):ImageDraw.Draw(im).line(pts,fill=color,width=width,joint='curve')
def rect(im,xy,fill,outline=None,width=1):ImageDraw.Draw(im).rectangle(xy,fill=fill,outline=outline,width=width)
helmet=new()
shape(helmet,[(11,60),(13,41),(21,25),(34,11),(50,4),(72,2),(92,8),(109,18),(123,33),(130,48),(129,58),(110,60),(92,57),(73,59),(57,65),(33,70),(17,68)],'#4c4635')
shape(helmet,[(16,58),(18,40),(27,25),(37,15),(53,8),(70,6),(89,11),(107,21),(120,34),(126,49),(108,54),(91,52),(73,53),(57,59),(34,65),(20,63)],O2,stroke='#1b1914')
shape(helmet,[(28,41),(36,26),(49,16),(65,11),(86,12),(103,23),(111,34),(93,32),(71,35),(49,46)],O1,stroke='#544e3e',width=1)
shape(helmet,[(43,17),(57,9),(75,8),(91,12),(83,22),(61,22),(50,27)],O3,stroke='#4b4635',width=1)
line(helmet,[(45,18),(60,12),(75,11)],HIGHLIGHT)
shape(helmet,[(56,10),(71,7),(86,10),(94,16),(84,23),(65,23),(54,19)],'#aa985f',stroke='#534b36',width=1)
for py in range(13,21,3):
 for px in range(64,88,4):
  if helmet.getpixel((px,py))[3] and helmet.getpixel((px,py))[:3] == (170,152,95):rect(helmet,(px,py,px+1,py),'#897a50')
shape(helmet,[(16,55),(29,57),(45,54),(57,49),(74,47),(93,47),(111,49),(126,49),(130,57),(120,60),(101,59),(83,56),(66,59),(50,67),(31,71),(15,66)],'#453e2f')
line(helmet,[(19,57),(33,59),(47,57),(61,52),(77,51),(94,51),(113,53),(126,53)],'#b9ab88',width=2)
line(helmet,[(17,65),(30,69),(48,64),(63,55)],'#11100e',width=2)
shape(helmet,[(16,45),(29,40),(46,40),(56,44),(62,51),(53,59),(41,61),(29,72),(17,71),(15,62)],'#39362b')
shape(helmet,[(18,47),(32,43),(45,44),(55,48),(58,52),(49,56),(39,58),(30,68),(19,68)],'#928667')
line(helmet,[(20,49),(32,46),(43,46),(51,48)],'#c0b08b',width=2)
for a,b in [(25,52),(31,50),(37,49),(43,49)]:rect(helmet,(a,b,a+2,b+5),'#28261f')
for cx,cy in [(54,51),(113,34)]:
 ImageDraw.Draw(helmet).ellipse((cx-3,cy-3,cx+3,cy+3),fill='#23221d',outline='#cfbf94',width=1)
 rect(helmet,(cx-1,cy-1,cx,cy),'#a3a49f')
shape(helmet,[(104,22),(117,24),(124,31),(125,45),(119,50),(104,48),(99,41),(100,29)],'#4c4739')
shape(helmet,[(104,25),(115,25),(121,31),(121,44),(117,46),(104,44),(103,36)],'#b0a180',stroke='#22201b')
rect(helmet,(108,31,118,43),'#191a18','#c9b68f',width=2)
rect(helmet,(110,34,116,41),'#40443a')
# Raised attachment rim, vents and stitching, sized individually for the bald Head 133
line(helmet,[(26,43),(40,36),(55,34)],'#b5a47e',width=1)
line(helmet,[(36,31),(48,21),(59,17)],'#554d3d')
for tx in range(63,85,5):
 for ty in range(13,21,4):
  rect(helmet,(tx,ty,tx+1,ty),'#84744e')
for vx in (25,31,37,43):rect(helmet,(vx,54,vx+2,55),'#292820')
line(helmet,[(103,25),(118,25),(122,31)],'#decba3')
rect(helmet,(111,35,115,37),'#555849')
chin=new()
line(chin,[(48,66),(52,77),(57,90),(63,109)],'#171715',width=5)
line(chin,[(49,67),(52,77),(58,91),(63,108)],'#645c49',width=3)
shape(chin,[(58,91),(67,91),(70,99),(68,105),(60,105),(56,99)],'#aaa89b',stroke='#141414')
rect(chin,(61,94,66,101),'#2a2826','#141414')
line(chin,[(65,110),(75,122),(90,130),(110,130),(121,120)],'#171611',width=5)
line(chin,[(67,111),(78,123),(91,128),(107,128),(119,119)],'#797159',width=3)
mask_rear=new()
line(mask_rear,[(30,74),(40,72),(54,75),(76,79)],'#111116',width=7)
line(mask_rear,[(30,74),(40,72),(54,75),(76,79)],'#383b42',width=4)
line(mask_rear,[(38,103),(57,109),(72,108)],'#17171b',width=5)
line(mask_rear,[(39,103),(56,107),(72,107)],'#45464b',width=2)
goggle=new()
shape(goggle,[(72,67),(83,60),(104,59),(118,61),(130,68),(130,96),(123,101),(109,100),(102,93),(95,96),(81,96),(72,91)],'#141519',stroke='#0b0b0e')
shape(goggle,[(76,71),(85,65),(103,64),(118,66),(126,72),(127,91),(122,96),(110,95),(102,89),(96,91),(81,91),(76,86)],'#42434a',stroke='#9c9ea0',width=1)
inner=[(79,72),(86,68),(103,67),(117,69),(124,75),(124,88),(120,91),(109,91),(102,85),(96,87),(83,87),(79,83)]
ImageDraw.Draw(goggle).polygon(inner,fill=(108,124,131,0))
line(goggle,[(81,72),(91,69),(107,69)],(224,228,223,110),width=1)
line(goggle,[(119,73),(122,77),(122,85)],(235,238,233,105),width=1)
mask_shell=new()
shape(mask_shell,[(78,88),(90,91),(101,90),(107,87),(116,92),(129,94),(130,117),(122,128),(109,134),(96,132),(83,124),(76,111)],'#16171c')
shape(mask_shell,[(81,95),(91,95),(101,94),(107,91),(116,96),(126,99),(127,115),(119,126),(109,130),(97,128),(85,120),(79,108)],GRAPH,stroke='#14151a')
shape(mask_shell,[(89,101),(102,98),(106,101),(109,119),(103,127),(90,118)],'#484a52',stroke='#2c2e34',width=1)
line(mask_shell,[(92,105),(98,100),(103,101)],'#64666d')
shape(mask_shell,[(106,100),(114,99),(123,106),(121,119),(112,126),(107,118)],'#2b2d33',stroke='#292b30',width=1)
line(mask_shell,[(114,102),(119,108),(118,118)],'#4e5157')
for yy in [113,117,121]:line(mask_shell,[(116,yy),(122,yy-1)],'#16181b')
line(mask_shell,[(76,91),(82,94),(93,94),(101,89),(106,89),(116,95),(125,96)],'#0b0c0f',width=2)
buckle=new()
shape(buckle,[(65,83),(72,83),(75,88),(73,95),(65,95),(62,90)],'#9da0a1',stroke='#111216')
rect(buckle,(67,86,71,92),'#22242a','#08090a')
# Fit gear overlays to 124x135 source; never resize or repaint original.
# Helmet is scaled from the standard 131x138 template, with mask goggles
# adjusted only in horizontal fit to preserve the source eyes.
original.save(OUT/'original.png')
for name,im in [('helmet_shell',helmet),('helmet_chin',chin),('mask_rear',mask_rear),('mask_goggles',goggle),('mask_shell',mask_shell),('mask_buckle',buckle)]:im.save(OUT/(name+'.png'))
def render(which):
 out=new()
 if which in ('mask','both'):out.alpha_composite(mask_rear)
 out.alpha_composite(original)
 if which in ('helmet','both'):out.alpha_composite(helmet)
 if which in ('mask','both'):
  out.alpha_composite(mask_shell);out.alpha_composite(goggle);out.alpha_composite(buckle)
 if which in ('helmet','both'):out.alpha_composite(chin)
 return out
names=['original','helmet','mask','both']
for n in names:render(n).save(OUT/(n+'.png'))
scale=4;pad=16;headroom=30
review=Image.new('RGB',(4*W*scale+5*pad,H*scale+headroom+20),'#1b2532');dr=ImageDraw.Draw(review)
for i,n in enumerate(names):
 bg=Image.new('RGBA',(W,H),'#2d3d4e');bg.alpha_composite(render(n))
 x=pad+i*(W*scale+pad)
 review.paste(bg.resize((W*scale,H*scale),Image.Resampling.NEAREST).convert('RGB'),(x,headroom))
 dr.text((x+6,8),n.upper(),fill='white')
review.save(OUT/'review.png')
assert render('original').tobytes()==original.tobytes()
(OUT/'qa.json').write_text(json.dumps({'character':133,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_pixels_preserved':True,'approved':False,'visual_status':'review_candidate'},indent=2))
with zipfile.ZipFile(OUT/'Head133_ExactSource_Gear_Review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.glob('*.png'):z.write(f,f.name)
 z.write(OUT/'qa.json','qa.json')
print('Head133 exact-source art generated')