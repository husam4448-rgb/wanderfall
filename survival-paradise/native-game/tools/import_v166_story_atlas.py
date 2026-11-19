#!/usr/bin/env python3
"""Import the V166 original character-free interior set-piece atlas.

One-time reproducible source import. The committed output is a local Android
asset; the finished game does NOT request the image from any network.
"""
from __future__ import annotations
import base64
import hashlib
import io
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

ORIGINAL = "https://cdn.openart.ai/openart-uploads/production/attachment-transfers/1e536e569d613100374694d845cdab2ed1c7f3fb8f1834badbfea9b3da0c012a.png"
SHA256 = "37ac5c1e4b1a490482e0427805abbc207424f04c2fc60d74be771756823ee124"
ASSET = Path(__file__).resolve().parents[1] / "app/src/main/assets/sp_v166_story_props.webp.b64"

def main():
    with urlopen(Request(ORIGINAL, headers={"User-Agent": "SP-V166-Art-Importer/1"}), timeout=60) as response:
        raw = response.read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SHA256:
        raise RuntimeError("Source art SHA mismatch: " + actual)
    src = Image.open(io.BytesIO(raw)).convert("RGBA")
    if src.size != (1254, 1254):
        raise RuntimeError("Original sprite atlas dimensions changed")
    cell = 96
    atlas = Image.new("RGBA", (4*cell,4*cell), (0,0,0,0))
    for i in range(16):
        col, row = i % 4, i // 4
        region = src.crop((
            round(col*src.width/4), round(row*src.height/4),
            round((col+1)*src.width/4), round((row+1)*src.height/4)))
        region = region.resize((cell,cell), Image.Resampling.LANCZOS)
        pixels = region.load()
        for y in range(cell):
            for x in range(cell):
                r,g,b,a = pixels[x,y]
                if a < 22:
                    pixels[x,y]=(0,0,0,0)
        if region.getchannel("A").getbbox() is None:
            raise RuntimeError("Missing sprite "+str(i))
        atlas.alpha_composite(region,(col*cell,row*cell))
    encoded=io.BytesIO()
    atlas.save(encoded, format="WEBP", quality=70, method=4)
    data=encoded.getvalue()
    check=Image.open(io.BytesIO(data)).convert("RGBA")
    if check.size != (384,384):
        raise RuntimeError("Pack size invalid")
    for i in range(16):
        tile=check.crop(((i%4)*cell,(i//4)*cell,(i%4+1)*cell,(i//4+1)*cell))
        if not tile.getchannel("A").getbbox():
            raise RuntimeError("Empty authored set piece "+str(i))
    ASSET.write_text(base64.b64encode(data).decode("ascii")+"\n",encoding="ascii")
    print("Imported 16 detailed interior prop scenes; original SHA",actual,
          "WebP bytes",len(data),"target",ASSET)

if __name__ == "__main__":
    main()
