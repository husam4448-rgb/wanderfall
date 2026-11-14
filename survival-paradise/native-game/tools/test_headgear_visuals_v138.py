#!/usr/bin/env python3
"""V138 static contract: headgear remains functional but is never rendered."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "app/src/main/java/com/survivalparadise/nativegame"
g = (SRC / "GameView.java").read_text(encoding="utf-8")
w = (SRC / "WearableArtV96.java").read_text(encoding="utf-8")
ui = (SRC / "MainActivity.java").read_text(encoding="utf-8")
wardrobe = (SRC / "WardrobeV92.java").read_text(encoding="utf-8")
skins = (SRC / "CharacterSkinsV109.java").read_text(encoding="utf-8")

# No head-equipment canvas operation is reachable through the legacy renderer.
assert "wearableArtV96.drawHead(" not in g
assert re.search(r"void drawApprovedGearV93\(.*?if\(index==1\)return;", g, re.S)
head_api = w.split("public void drawHead(", 1)[1]
assert "c.drawBitmap(" not in head_api
assert "Intentionally empty" in head_api
assert "void drawPack(" in w and "c.drawBitmap(packs," in w

# The cosmetic selector is removed, but head equipment slots and saved data survive.
assert "headLookV96" not in ui and "HEADGEAR LOOK" not in ui
assert "game.headgearStyleV96=" not in ui
assert 'headgearStyleV96=Math.floorMod(host.prefs.getInt("headgearStyleV96",0),4)' in g
assert '.putInt("headgearStyleV96",headgearStyleV96)' in g
assert '"HEAD","TORSO","LEGS","BOOTS"' in wardrobe
assert "public final int[] equipped={-1,-1,-1,-1};" in wardrobe
assert "public boolean equip(int slot,int variant)" in wardrobe
assert "public String encode()" in wardrobe and "public void decode(String src)" in wardrobe

# Character bodies, pants, boots, backpacks, weapons and original heads
# still use their preexisting drawing routes; this change must not remove them.
assert "characterSkinsV109.draw(c,skinIdV109," in g
assert "BootArtV133.COUNT" in g
assert "wardrobeV92.equipped[1]" in g and "wardrobeV92.equipped[2]" in g
assert "wearableArtV96.drawPack(" in g
assert "void draw(" in skins and "head(id)" in skins
assert "packLookV96" in ui and "bootLookV133" in ui

print("PASS V138: headgear visuals permanently suppressed; slots, saves, clothing, packs, boots and source heads preserved")
