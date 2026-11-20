#!/usr/bin/env python3
"""Deterministic OFFLINE V166 original art: 96 functional assets x genuine two faces.
Asset generator, not screenshot painting. Pillow==11.3.0, fully transparent cells.
Do not touch approved character artwork, collision geometry, or save inventory.
"""
import base64,io,random,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"app/src/main/assets/sp_v166_directional_furniture.webp.b64"
PREVIEW=Path("docs/qa/v166/interiors/reconstruction/asset_review/v166_directional_contact_sheet.jpg")
KINDS=((1,0,2,3,4,5,8,30,6,7,31,10),
(6,9,7,10,28,29,8,16,11,5,30,2),
(13,12,8,14,16,27,25,5,6,26,4,11),
(0,30,15,16,1,7,2,8,4,11,5,14),
(17,18,8,6,7,5,19,20,11,10,28,4),
(22,23,24,25,20,19,29,27,26,11,4,9),
(25,27,26,23,24,11,28,29,6,8,22,14),
(1,0,3,4,5,2,30,31,8,6,7,14))
DARK=(23,34,36);MID=(40,55,56)
WOOD=((103,75,53),(99,76,56),(116,82,50),(121,91,65),
(112,96,75),(106,101,83),(116,95,77),(111,76,55))
FABRIC=((124,96,75),(96,134,107),(128,116,95),(91,137,137),
(106,125,101),(107,121,111),(99,123,110),(132,111,84))
METAL=(100,115,113);PAPER=(210,204,176);RUST=(166,94,57)
SCREEN=(65,117,117)
def tint(c,n):return tuple(max(0,min(255,x+n)) for x in c)

class Art:
 def __init__(self,t,k,side,slot):
  self.t=t;self.k=k;self.side=side
  self.r=random.Random(8117+t*781+k*167+int(side)*31+slot*487)
  self.a=Image.new("RGBA",(128,128))
  cast=Image.new("RGBA",(128,128));ImageDraw.Draw(cast).ellipse((8,101,120,125),fill=(10,22,23,100))
  self.a.alpha_composite(cast.filter(ImageFilter.GaussianBlur(5)))
  self.d=ImageDraw.Draw(self.a)
  self.w=tint(WOOD[t],self.r.randint(-10,10));self.f=tint(FABRIC[t],self.r.randint(-10,10))
  self.m=tint(METAL,self.r.randint(-9,9));self.b=(192,190,169)
 def P(self,pts,col,border=True):self.d.polygon(pts,fill=col,outline=DARK if border else None,width=2 if border else 1)
 def R(self,box,col,rad=0,border=True):
  b=tuple(round(x) for x in box)
  if rad:self.d.rounded_rectangle(b,radius=rad,fill=col,outline=DARK if border else None,width=2 if border else 1)
  else:self.d.rectangle(b,fill=col,outline=DARK if border else None,width=2 if border else 1)
 def L(self,pts,col=DARK,width=2):self.d.line(pts,fill=col,width=width,joint="curve")
 def O(self,b,col,border=False):self.d.ellipse(b,fill=col,outline=DARK if border else None,width=2 if border else 1)
 def screw(self,x,y):
  self.O((x-2,y-2,x+2,y+2),tint(self.m,30));self.L(((x-1,y),(x+1,y)),DARK,1)
 def grit(self,b,typ="wood",n=40):
  x0,y0,x1,y1=map(round,b)
  if x1-x0<9 or y1-y0<9:return
  for i in range(n):
   x=self.r.randint(x0+2,x1-3);y=self.r.randint(y0+2,y1-3)
   if typ=="wood":col=tint(self.w,self.r.choice((-30,-12,19,31)));w=self.r.randint(4,16)
   elif typ=="fabric":col=tint(self.f,self.r.choice((-25,22,-14,13)));w=self.r.randint(1,5)
   else:col=self.r.choice((RUST,tint(self.m,-31),tint(self.m,33)));w=self.r.randint(2,9)
   self.L(((x,y),(min(x1-3,x+w),y)),col,1)
 def plank(self,b):
  self.R(b,self.w,2)
  self.grit((b[0]+2,b[1]+2,b[2]-2,b[3]-2),"wood",38)
  self.L(((b[0]+3,b[1]+4),(b[2]-3,b[1]+4)),tint(self.w,34),2)
  self.screw(b[0]+6,b[1]+6);self.screw(b[2]-6,b[3]-6)
 def hull(self,steel=False):
  col=self.m if steel else self.w
  if self.side:
   self.P(((35,13),(95,20),(103,112),(43,108)),tint(col,-37))
   self.P(((38,16),(92,18),(99,33),(42,31)),tint(col,24))
   self.P(((44,34),(98,37),(100,103),(47,101)),col,False)
   self.L(((92,21),(101,106)),tint(col,-44),3)
   self.grit((48,41,94,97),"metal" if steel else "wood",48)
   return (48,42,92,98)
  self.P(((13,25),(110,25),(117,109),(9,109)),tint(col,-45))
  self.P(((15,20),(109,20),(115,35),(11,35)),tint(col,27))
  self.P(((13,36),(114,36),(111,105),(16,105)),col,False)
  self.L(((18,40),(109,40)),tint(col,38),2)
  self.grit((20,43,108,100),"metal" if steel else "wood",66)
  return (21,44,105,101)
 def table(self,steel=False):
  col=self.m if steel else self.w
  if self.side:
   self.P(((41,9),(93,15),(104,93),(46,101)),tint(col,-38))
   self.P(((41,12),(89,15),(100,90),(47,94)),tint(col,27))
   self.P(((44,18),(87,20),(94,85),(50,90)),col,False)
   self.R((45,94,54,113),DARK);self.R((92,91,100,113),DARK)
   self.grit((50,25,86,81),"metal" if steel else "wood",66)
   return (49,25,90,82)
  self.P(((17,17),(111,17),(117,95),(11,95)),tint(col,-37))
  self.P(((17,13),(109,13),(113,88),(15,88)),tint(col,28))
  self.P(((21,22),(106,22),(110,81),(18,81)),col,False)
  for x in (18,104):self.R((x,88,x+8,114),DARK)
  self.grit((22,27,104,78),"metal" if steel else "wood",72)
  return (22,27,105,78)
 def cabinet(self,steel=False):
  self.hull(steel)
  for i in (0,1):
   if self.side:
    self.R((50,41+i*29,87,66+i*29),tint(self.m if steel else self.w,12-i*17),2)
    self.L(((55,46+i*29),(80,46+i*29)),self.b,1);self.screw(77,58+i*29)
   else:
    self.R((20+i*43,45,60+i*43,99),tint(self.m if steel else self.w,11-i*16),2)
    self.L(((25+i*43,49),(55+i*43,49)),self.b,1);self.screw(55+i*12,72)
 def shelves(self,what):
  self.hull(what==25)
  l=51 if self.side else 21;r=88 if self.side else 103
  for n,y in enumerate((44,65,86)):
   self.R((l,y,r,y+4),DARK)
   if what==8:
    for j in range(5 if self.side else 12):
     x=l+3+j*(r-l-6)/(5 if self.side else 12)
     h=self.r.randint(11,17)
     col=self.r.choice(((138,94,66),(87,113,106),(159,132,93),(82,103,119)))
     self.R((x,y-h,x+max(3,(r-l-6)/(5 if self.side else 12)-1),y-3),col,1)
     self.L(((x+2,y-h+3),(x+2,y-6)),tint(col,37),1)
   else:
    for j in range(3 if self.side else 6):
     x=l+3+j*(r-l-7)/(3 if self.side else 6)
     color=self.r.choice(((137,106,79),(107,139,111),(178,142,73),RUST))
     self.R((x,y-14,x+9,y-4),color,2)
     self.L(((x+2,y-11),(x+7,y-11)),self.b,1)
  if what==25:
   self.L(((l-5,32),(l-5,109)),RUST,4);self.L(((r+4,32),(r+4,109)),RUST,4)
   for x in range(l,r,14):self.L(((x,99),(x+5,93)),DARK,3)
 def screen(self,b,lines=False):
  self.R(b,DARK,4);self.R((b[0]+4,b[1]+4,b[2]-4,b[3]-4),SCREEN,2)
  self.L(((b[0]+7,b[1]+8),(b[2]-9,b[1]+8)),tint(SCREEN,52),2)
  if lines:
   for j in range(3):self.L(((b[0]+7,b[1]+14+j*6),(b[2]-11-j*5,b[1]+14+j*6)),
                                (178,207,175),1)
  else:self.L(((b[0]+9,b[3]-10),(b[2]-9,b[1]+13)),tint(SCREEN,39),2)
 def draw(self):
  k=self.k;s=self.side
  # Full-sized, believable equipment. Detail belongs to furnishings,
  # never distributed as standalone floor specks/mini paper.
  if k==0:
   self.plank((40,10,96,114) if s else (12,13,115,111))
   b=(46,18,91,107) if s else (19,25,108,104)
   self.R(b,self.f,6)
   if s:
    self.R((49,23,88,48),PAPER,6)
    self.L(((49,61),(87,63)),tint(self.f,42),3)
    self.L(((49,84),(88,88)),tint(self.f,-26),2)
   else:
    for x in (25,68):self.R((x,30,x+34,51),PAPER,6)
    self.L(((22,68),(105,72)),tint(self.f,39),3)
    self.L(((23,91),(104,93)),tint(self.f,-31),3)
   self.grit((b[0]+4,57,b[2]-4,b[3]-5),"fabric",74)
  elif k==1:
   self.R((43,10,109,112) if s else (9,22,119,110),DARK,9)
   self.R((48,15,103,105) if s else (15,28,113,103),self.f,8)
   if s:
    self.R((50,18,64,103),tint(self.f,-37),5)
    for i in range(3):
     y=19+i*28;self.R((65,y,101,y+25),tint(self.f,-8 if i%2 else 12),6)
     self.grit((68,y+5,97,y+22),"fabric",26)
   else:
    self.R((17,33,110,54),tint(self.f,-35),5)
    for i in range(3):
     x=20+i*30;self.R((x,55,x+28,97),tint(self.f,-7 if i%2 else 11),6)
     self.grit((x+3,61,x+25,92),"fabric",25)
    for x in (11,106):self.R((x,46,x+12,101),self.w,4)
  elif k in (2,10,11,24,30):
   self.cabinet(k in (10,11,24))
   if k in (10,24,30):
    for j in range(3):
     y=44+j*18;self.R((52 if s else 26,y,87 if s else 99,y+15),
                      tint(self.m if k in (10,24) else self.w,-10+j*9),1)
     self.L(((59 if s else 40,y+10),(77 if s else 83,y+10)),DARK,2)
   if k==2:
    self.L(((52 if s else 62,45),(84 if s else 62,99)),tint(self.w,-32),2)
   if k==11:
    for j in range(5):self.L(((53 if s else 27,49+j*8),(79 if s else 54,49+j*8)),DARK,1)
   if k==24:
    for j in range(4):
     x=54+j*8 if s else 27+j*20
     self.L(((x,48),(x,63)),PAPER,2);self.O((x-3,59,x+3,66),self.m,True)
  elif k in (3,4,14,31):
   self.cabinet(k==14)
   if k==3:
    for x,y in (((60,47),(79,70)) if s else ((37,52),(84,52),(37,79),(84,79))):
     self.O((x-11,y-8,x+11,y+8),DARK,True)
     self.O((x-6,y-4,x+6,y+4),self.m)
     self.screw(x,y)
   elif k in (4,31):
    b=(53,42,83,81) if s else (24,44,98,82)
    self.R(b,self.m,6);self.R((b[0]+4,b[1]+4,b[2]-4,b[3]-4),DARK,5)
    self.L(((b[0]+16,b[1]+5),(b[0]+16,b[1]-9),
            (b[0]+34,b[1]-9)),PAPER,3)
   else:
    for i in range(3):
     y=45+i*18;self.R((52 if s else 24,y,86 if s else 100,y+13),PAPER,2)
     self.L(((59 if s else 31,y+8),(80 if s else 93,y+8)),self.m,2)
  elif k==5:
   self.table()
   for x,y in (((63,40),(73,71)) if s else ((44,45),(86,44))):
    self.O((x-13,y-10,x+13,y+10),PAPER,True)
    self.O((x-6,y-5,x+6,y+5),self.m)
    self.L(((x+5,y+6),(x+14,y+11)),PAPER,2)
  elif k in (6,12,16):
   self.table(k==12)
   self.screen((56,29,84,58) if s else (32,29,83,58),k!=16)
   self.R((52,64,90,71) if s else (39,64,90,71),DARK,2)
   for j in range(8):self.L(((47+j*5,67),(49+j*5,67)),PAPER,1)
   self.R((53 if s else 24,74,69 if s else 36,80),PAPER,1)
   if k==12:
    self.R((85,42,106,66),self.m,2)
    self.L(((90,49),(102,49)),RUST,3)
   if k==16:self.R((40 if s else 19,87,87 if s else 106,94),tint(self.w,-27),2)
  elif k in (7,17):
   if s:
    self.R((53,16,89,85),DARK,8);self.R((58,21,84,77),self.f,6)
    self.R((44,73,98,98),tint(self.f,-21),6)
    self.L(((71,99),(71,116)),DARK,5)
    self.L(((47,112),(96,112)),self.m,4)
   else:
    self.R((21,16,105,65),DARK,8);self.R((27,22,99,59),self.f,6)
    self.R((31,63,96,95),tint(self.f,-21),6)
    self.L(((64,97),(64,116)),DARK,5)
    self.L(((37,112),(91,112)),self.m,4)
   if k==17:
    self.R((42 if s else 18,49,92 if s else 111,59),self.w,2)
    self.R((52 if s else 30,51,71 if s else 67,56),PAPER,1,False)
  elif k in (8,13,25):self.shelves(k)
  elif k in (9,20,28,29):
   self.cabinet(True)
   self.screen((53,43,86,75) if s else (27,44,101,77),True)
   if k==20:
    for x in ((62,79) if s else (42,84)):
     self.O((x-6,82,x+6,94),RUST,True);self.O((x-3,85,x+3,91),self.m)
   elif k==29:
    for j in range(3):
     y=78+j*7;self.R((53 if s else 28,y,87 if s else 101,y+5),DARK)
     self.O((81 if s else 94,y+1,84 if s else 97,y+4),(109,160,92))
   elif k==28:
    self.R((53 if s else 29,80,87 if s else 97,93),PAPER,2)
    self.L(((55 if s else 31,99),(86 if s else 97,99)),DARK,2)
  elif k==15:
   self.L(((36,13),(90,13),(102,97),(35,97)),self.m,5)
   self.R((48,41,96,90),self.w,5)
   self.L(((54,52),(91,55)),RUST,4)
   self.L(((72,42),(72,86)),tint(self.w,40),3)
   self.R((61,32,78,45),DARK,4)
   for x in (40,96):self.O((x-7,98,x+7,113),DARK,True)
  elif k==18:
   self.R((50,12,95,110) if s else (8,23,118,98),self.w,4)
   b=(56,19,88,101) if s else (15,29,111,90)
   self.R(b,(36,72,64),2)
   for i in range(6):
    y=b[1]+8+i*(b[3]-b[1]-14)/6
    self.L(((b[0]+5,y),(b[2]-8-self.r.randint(0,9),y-2)),(171,191,168),1)
   self.R((54,102,94,110) if s else (12,90,114,98),tint(self.w,-22))
  elif k==19:
   self.table(True)
   for x,y in (((53,32),(67,52),(75,72)) if s else ((30,36),(49,37),(70,40))):
    self.R((x,y,x+10,y+18),tint(SCREEN,30),2)
    self.R((x+2,y-4,x+8,y),DARK,1)
    self.L(((x+2,y+12),(x+7,y+12)),RUST,2)
   x=83 if s else 88
   self.L(((x-9,40),(x+2,53),(x-11,74)),DARK,5)
   self.O((x-17,74,x+4,84),DARK);self.screw(x,50)
  elif k==21:
   self.R((41,9,95,113) if s else (11,27,117,99),DARK,5)
   self.R((45,14,91,107) if s else (17,32,111,93),(154,184,177),4)
   self.R((47,18,88,43) if s else (20,36,52,88),PAPER,4)
   self.L(((47,76),(89,80)) if s else ((59,35),(60,90)),self.m,3)
   for x in (44,94):self.L(((x,99),(x,115)),DARK,4)
  elif k in (22,23):
   self.cabinet(True)
   if k==22:
    self.R((53,43,87,92) if s else (26,45,101,98),DARK,4)
    self.R((58,51,83,83) if s else (37,51,93,89),RUST,3)
    for x in ((69,) if s else (49,83)):
     self.L(((x,36),(x,92)),self.m,5)
    for x in range(25,100,15):self.L(((x,98),(x+7,91)),DARK,3)
   else:
    self.R((46,23,98,108) if s else (11,41,117,91),MID,4)
    for j in range(6):
     if s:
      y=28+j*12;self.R((51,y,93,y+7),tint(self.m,27),1)
      self.L(((53,y+2),(90,y+2)),PAPER,1)
     else:
      x=18+j*15;self.R((x,46,x+11,87),tint(self.m,26),1)
      self.L(((x+2,48),(x+2,84)),PAPER,1)
  elif k==26:
   if s:
    self.L(((54,11),(61,93),(99,93)),self.m,6)
    self.L(((65,14),(69,82),(105,82)),DARK,4)
    self.plank((62,41,92,83))
    self.L(((64,44),(90,80)),DARK,2)
    for x in (65,99):self.O((x-7,94,x+7,109),DARK,True)
   else:
    self.L(((27,13),(35,93),(107,93)),self.m,6)
    self.L(((38,16),(47,83),(109,83)),DARK,4)
    self.plank((36,49,101,86))
    self.L(((39,51),(98,84)),DARK,2)
    for x in (38,103):self.O((x-7,94,x+7,109),DARK,True)
  elif k==27:
   self.plank((40,84,99,112) if s else (17,85,111,112))
   for j in range(3):
    b=(46,18+j*23,95,38+j*23) if s else (21,22+j*21,107,42+j*21)
    self.plank(b)
    cx=(b[0]+b[2])//2
    self.L(((cx,b[1]+2),(cx,b[3]-2)),tint(self.w,-40),2)
   self.L(((69,17),(69,109)),(70,89,81),5)
  if k not in (0,1,7,17,18,26):
   for x,y in (((52,43),(91,100)) if s else ((20,41),(106,101))):
    self.screw(x,y)
  return self.a

def run():
 atlas=Image.new("RGBA",(2048,1536))
 sheet=Image.new("RGB",(1024,1536),(43,55,54))
 for theme,group in enumerate(KINDS):
  for slot,kind in enumerate(group):
   sprites=[]
   for side in (False,True):
    art=Art(theme,kind,side,slot).draw()
    cell=(theme*12+slot)*2+int(side)
    atlas.alpha_composite(art,((cell%16)*128,(cell//16)*128))
    sprites.append(art)
    assert art.getchannel("A").getbbox(),(theme,kind,side)
   assert ImageChops.difference(*sprites).getbbox(),(theme,kind)
   sheet.paste(sprites[0],(theme*128,slot*128),sprites[0])
 PREVIEW.parent.mkdir(parents=True,exist_ok=True)
 sheet.save(PREVIEW,quality=91,subsampling=0)
 content=io.BytesIO();atlas.save(content,"WEBP",lossless=True,method=6)
 OUT.write_text(base64.b64encode(content.getvalue()).decode("ascii")+"\n")
 print("PASS 96 thematic furniture identities and 192 DISTINCT front/profile original sprites")
 print("PASS 128x128 transparent per object, no rotated silhouettes or miniature loot")
 print("ATLAS_SHA256",hashlib.sha256(content.getvalue()).hexdigest())
 print("ATLAS_BYTES",len(content.getvalue()))
if __name__=="__main__":run()
