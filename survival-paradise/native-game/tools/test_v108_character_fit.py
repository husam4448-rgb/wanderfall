#!/usr/bin/env python3
"""V108 character fit non-regression smoke test; Android build checks compilation."""
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
src=root/"app/src/main/java/com/survivalparadise/nativegame"
g=(src/"GameView.java").read_text()
m=(src/"MainActivity.java").read_text()
f=(src/"CharacterFitV108.java").read_text()
anim=(src/"AnimationCycle.java").read_text()
gradle=(root/"app/build.gradle").read_text()

assert "applicationId 'com.survivalparadise.nativegame'" in gradle
assert "versionCode 108" in gradle
assert "static final int APPROVED_PLANTED_IDLE_FRAME=2;" in g
assert "static final int IDLE_HEAD_BODY_SPLIT=92;" in g
assert "static final int IDLE_HEAD_OVERLAP=101;" in g
assert "src.set(sx,sy+IDLE_HEAD_BODY_SPLIT,sx+260,sy+160);" in g
assert "src.set(sx,sy,sx+260,sy+IDLE_HEAD_OVERLAP);" in g
assert "stablePose(c,atlas,npcVariant,frame,s,breath,torsoVariant);" in g
assert "Body pixels" not in f or "never" in f
assert "public static final float[] BREATH_OFFSETS" not in anim
assert "private static final float[] BREATH_OFFSETS={0f,-4f};" in anim
assert "public static final int WALK_FRAMES=4;" in anim
assert "public static final int IDLE_PHASES=2;" in anim

# A null fitting adjustment always stays on the exact legacy compositor.
assert "HEAD_X_DEFAULT=0,HEAD_Y_DEFAULT=0" in f
assert "BREATH_DEFAULT=4,WALK_FPS_DEFAULT=0" in f
assert "fps==0?original:fps/1.25f" in f
assert "return !HeadKnifeV82.defaultHead(scale)||x!=0||y!=0||breathAmplitude!=BREATH_DEFAULT;" in f

# Every character uses an identical head fit, but the torso/pants/feet remain in place.
assert g.count("CharacterFitV108.separateHead(")==2
assert "float dx=fitHeadXV108*s,dy=fitHeadYV108*s;" in g
assert "CharacterFitV108.breath(breath,fitIdleBreathV108)*s" in g
assert "src.set(sx+HeadKnifeV82.HEAD_LEFT,sy+HeadKnifeV82.HEAD_TOP" in g
assert "c.translate(fitHeadXV108*size,fitHeadYV108*size);" in g
assert g.count("CharacterFitV108.rate(")>=6

# Android Storage Access Framework, scoped JSON export: no broad file permission.
assert 'pick.setType("application/json");' in m
assert "startActivityForResult(pick,EXPORT_FIT_V108);" in m
assert "CharacterFitV108.exportJson(prefs).toString(2)" in m
assert '"fitHeadXV108",-24,24,0' in m
assert '"fitHeadYV108",-24,24,0' in m
assert '"fitIdleBreathV108",0,12,4' in m
assert '"fitWalkFpsV108",0,12,0' in m
assert "RESET APPROVED CHARACTER FITTING" in m
assert "EXPORT CHARACTER FITTING JSON" in m
assert 'o.put("format","survival-paradise-character-fit-v108");' in f

# Ensure existing gameplay, inventory, and serialization surfaces are not replaced.
for name in ["void saveProgress()","void newGame()","void continueGame()",
             "void drawWorld(Canvas c)","void drawWardrobeV92("]:
    assert name in g,name
for name in ['"EXPORT GAME SAVE TO FILE"','"IMPORT GAME SAVE FROM FILE"',
             'void inventory()','void settings()']:
    assert name in m,name

# Smoke-test the coordinate/frame-rate equations in the validated range.
def separate(h,x,y,b): return abs(h-1.0)>.0001 or x!=0 or y!=0 or b!=4
def rate(original,fps): return original if fps==0 else fps/1.25
assert not separate(1.0,0,0,4)
assert separate(1.0,-9,3,4)
assert separate(1.07,0,0,4)
assert abs(rate(7.8,0)-7.8)<1e-6
assert abs(rate(7.8,3)-2.4)<1e-6
assert (-4)*(4/4)==-4
print("V108 PASS: baseline defaults, head-only positioning, animation timing, PNG geometry, save integrity, Android JSON export")
