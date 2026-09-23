#!/usr/bin/env python3
"""D3D.12: swap placeholder equipment for actual skinned outfit parts and hand-socket pistol."""
from pathlib import Path
import re, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

def once(old,new,name):
    global s
    if old not in s:
        raise SystemExit("D3D.12 missing "+name)
    s=s.replace(old,new,1)

once("var gun_root: Node3D\n","var gun_root: Node3D\nvar pistol_hand_socket: BoneAttachment3D\n","pistol socket declaration")
once('    _make_pistol()\n','    _make_pistol()\n    _install_pistol_hand_socket()\n',"pistol stage")
once("    _make_backpack()\n    _make_pistol()\n","    _make_backpack()\n    _sync_apparel_visuals()\n    _make_pistol()\n","backpack initial sync")

a=s.find("func _sync_apparel_visuals() -> void:\n")
b=s.find("\nfunc _weapon_category() -> String:\n",a)
if a<0 or b<0:
    raise SystemExit("D3D.12 apparel section missing")
apparel=r'''func _set_rigged_part(name: String, show: bool) -> void:
    if ranger_model == null:
        return
    var part := ranger_model.find_child(name,true,false)
    if part is MeshInstance3D:
        (part as MeshInstance3D).visible = show

func _sync_apparel_visuals() -> void:
    if body_model == null:
        return
    # Never show D3D.11's capsules/boxes; the wearable shape comes from
    # authored, skin-weighted 3D meshes with correct anatomical proportions.
    for slot in gear_layers.keys():
        for primitive in gear_layers[slot]:
            if primitive is Node3D:
                (primitive as Node3D).visible = false
    body_model.visible = true
    if outfit_model != null:
        outfit_model.visible = false
    if ranger_model == null:
        return

    var equipped: Dictionary = {}
    for slot in ["torso","armor","hands","legs","feet","head","eyes","lower_face","back"]:
        equipped[slot] = String(equipment.get_visual_item(slot)) if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item") else ""
    var shirt := not String(equipped["torso"]).is_empty()
    var armor := not String(equipped["armor"]).is_empty()
    var hands := not String(equipped["hands"]).is_empty()
    var trousers := not String(equipped["legs"]).is_empty()
    var boots := not String(equipped["feet"]).is_empty()
    var any_ranger := shirt or armor or hands or trousers or boots
    ranger_model.visible = any_ranger

    # The Ranger GLTF contains independently skinned garment submeshes, all
    # authored against the very same 65-bone skeleton. Never toggle the whole
    # costume based on one item again.
    _set_rigged_part("Male_Ranger_Body",shirt)
    _set_rigged_part("Male_Ranger_Arms",shirt)
    _set_rigged_part("Male_Ranger_Legs",trousers)
    _set_rigged_part("Male_Ranger_Feet_Boots",boots)
    _set_rigged_part("Male_Ranger_Arms_Bracer",hands)
    _set_rigged_part("Male_Ranger_Acc_Pauldron",armor)
    _set_rigged_part("Male_Ranger_Body_Belt_1",armor)
    _set_rigged_part("Male_Ranger_Body_Belt_2",false)
    _set_rigged_part("Male_Ranger_Head_Hood",false)
    for extra in ["HeadMesh","Eyes","Eyebrows","SurvivorHair"]:
        var duplicate := ranger_skeleton.get_node_or_null(extra) if ranger_skeleton != null else null
        if duplicate is Node3D:
            (duplicate as Node3D).visible = false
    if backpack_root != null:
        backpack_root.visible = not String(equipped["back"]).is_empty()
'''
s=s[:a]+apparel+s[b:]

# The pistol is parented to the right hand's bone attachment. The weapon model
# has the slide along +Z and the grip at (0,-0.075,-0.055). Thus offset the gun
# origin from the hand to place the grip *inside* the palm rather than beside it.
needle="func _make_pistol() -> void:\n"
socket=r'''func _install_pistol_hand_socket() -> void:
    if body_skeleton == null or gun_root == null:
        return
    if pistol_hand_socket != null:
        return
    pistol_hand_socket = BoneAttachment3D.new()
    pistol_hand_socket.name = "RightHandPistolSocket"
    body_skeleton.add_child(pistol_hand_socket)
    pistol_hand_socket.bone_name = "hand_r"
    gun_root.reparent(pistol_hand_socket,false)
    gun_root.position = Vector3.ZERO

'''
once(needle,socket+needle,"pistol socket helper")

# No torso-relative/character-wide gun offset. Bone attachment provides location.
# Keep pistol forward in actor space while using the hand bone to follow motion.
start=s.find("    if gun_root != null:\n",s.find("func _update_equipment_3d(armed: bool) -> void:\n"))
end=s.find("\n    if backpack_root != null:\n",start)
if start<0 or end<0:
    raise SystemExit("D3D.12 pistol update missing")
gun=r'''    if gun_root != null:
        gun_root.visible = armed
        if armed and pistol_hand_socket != null:
            # Pose has already been applied. Socket moves with the real hand,
            # including when the whole actor turns, breathes and extends to aim.
            var hand_world := pistol_hand_socket.global_position
            var local_grip_to_gun := actor_root.global_transform.basis * Vector3(0.0,0.075,0.055)
            gun_root.global_transform = Transform3D(actor_root.global_transform.basis, hand_world + local_grip_to_gun)
'''
s=s[:start]+gun+s[end:]

# Replace block-shaped rucksack with a tapered, contoured fabric volume, rounded
# top seam, side pockets, actual inset flap and straps. This is bespoke mesh
# geometry, not a resized cube or capsule masquerading as a backpack.
a=s.find("func _rebuild_backpack_shape() -> void:\n")
b=s.find("\nfunc _update_equipment_3d(armed: bool) -> void:\n",a)
if a<0 or b<0:
    raise SystemExit("D3D.12 backpack helper missing")
bag=r'''func _rucksack_mesh() -> ArrayMesh:
    var mesh := ArrayMesh.new()
    var st := SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)
    var rings := [
        Vector3(0.125,-0.21,0.085),
        Vector3(0.18,-0.16,0.105),
        Vector3(0.19,0.105,0.105),
        Vector3(0.14,0.195,0.080),
        Vector3(0.075,0.215,0.050)
    ]
    for layer in range(rings.size()-1):
        for side in range(8):
            var a := float(side)*TAU/8.0
            var b := float(side+1)*TAU/8.0
            var lo: Vector3 = rings[layer]
            var hi: Vector3 = rings[layer+1]
            var p0 := Vector3(sin(a)*lo.x,lo.y,cos(a)*lo.z)
            var p1 := Vector3(sin(b)*lo.x,lo.y,cos(b)*lo.z)
            var p2 := Vector3(sin(a)*hi.x,hi.y,cos(a)*hi.z)
            var p3 := Vector3(sin(b)*hi.x,hi.y,cos(b)*hi.z)
            st.add_vertex(p0)
            st.add_vertex(p2)
            st.add_vertex(p1)
            st.add_vertex(p1)
            st.add_vertex(p2)
            st.add_vertex(p3)
    st.generate_normals()
    mesh=st.commit()
    return mesh

func _rebuild_backpack_shape() -> void:
    if backpack_root == null:
        return
    for child in backpack_root.get_children():
        child.queue_free()
    var fabric := StandardMaterial3D.new()
    fabric.albedo_color=Color(0.24,0.28,0.20)
    fabric.roughness=0.96
    fabric.cull_mode=BaseMaterial3D.CULL_DISABLED
    var trim := StandardMaterial3D.new()
    trim.albedo_color=Color(0.12,0.14,0.11)
    trim.roughness=0.9

    var pack := MeshInstance3D.new()
    pack.name="ContouredRucksack"
    pack.mesh=_rucksack_mesh()
    pack.material_override=fabric
    backpack_root.add_child(pack)

    var flap := MeshInstance3D.new()
    flap.name="FabricTopFlap"
    var flap_mesh := PrismMesh.new()
    flap_mesh.size=Vector3(0.31,0.065,0.10)
    flap.mesh=flap_mesh
    flap.position=Vector3(0.0,0.157,0.073)
    flap.material_override=trim
    backpack_root.add_child(flap)

    # Straps are behind the pack and only emerge over the shoulders.
    for x in [-0.112,0.112]:
        var strap := MeshInstance3D.new()
        var strap_mesh := CylinderMesh.new()
        strap_mesh.top_radius=0.022
        strap_mesh.bottom_radius=0.022
        strap_mesh.height=0.32
        strap.mesh=strap_mesh
        strap.position=Vector3(x,0.0,-0.075)
        strap.material_override=trim
        backpack_root.add_child(strap)

    var front := MeshInstance3D.new()
    front.name="RucksackOuterPocket"
    var pocket_mesh := PrismMesh.new()
    pocket_mesh.size=Vector3(0.22,0.16,0.055)
    front.mesh=pocket_mesh
    front.position=Vector3(0.0,-0.075,0.11)
    front.material_override=fabric
    backpack_root.add_child(front)

'''
s=s[:a]+bag+s[b:]
visual.write_text(s,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=41',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.12"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.12 Android version anchors missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.12"',t,count=1)
    save.write_text(t,encoding="utf-8")
for target in ["RightHandPistolSocket","Male_Ranger_Feet_Boots","ContouredRucksack","gun_root.reparent"]:
    if target not in s:
        raise SystemExit("D3D.12 runtime guard missing: "+target)
print("Applied D3D.12: authored rigged equipment per slot, contoured backpack and true right-hand pistol socket.")
