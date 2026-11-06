#!/usr/bin/env bash
set -euo pipefail
PKG=com.survivalparadise.nativegame.v130survivalqa
APP="$PKG/com.survivalparadise.nativegame.MainActivity"
APK=survival-paradise/native-game/app/build/outputs/apk/debug/app-debug.apk
mkdir -p artifacts
adb install -r "$APK"
adb shell am start -n "$APP"
sleep 9
adb exec-out screencap -p > /tmp/v130_menu_screen.png
read W H < <(python3 - <<'PY'
from struct import unpack
p=open('/tmp/v130_menu_screen.png','rb').read(24)
assert p[:8]==b'\x89PNG\r\n\x1a\n'
print(*unpack('>II',p[16:24]))
PY
)
test "$W" -gt "$H"
NEW_X=$((W/2 - 132*H/660))
CONT_X=$((W/2 + 132*H/660))
MENU_Y=$((378*H/660))
adb shell input tap "$NEW_X" "$MENU_Y"
sleep 11
adb shell screencap -p /sdcard/V130_Outdoor_Camp_QA.png
adb pull /sdcard/V130_Outdoor_Camp_QA.png artifacts/SP_V130_Outdoor_Camp_QA.png
# Capture the enlarged exterior at the actual stable motel gate.
adb shell am force-stop "$PKG"
adb exec-out run-as "$PKG" cat shared_prefs/survival_paradise_native_v34.xml > /tmp/v130-prefs.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
path='/tmp/v130-prefs.xml'
root=ET.parse(path).getroot()
def setv(name,tag,value):
    for node in list(root):
        if node.attrib.get('name')==name:
            root.remove(node)
    ET.SubElement(root,tag,{'name':name,'value':str(value)})
setv('px','float','2170.0')
setv('py','float','-296.0')
setv('hasSave','boolean','true')
setv('inside_clinic_v89','boolean','false')
setv('v128_world_coords','boolean','true')
ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
PY
adb push /tmp/v130-prefs.xml /data/local/tmp/v130-prefs.xml
adb shell chmod 644 /data/local/tmp/v130-prefs.xml
adb shell run-as "$PKG" sh -c "cat /data/local/tmp/v130-prefs.xml > shared_prefs/survival_paradise_native_v34.xml"
adb shell am start -n "$APP"
sleep 7
adb shell input tap "$CONT_X" "$MENU_Y"
sleep 10
adb shell screencap -p /sdcard/V130_Enlarged_Motel_QA.png
adb pull /sdcard/V130_Enlarged_Motel_QA.png artifacts/SP_V130_Enlarged_Motel_QA.png
# Capture the exact same saved game after loading an existing room.
adb shell am force-stop "$PKG"
adb exec-out run-as "$PKG" cat shared_prefs/survival_paradise_native_v34.xml > /tmp/v130-prefs.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
path='/tmp/v130-prefs.xml'
root=ET.parse(path).getroot()
def setv(name,tag,value):
    for node in list(root):
        if node.attrib.get('name')==name:
            root.remove(node)
    ET.SubElement(root,tag,{'name':name,'value':str(value)})
setv('px','float','1360.0')
setv('py','float','1757.8')
setv('hasSave','boolean','true')
setv('active_site_v91','int','8')
setv('inside_clinic_v89','boolean','true')
setv('clinic_scaled_v90','boolean','true')
setv('clinic_return_x_v89','float','2170.0')
setv('clinic_return_y_v89','float','-300.0')
ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
PY
adb push /tmp/v130-prefs.xml /data/local/tmp/v130-prefs.xml
adb shell chmod 644 /data/local/tmp/v130-prefs.xml
adb shell run-as "$PKG" sh -c "cat /data/local/tmp/v130-prefs.xml > shared_prefs/survival_paradise_native_v34.xml"
adb shell am start -n "$APP"
sleep 7
adb shell input tap "$CONT_X" "$MENU_Y"
sleep 10
adb shell screencap -p /sdcard/V130_Interior_Cone_QA.png
adb pull /sdcard/V130_Interior_Cone_QA.png artifacts/SP_V130_Interior_Cone_QA.png
python3 - <<'PY'
from pathlib import Path
from struct import unpack
for name in ['SP_V130_Outdoor_Camp_QA.png','SP_V130_Enlarged_Motel_QA.png','SP_V130_Interior_Cone_QA.png']:
    p=Path('artifacts')/name
    data=p.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=unpack('>II',data[16:24])
    assert width>400 and height>300, (name,width,height)
    print('V130 EMULATOR CAPTURE',name,width,height,len(data))
PY
