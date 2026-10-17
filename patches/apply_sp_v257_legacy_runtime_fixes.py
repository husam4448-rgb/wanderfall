#!/usr/bin/env python3
"""Fix 4 observed legacy D2D14 runtime errors without changing world or HUD layout.
Actual errors observed in native Godot screenshot CI, not inferred.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])
def one(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if s.count(old)!=1:
        raise SystemExit(f'V257 RUNTIME FAIL: {label}, found {s.count(old)}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')
one('scripts/ui/ui_manager.gd',
    '            button.icon_max_width = 22\n',
    '            # Godot 4.7 Button has no icon_max_width property; old\n            # theme_constant_override already applies this at line ~751.\n',
    'UIManager invalid Godot Button property')
for path,anchor,label in [
    ('scripts/social/friendly_npc.gd','    trade_stock = stock.duplicate(true) if stock is Array else []','FriendlyNPC stock'),
    ('scripts/social/faction_mobile_group.gd','    trade_stock = stock.duplicate(true) if stock is Array else []','FactionMobileGroup stock'),
    ('scripts/social/faction_mobile_group.gd','    trade_stock = stock.duplicate(true) if stock is Array else trade_stock','FactionMobileGroup saved stock'),
]:
    one(path,anchor,
    '''    trade_stock.clear()
    if stock is Array:
        for entry in stock:
            if entry is Dictionary:
                trade_stock.append(entry)''',label)
one('scripts/ecology/wildlife_actor.gd',
    '    drops = configured_drops.duplicate(true) if configured_drops is Array else []',
    '''    drops.clear()
    if configured_drops is Array:
        for entry in configured_drops:
            if entry is Dictionary:
                drops.append(entry)''','WildlifeActor typed drops')
one('scripts/ecology/wildlife_actor.gd',
    '        drops = stored_drops.duplicate(true) if stored_drops is Array else drops',
    '''        if stored_drops is Array:
            drops.clear()
            for entry in stored_drops:
                if entry is Dictionary:
                    drops.append(entry)''','WildlifeActor stored drops')
one('scripts/social/faction_mobile_group.gd',
    'var other_faction := String(node.get("faction_id"))',
    'var faction_variant: Variant = node.get("faction_id")\n        var other_faction := str(faction_variant) if faction_variant != null else ""',
    'null faction compatibility')
print('SP_V257_HISTORIC_UI_NPC_COMPAT_FIXED invalid Button icon property; typed NPC and wildlife dictionaries; missing faction ID')
