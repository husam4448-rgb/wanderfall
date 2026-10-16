extends Node2D
## PC58 real approved art on a Bone2D articulated adult male RIGHT rig.
## Actual source pixels, not an invented full painted character.
## IMPORTANT: original source leg shapes have NO painted concealed knee surfaces.
const S:float=1.5
const N:int=32
const SOURCE_PELVIS:Vector2=Vector2(112.0,140.0)
const GROUND:float=492.0
const REFERENCES:Dictionary={
    "front_thigh":Vector2(88.0,160.0),
    "front_shin":Vector2(79.0,182.0),
    "front_boot":Vector2(84.0,227.0),
    "back_thigh":Vector2(132.0,155.0),
    "back_shin":Vector2(131.0,184.0),
    "back_boot":Vector2(138.0,216.0)
}
const PARENTS:Dictionary={
    "head_neck":"torso",
    "dominant_hand":"near_forearm",
    "support_hand":"rifle_stock",
    "near_forearm":"near_upper_arm",
    "near_upper_arm":"torso",
    "rifle_stock":"",
    "rifle_receiver":"rifle_stock",
    "torso":"pelvis",
    "backpack":"torso",
    "front_thigh":"pelvis",
    "back_thigh":"pelvis",
    "front_shin":"front_thigh",
    "back_shin":"back_thigh",
    "front_boot":"front_shin",
    "back_boot":"back_shin"
}
var skeleton:Skeleton2D
var bones:Dictionary={}
var records:Array=[]

func _ready()->void:
    var path:String="res://assets/manifest.json"
    var data:Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
    if not data is Dictionary or data.get("part_count",0)!=16:
        push_error("PC58_SOURCE_PARTS_MISSING")
        get_tree().quit(3)
        return
    skeleton=Skeleton2D.new()
    skeleton.name="PC58_ApprovedCharacter_Rig"
    skeleton.scale=Vector2(S,S)
    add_child(skeleton)
    var pivots:Dictionary={}
    for spec in data["segments"]:
        pivots[spec["name"]]=Vector2(spec["pivot"][0],spec["pivot"][1])
    var remaining:Array=(data["segments"] as Array).duplicate()
    var loops:int=0
    while not remaining.is_empty():
        loops+=1
        if loops>20:
            push_error("PC58_INVALID_SOURCE_PARENTS")
            get_tree().quit(7)
            return
        var waiting:Array=[]
        for spec in remaining:
            var name:String=str(spec["name"])
            var parent_name:String=str(PARENTS.get(name,""))
            if parent_name!="" and not bones.has(parent_name):
                waiting.append(spec)
                continue
            var bone:Bone2D=Bone2D.new()
            bone.name="Bone_"+name
            bone.position=pivots[name]-(pivots[parent_name] if parent_name!="" else Vector2.ZERO)
            var parent_node:Node2D=skeleton if parent_name=="" else bones[parent_name]
            parent_node.add_child(bone)
            var img:Image=Image.load_from_file(ProjectSettings.globalize_path("res://assets/"+str(spec["filename"])))
            if img==null or img.is_empty():
                push_error("PC58_MISSING_SOURCE_TEXTURE "+name)
                get_tree().quit(8)
                return
            var sprite:Sprite2D=Sprite2D.new()
            sprite.texture=ImageTexture.create_from_image(img)
            sprite.centered=false
            sprite.position=-pivots[name]
            sprite.name="Source_"+name
            sprite.z_index=32-int(data["ordering"].find(name)) if (data["ordering"] as Array).has(name) else 17
            bone.add_child(sprite)
            bones[name]=bone
        if waiting.size()==remaining.size():
            push_error("PC58_SOURCE_BONE_LOOP")
            get_tree().quit(10)
            return
        remaining=waiting
    if bones.size()!=16:
        push_error("PC58_MISSING_BONES")
        get_tree().quit(11)
        return
    # PC59: original complete hidden clothing surfaces go UNDER original source
    # pixels in their parent bone local frame. NO new pivots are fabricated.
    if data.has("underpaint"):
        var inner:Array=data["underpaint"]
        if inner.size()!=6:
            push_error("PC59_UNDERPAINT_LAYER_COUNT_INVALID")
            get_tree().quit(91)
            return
        for spec in inner:
            var source_parent:String=str(spec["parent"])
            if not bones.has(source_parent):
                push_error("PC59_UNDERPAINT_MISSING_PARENT "+source_parent)
                get_tree().quit(92)
                return
            var picture:Image=Image.load_from_file(ProjectSettings.globalize_path("res://assets/"+str(spec["filename"])))
            if picture==null or picture.is_empty():
                push_error("PC59_UNDERPAINT_MISSING_ART "+str(spec["filename"]))
                get_tree().quit(93)
                return
            var under:Sprite2D=Sprite2D.new()
            under.texture=ImageTexture.create_from_image(picture)
            under.name="OriginalUnderpaint_"+str(spec["name"])
            under.centered=false
            under.position=-pivots[source_parent]
            under.z_index=-8
            (bones[source_parent] as Bone2D).add_child(under)
        print("PC59_ORIGINAL_INNER_CLOTH_LOADED layers="+str(inner.size()))
    if OS.get_environment("PC58_CAPTURE")=="1":
        call_deferred("_capture")
    else:
        _pose(0)

func _leg_ik(hip:Vector2,target:Vector2,upper:float,lower:float)->Dictionary:
    var d:Vector2=target-hip
    var dist:float=d.length()
    if dist<0.001:return {"valid":false}
    var reachable:bool=dist<=upper+lower-0.01 and dist>=absf(upper-lower)+0.01
    var length:float=clampf(dist,absf(upper-lower)+0.01,upper+lower-0.01)
    var axis:Vector2=d/dist
    var x:float=(upper*upper+length*length-lower*lower)/(2.0*length)
    var height:float=sqrt(maxf(0.0,upper*upper-x*x))
    var normal:Vector2=Vector2(-axis.y,axis.x)
    # For RIGHT facing, knee points towards positive X on mostly vertical legs.
    var knee:Vector2=hip+axis*x-normal*height
    return {"valid":true,"reachable":reachable,"knee":knee,"ankle":hip+axis*length}

func _to_world(source:Vector2,root:Vector2)->Vector2:
    return root+(source-SOURCE_PELVIS)*S

func _fit_leg(side:String,ankle_goal:Vector2,root:Vector2,boot_pitch:float)->Dictionary:
    var hip_name:String=side+"_thigh"
    var shin_name:String=side+"_shin"
    var boot_name:String=side+"_boot"
    var hip:Vector2=_to_world(REFERENCES[hip_name],root)
    var source_upper:Vector2=REFERENCES[shin_name]-REFERENCES[hip_name]
    var source_lower:Vector2=REFERENCES[boot_name]-REFERENCES[shin_name]
    var solution:Dictionary=_leg_ik(hip,ankle_goal,source_upper.length()*S,source_lower.length()*S)
    if not solution.get("valid",false):return {"valid":false}
    var front:Bone2D=bones[hip_name]
    var shin:Bone2D=bones[shin_name]
    var boot:Bone2D=bones[boot_name]
    var upper_world:Vector2=solution["knee"]-hip
    var lower_world:Vector2=solution["ankle"]-solution["knee"]
    var upper_rotation:float=upper_world.angle()-source_upper.angle()
    var lower_rotation:float=lower_world.angle()-source_lower.angle()
    front.rotation=upper_rotation
    shin.rotation=lower_rotation-upper_rotation
    boot.rotation=boot_pitch-lower_rotation
    return {"valid":true,"reachable":solution["reachable"],
        "knee":solution["knee"],"ankle":solution["ankle"],"hip":hip,
        "residual":(solution["ankle"] as Vector2).distance_to(ankle_goal)}

func _swing(a:Vector2,b:Vector2,t:float)->Vector2:
    var u:float=clampf(t,0.0,1.0)
    var smooth:float=u*u*(3.0-2.0*u)
    return a.lerp(b,smooth)+Vector2(0.0,-16.0*sin(PI*u))

func _pose(i:int)->void:
    var f:float=float(i)
    var root:Vector2=Vector2(300.0+70.0*f/32.0,364.0-1.0*pow(sin(f*PI/16.0),2.0))
    skeleton.position=root-SOURCE_PELVIS*S
    # One stance and one swing per 16-frame half. No manual bob in knee positions.
    var back_stance:bool=i<16
    var front_heel:Vector2
    var back_heel:Vector2
    if back_stance:
        back_heel=Vector2(345.0,GROUND)
        front_heel=_swing(Vector2(270.0,GROUND),Vector2(339.0,GROUND),f/16.0)
    else:
        front_heel=Vector2(339.0,GROUND)
        back_heel=_swing(Vector2(345.0,GROUND),Vector2(414.0,GROUND),(f-16.0)/16.0)
    var front_pitch:float=deg_to_rad(-6.0*sin(PI*f/16.0)) if back_stance else 0.0
    var back_pitch:float=0.0 if back_stance else deg_to_rad(-6.0*sin(PI*(f-16.0)/16.0))
    # The original approved boots keep their native silhouette and pivot; target
    # ankles sit ABOVE each visible heel/sole by actual source-picture offsets.
    var front_ankle:Vector2=front_heel+Vector2(0.0,-27.0)
    var back_ankle:Vector2=back_heel+Vector2(0.0,-20.0)
    var fl:Dictionary=_fit_leg("front",front_ankle,root,front_pitch)
    var bl:Dictionary=_fit_leg("back",back_ankle,root,back_pitch)
    if not fl.get("valid",false) or not bl.get("valid",false):
        push_error("PC58_INVALID_SOURCE_LEG_IK")
        get_tree().quit(12)
        return
    if not fl["reachable"] or not bl["reachable"]:
        push_error("PC58_SOURCE_ART_UNREACHABLE "+str(i)+" "+str(fl["residual"])+" "+str(bl["residual"]))
        get_tree().quit(13)
        return
    var torso:Bone2D=bones["torso"]
    torso.rotation=deg_to_rad(0.7*sin(f*TAU/16.0))
    # The actual source rifle and both hands remain source-authored and fixed
    # relative to the torso. New weapon IK art still requires separate underpaint.
    records.append({"frame":i,"time_seconds":f/30.0,
        "root":[root.x,root.y],
        "feet":{"front":{"heel_world":[front_heel.x,front_heel.y],"stance":not back_stance},
                "back":{"heel_world":[back_heel.x,back_heel.y],"stance":back_stance}},
        "leg_reach":{"front":fl["residual"],"back":bl["residual"]},
        "knee":{"front":[fl["knee"].x,fl["knee"].y],"back":[bl["knee"].x,bl["knee"].y]},
        "ankle":{"front":[fl["ankle"].x,fl["ankle"].y],"back":[bl["ankle"].x,bl["ankle"].y]}})

func _capture()->void:
    var folder:String=OS.get_environment("PC58_CAPTURE_DIR")
    if folder.is_empty():folder="/tmp/pc58_frames"
    DirAccess.make_dir_recursive_absolute(folder)
    for i in range(N):
        _pose(i)
        await RenderingServer.frame_post_draw
        var img:Image=get_viewport().get_texture().get_image()
        if img.save_png(folder.path_join("frame_%03d.png"%i))!=OK:
            push_error("PC58_FRAME_CAPTURE_FAILED")
            get_tree().quit(14)
            return
    var file:FileAccess=FileAccess.open(folder.path_join("source_art_frames.json"),FileAccess.WRITE)
    if file==null:
        push_error("PC58_CANNOT_WRITE_FRAMES")
        get_tree().quit(15)
        return
    file.store_string(JSON.stringify({"frames":records,"status":"SOURCE_ART_FIT_VISUAL_QA_REQUIRED"}))
    file.close()
    print("PC58_REAL_APPROVED_ART_RIG_CAPTURED frames="+str(N)+" source_parts="+str(bones.size()))
    get_tree().quit()
