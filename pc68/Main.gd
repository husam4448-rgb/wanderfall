extends Node2D
## PC68: proportions-restored native RIGHT male with real SP head/torso diagnostic.
## Two true original-SP trouser textures on independently articulated thigh/shin
## draw panels plus independent rigid boot per leg. No commercial geometry or pixels.
const FRONT_TROUSERS:Texture2D=preload("res://assets/PC68_MaleRight_Front_Trouser.png")
const REAR_TROUSERS:Texture2D=preload("res://assets/PC68_MaleRight_Rear_Trouser.png")
const BOOT:Texture2D=preload("res://assets/SP_PC63_MaleRight_L_leg02_BOOT.png")
const PELVIS:Texture2D=preload("res://assets/PC68_MaleRight_Belt_Pelvis.png")
const UPPER_BODY:Texture2D=preload("res://assets/PC68_MaleRight_Approved_Torso_Head.png")
const GRID_W:int=10
const GRID_H:int=6
const FRAMES:int=32
const GROUND:float=502.0
const BOOT_SCALE:float=0.78
const BOOT_PIVOT:Vector2=Vector2(22.0,21.0)
const BOOT_HEEL_PIXEL:Vector2=Vector2(18.0,51.0)
const CLOTH_WIDTH:float=0.69
const PC65_KNEE_DEFAULT_STIFFNESS:float=0.65
const PC65_KNEE_SOFT_ZONE:float=0.30
var knee_stiffness:float=PC65_KNEE_DEFAULT_STIFFNESS
var uv_points:Array[Vector2]=[]
var triangles:Array[PackedInt32Array]=[]
var pose:Dictionary={}
var records:Array=[]
var layer:String="both"

func _ready()->void:
    var test_value:String=OS.get_environment("PC65_KNEE_STIFFNESS")
    if not test_value.is_empty():
        knee_stiffness=clampf(test_value.to_float(),0.0,0.8)
    # Two original-texture fabric panels join at the actual IK knee pivot.
    # The upper texture overlaps the lower by a few original SP pixels;
    # no across-the-knee triangles can turn inside out at high flexion.
    var y_uv:PackedFloat32Array=PackedFloat32Array([0.0,40.0,86.0,80.0,120.0,159.0])
    for y in range(GRID_H):
        for x in range(GRID_W):
            uv_points.append(Vector2(float(x)*79.0/float(GRID_W-1),y_uv[y]))
    for y in range(GRID_H-1):
        if y==2:
            continue
        for x in range(GRID_W-1):
            var a:int=y*GRID_W+x
            triangles.append(PackedInt32Array([a,a+1,a+GRID_W]))
            triangles.append(PackedInt32Array([a+1,a+GRID_W+1,a+GRID_W]))
    if uv_points.size()!=60 or triangles.size()!=72:
        push_error("PC67_HINGE_PANEL_TOPOLOGY_INVALID")
        get_tree().quit(71)
        return
    if OS.get_environment("PC68_CAPTURE")=="1":
        call_deferred("_capture")
    else:
        _pose(0)
        queue_redraw()

static func _two_bone(hip:Vector2,ankle:Vector2,upper:float,lower:float)->Dictionary:
    var d:Vector2=ankle-hip
    var length:float=d.length()
    if length<0.001 or length>=upper+lower-0.0001 or length<=absf(upper-lower)+0.0001:
        return {"ok":false,"distance":length}
    var a:float=(upper*upper+length*length-lower*lower)/(2.0*length)
    var height:float=sqrt(maxf(0.0,upper*upper-a*a))
    var unit:Vector2=d/length
    var knee:Vector2=hip+unit*a+Vector2(unit.y,-unit.x)*height
    return {"ok":true,"knee":knee,"knee_forward":height,
            "upper_error":absf(hip.distance_to(knee)-upper),
            "lower_error":absf(knee.distance_to(ankle)-lower)}

static func _swing(a:Vector2,b:Vector2,u:float)->Vector2:
    var v:float=clampf(u,0.0,1.0)
    var smooth:float=v*v*(3.0-2.0*v)
    return a.lerp(b,smooth)+Vector2(0.0,-19.0*sin(PI*v))


## All positions are global fixture coordinates, +x right and +y down.
## The leg artwork is provisionally re-used; PC66 measures geometry, NOT 2 unique authored limbs.
func _leg_pose(index:int,frame:int,pelvis:Vector2)->Dictionary:
    var lead:bool=index==0
    var stance:bool=frame<16 if lead else frame>=16
    var hip:Vector2=pelvis+(Vector2(2.0,-1.0) if lead else Vector2(-5.0,1.0))
    var boot_heel:Vector2
    var foot_pitch:float=0.0
    if stance:
        boot_heel=Vector2(330.0 if lead else 366.0,GROUND)
    else:
        var u:float=float(frame-16)/16.0 if lead else float(frame)/16.0
        boot_heel=_swing(Vector2(330.0 if lead else 294.0,GROUND),
                         Vector2(402.0 if lead else 366.0,GROUND),u)
        foot_pitch=deg_to_rad(-8.0*sin(PI*u))
    var ankle:Vector2=boot_heel-((BOOT_HEEL_PIXEL-BOOT_PIVOT)*BOOT_SCALE).rotated(foot_pitch)
    var ik:Dictionary=_two_bone(hip,ankle,77.0,77.0)
    if not ik["ok"]:
        push_error("PC66_UNREACHABLE_LEG_"+str(index)+" frame="+str(frame))
        get_tree().quit(72)
        return {}
    var knee:Vector2=ik["knee"]
    var thigh_axis:Vector2=(knee-hip).normalized()
    var shin_axis:Vector2=(ankle-knee).normalized()
    var vtx:Array[Vector2]=[]
    for idx in range(uv_points.size()):
        var tex_coord:Vector2=uv_points[idx]
        var row:int=idx/GRID_W
        var center:Vector2
        var direction:Vector2
        if row<=2:
            center=hip.lerp(knee,tex_coord.y/86.0)
            direction=thigh_axis
        else:
            center=knee.lerp(ankle,(tex_coord.y-80.0)/79.0)
            direction=shin_axis
        var normal:Vector2=Vector2(direction.y,-direction.x)
        var width_offset:float=(tex_coord.x-39.5)*CLOTH_WIDTH
        vtx.append(center+normal*width_offset)
    return {"id":"front" if lead else "rear","hip":hip,"ankle":ankle,
            "knee":knee,"heel":boot_heel,"pitch":foot_pitch,"stance":stance,
            "ik":ik,"trouser_vertices":vtx}

func _pose(i:int)->void:
    var frame:float=float(i)
    var pelvis:Vector2=Vector2(303.0+72.0*frame/32.0,
                             330.0-1.6*pow(sin(PI*frame/16.0),2.0))
    var front:Dictionary=_leg_pose(0,i,pelvis)
    var rear:Dictionary=_leg_pose(1,i,pelvis)
    if front.is_empty() or rear.is_empty():
        pose={}
        return
    pose={"root":pelvis,"legs":[front,rear],"phase":i}

func _draw_leg(leg:Dictionary,which:String)->void:
    if which=="trouser":
        var shape:Array=leg["trouser_vertices"]
        for tri in triangles:
            var positions:=PackedVector2Array()
            var tex_coords:=PackedVector2Array()
            var colors:=PackedColorArray()
            for k in tri:
                positions.append(shape[k])
                tex_coords.append(Vector2(uv_points[k].x/79.0,uv_points[k].y/159.0))
                colors.append(Color.WHITE)
            draw_polygon(positions,colors,tex_coords,FRONT_TROUSERS if leg["id"]=="front" else REAR_TROUSERS)
    elif which=="boot":
        draw_set_transform(leg["ankle"],leg["pitch"],Vector2(BOOT_SCALE,BOOT_SCALE))
        draw_texture(BOOT,-BOOT_PIVOT)
        draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _draw()->void:
    if pose.is_empty():return
    var root:Vector2=pose["root"]
    var front:Dictionary=pose["legs"][0]
    var rear:Dictionary=pose["legs"][1]
    if layer=="both":
        draw_line(Vector2(55.0,GROUND),Vector2(810.0,GROUND),Color(0.60,0.62,0.63),2.0)
    if layer=="both" or layer=="rear-trouser":_draw_leg(rear,"trouser")
    if layer=="both" or layer=="rear-boot":_draw_leg(rear,"boot")
    if layer=="both" or layer=="front-trouser":_draw_leg(front,"trouser")
    if layer=="both" or layer=="front-boot":_draw_leg(front,"boot")
    if layer=="both" or layer=="pelvis":
        draw_texture_rect(PELVIS,Rect2(root+Vector2(-24.0,-20.0),Vector2(48.0,28.0)),false)
    if layer=="both" or layer=="torso":
        # Actual original RIGHT facing survivor head/torso/backpack reference alpha.
        # Source pixel landmark at (108,151) aligns with native bilateral pelvis pivot.
        draw_texture(UPPER_BODY,root-Vector2(108.0,151.0))

func _capture()->void:
    var folder:String=OS.get_environment("PC68_CAPTURE_DIR")
    if folder.is_empty():folder="/tmp/pc68-native"
    DirAccess.make_dir_recursive_absolute(folder)
    for i in range(FRAMES):
        _pose(i)
        if pose.is_empty():
            get_tree().quit(73)
            return
        layer="both"
        queue_redraw()
        await RenderingServer.frame_post_draw
        var picture:Image=get_viewport().get_texture().get_image()
        if picture.save_png(folder.path_join("frame_%03d.png"%i))!=OK:
            push_error("PC66_FRAME_SAVE_FAILURE")
            get_tree().quit(74)
            return
        if i%4==0:
            for k in ["rear-trouser","rear-boot","front-trouser","front-boot","pelvis","torso"]:
                layer=k
                queue_redraw()
                await RenderingServer.frame_post_draw
                var separate:Image=get_viewport().get_texture().get_image()
                if separate.save_png(folder.path_join("%s_%03d.png"%[k,i]))!=OK:
                    push_error("PC66_LAYER_SAVE_FAILURE "+k)
                    get_tree().quit(75)
                    return
        var out_legs:Array=[]
        for leg in pose["legs"]:
            var verts:Array=[]
            for point in leg["trouser_vertices"]:
                verts.append([point.x,point.y])
            var serialized:Dictionary={"id":leg["id"],"stance":leg["stance"],
                "hip":[leg["hip"].x,leg["hip"].y],
                "knee":[leg["knee"].x,leg["knee"].y],
                "ankle":[leg["ankle"].x,leg["ankle"].y],
                "heel":[leg["heel"].x,leg["heel"].y],
                "boot_pitch":leg["pitch"],
                "forward_knee_clearance":leg["ik"]["knee_forward"],
                "upper_segment_residual":leg["ik"]["upper_error"],
                "lower_segment_residual":leg["ik"]["lower_error"],
                "cloth_vertices":verts}
            out_legs.append(serialized)
        records.append({"frame":i,"time_seconds":float(i)/30.0,
                        "pelvis":[pose["root"].x,pose["root"].y],"legs":out_legs})
    var output:FileAccess=FileAccess.open(folder.path_join("pose_metrics.json"),FileAccess.WRITE)
    if output==null:
        push_error("PC66_JSON_WRITE_FAILURE")
        get_tree().quit(76)
        return
    var tris:Array=[]
    for tri in triangles:tris.append(Array(tri))
    output.store_string(JSON.stringify({"frames":records,"triangles":tris,
        "source":"Original male EAST upright head/torso + two original front/rear trouser masks + independent source boots, proportions restored.",
        "provisional_reused_leg_art":false,
        "two_independent_ik_chains":true,
        "commercial_reference_geometry_included":false,
        "knee_stiffness":knee_stiffness,
        "cloth_mode":"two_source_fabric_panels_at_real_ik_knee",
        "torso_mode":"approved_original_male_east_alpha",
        "visual_status":"PENDING_HUMAN_APPROVAL"}))
    output.close()
    print("PC68_GODOT_FULL_SILHOUETTE_CAPTURED frames=32 legs=2 torso=approved_right_source")
    get_tree().quit()
