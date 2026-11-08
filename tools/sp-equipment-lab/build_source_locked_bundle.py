#!/usr/bin/env python3
"""Reconstruct verified V132 200-head offline equipment lab from original bytes."""
from pathlib import Path
import hashlib, io, json, shutil, struct, zipfile

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT/'survival-paradise/native-game/source_v109'
HERE=Path(__file__).resolve().parent
OUT=ROOT/'artifacts/sp-equipment-lab'
EXPECTED='c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a'
def sha(b):return hashlib.sha256(b).hexdigest()
def dims(b):
    assert b[:8]==b'\x89PNG\r\n\x1a\n' and b[12:16]==b'IHDR','Invalid original PNG'
    return list(struct.unpack('>II',b[16:24]))
def main():
    parts=sorted(GAME.glob('part_*.bin'))
    assert [p.name for p in parts]==[f'part_{i:02}.bin' for i in range(8)]
    source=b''.join(p.read_bytes() for p in parts)
    assert sha(source)==EXPECTED,'Original V132 source checksum mismatch'
    names=['body_idle.png','body_walk.png','v5_fittings.json']+[f'heads/{i:03}.png' for i in range(1,201)]
    OUT.mkdir(parents=True,exist_ok=True)
    report={}
    with zipfile.ZipFile(io.BytesIO(source)) as z:
        assert z.testzip() is None and all(n in z.namelist() for n in names)
        fitting=json.loads(z.read('v5_fittings.json'))
        assert fitting['totalCharacters']==200 and len(fitting['characterOverrides'])==fitting['overrideCount']==51
        for n in names:
            b=z.read(n)
            d=dims(b) if n.endswith('.png') else None
            if n=='body_idle.png':assert d==[200,260]
            if n=='body_walk.png':assert d==[800,260]
            p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            assert p.read_bytes()==b
            report[n]={'sha256':sha(b),'bytes':len(b),'dimensions':d}
    (OUT/'index.html').write_bytes((HERE/'index.html').read_bytes())
    (OUT/'README.txt').write_bytes((HERE/'README.txt').read_bytes())
    (OUT/'v5_fittings_data.js').write_text('window.SP_V5_FITTINGS = '+json.dumps(fitting,separators=(',',':'))+';\n',encoding='utf-8')
    helmet=ROOT/'assets/authored2d/unified_character/generic/helmet.png'
    if helmet.is_file():
        p=OUT/'reference_gear/generic_helmet_repository_UNAPPROVED.png'
        p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(helmet,p)
    (OUT/'INTEGRITY_MANIFEST.json').write_text(json.dumps({'sourceSHA256':EXPECTED,'heads':200,'V5Overrides':51,'assetHashes':report,'gearStatus':'Existing generic helmet unapproved; no approved gas-mask art found'},indent=2))
    package=ROOT/'artifacts/SurvivalParadise_Modular_Equipment_Originals_Prototype_v1.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as o:
        for f in sorted(OUT.rglob('*')):
            if f.is_file():o.write(f,f.relative_to(OUT))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        assert sum(n.startswith('heads/') and n.endswith('.png') for n in z.namelist())==200
    print('PASS: 200 originals, idle, 4 walking frames, V5 fitting, full offline HTML, hash:',sha(package.read_bytes()))
if __name__=='__main__':main()
