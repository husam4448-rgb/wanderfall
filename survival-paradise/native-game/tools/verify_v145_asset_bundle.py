#!/usr/bin/env python3
"""Verify exact user-approved V145 assets. Never regenerate or repaint them."""
import hashlib, json, struct, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'app/src/main/assets/sp_v145_legacy_equipment.zip'
EXPECTED_SHA='649bbecd59b13740d7fe221e70f2f05707dae9b70e1a04ae517c83fc65997822'
EXPECTED=[
    'torsos/20_canvas_work_jacket.png',
    'torsos/21_weatherproof_field_coat.png',
    'torsos/22_plate_carrier.png',
    'pants/20_cargo_trousers.png',
    'pants/21_ripstop_trousers.png',
    'pants/22_tactical_trousers.png',
    'boots/05_steel_toe_work_boots.png',
    'boots/06_trail_boots.png',
    'boots/07_tactical_combat_boots.png',
]
def verify():
    assert PACKAGE.is_file(),f'Missing approved art archive: {PACKAGE}'
    assert hashlib.sha256(PACKAGE.read_bytes()).hexdigest()==EXPECTED_SHA, 'Unapproved altered archive'
    with zipfile.ZipFile(PACKAGE) as archive:
        assert archive.testzip() is None,'Corrupt archive'
        names=[n for n in archive.namelist() if n.endswith('.png')]
        assert sorted(names)==sorted(EXPECTED),'Missing or unexpected equipment PNG'
        manifest=json.loads(archive.read('manifest.json'))
        entries=manifest.get('items',[])
        assert len(entries)==9
        assert sorted(e['game_path'] for e in entries)==sorted(EXPECTED)
        for entry in entries:
            name=entry['game_path']
            data=archive.read(name)
            assert data[:8]==b'\x89PNG\r\n\x1a\n',name
            w,h,depth,color=struct.unpack('>IIBB',data[16:26])
            assert (w,h)==tuple(entry['game_dimensions']),name
            assert depth==8 and color==6,'Require 8-bit RGBA PNG'
            assert hashlib.sha256(data).hexdigest()==entry['game_sha256'],name
            if name.startswith('boots/'):assert (w,h)==(68,52),name
            else: assert 100<=w<=250 and 100<=h<=190,name
    java=ROOT/'app/src/main/java/com/survivalparadise/nativegame'
    assert 'headgear(int legacy){return -1;}' in (java/'LegacyOutfitVisualV144.java').read_text()
    assert 'ApprovedLegacyIconsV145.drawable(context,kind,dp)' in (java/'GearItemIconsV95.java').read_text()
    icon_code=(java/'ApprovedLegacyIconsV145.java').read_text()
    for name in EXPECTED:assert name in icon_code,name
    print('PASS V145: exact 9 verified designs, corrected ripstop, RGBA and 68x52 boot anchors')
if __name__=='__main__':verify()
