extends Node2D
## PC57B separate Godot pose renderer. Procedural shapes are NOT finished character art.
const IK=preload("res://SPUpperBodyIK.gd")
const N:int=32
const GROUND:float=490.0
var pose:Dictionary={}
var evidence:Array=[]

func _ready()->void:
    if OS.get_environment("PC57B_CAPTURE")=="1":
        call_deferred("_capture")
    else:
        _pose(0)
        queue_redraw()

func swing(start:Vector2, finish:Vector2, t:float)->Vector2:
    var u:float=clampf(t,0.0,1.0)
    var smooth:float=u*u*(3.0-2.0*u)
    return start.lerp(finish,smooth)+Vector2(0.0,-19.0*sin(PI*u))

func _pose(i:int)->void:
    var f:float=float(i)
    var stride_progress:float=f/32.0
    var counterweight:float=1.8*sin(f*TAU/16.0)
    var vertical_bob:float=1.8*pow(sin(f*PI/16.0),2.0)
    var root:Vector2=Vector2(300.0+90.0*stride_progress+counterweight,359.0-vertical_bob)
    var tilt:float=deg_to_rad(0.9*sin(f*TAU/16.0)+0.65*sin(f*TAU/32.0))
    var shoulder_near:Vector2=root+Vector2(5.0,-86.0).rotated(tilt)
    var shoulder_far:Vector2=root+Vector2(-10.0,-89.0).rotated(tilt)
    var pivot:Vector2=root+Vector2(22.0,-73.0)+Vector2(0.0,1.4*sin(f*TAU/16.0+0.3))
    var rifle:Dictionary=IK.sockets(pivot,deg_to_rad(-4.0+1.5*sin(f*TAU/32.0)))
    var dominant:Dictionary=IK.solve(shoulder_near,rifle["trigger"],44.0,41.0,1.0)
    var support:Dictionary=IK.solve(shoulder_far,rifle["foregrip"],54.0,51.0,1.0)
    var stance_left:bool=i<16
    var foot_left:Vector2
    var foot_right:Vector2
    var angle_left:float=0.0
    var angle_right:float=0.0
    if stance_left:
        foot_left=Vector2(286.0,GROUND)
        var right_swing:float=f/16.0
        foot_right=swing(Vector2(260.0,GROUND),Vector2(350.0,GROUND),right_swing)
        angle_right=deg_to_rad(-8.0*sin(PI*right_swing))
    else:
        foot_right=Vector2(350.0,GROUND)
        var left_swing:float=(f-16.0)/16.0
        foot_left=swing(Vector2(286.0,GROUND),Vector2(376.0,GROUND),left_swing)
        angle_left=deg_to_rad(-8.0*sin(PI*left_swing))
    var ankle_left_target:Vector2=foot_left+Vector2(0.0,-8.0)
    var ankle_right_target:Vector2=foot_right+Vector2(0.0,-8.0)
    var hip_left:Vector2=root+Vector2(-14.0,6.0)
    var hip_right:Vector2=root+Vector2(12.0,6.0)
    # Screen-right knees both bend forward; old +1 branch caused reverse knees.
    var leg_left:Dictionary=IK.solve(hip_left,ankle_left_target,69.0,70.0,-1.0)
    var leg_right:Dictionary=IK.solve(hip_right,ankle_right_target,69.0,70.0,-1.0)
    if not dominant["valid"] or not support["valid"] or not leg_left["valid"] or not leg_right["valid"]:
        push_error("PC57B_INVALID_IK")
        get_tree().quit(82)
        return
    if not dominant["reachable"] or not support["reachable"]:
        push_error("PC57B_UNREACHABLE_RIFLE_GRIP")
        get_tree().quit(84)
        return
    if not leg_left["reachable"] or not leg_right["reachable"]:
        push_error("PC57D_UNREACHABLE_LEG_TARGET")
        get_tree().quit(86)
        return
    var anchor:Vector2=IK.equipment_anchor(root,tilt)
    pose={"root":root,"shoulder_near":shoulder_near,"shoulder_far":shoulder_far,
        "rifle":rifle,"dominant":dominant,"support":support,
        "hip_left":hip_left,"hip_right":hip_right,
        "leg_left":leg_left,"leg_right":leg_right,
        "angle_left":angle_left,"angle_right":angle_right,
        "anchor":anchor,"variant":0 if i<16 else 1}
    evidence.append({"time_seconds":f/30.0,
        "feet":{"left":{"heel_world":[(leg_left["wrist"] as Vector2).x,(leg_left["wrist"] as Vector2).y+8.0],"stance":stance_left},
                "right":{"heel_world":[(leg_right["wrist"] as Vector2).x,(leg_right["wrist"] as Vector2).y+8.0],"stance":not stance_left}},
        "hands":{"dominant":{"actual_world":[dominant["wrist"].x,dominant["wrist"].y],
                              "grip_world":[rifle["trigger"].x,rifle["trigger"].y]},
                 "support":{"actual_world":[support["wrist"].x,support["wrist"].y],
                            "grip_world":[rifle["foregrip"].x,rifle["foregrip"].y]}},
        "equipment":{"anchor_world":[anchor.x,anchor.y],"variant":pose["variant"]},
        "body":{"pelvis_world":[root.x,root.y],"tilt_radians":tilt},
        "gait":{"phase":stride_progress,"step":"left_stance" if stance_left else "right_stance",
                "ankle_left":[(leg_left["wrist"] as Vector2).x,(leg_left["wrist"] as Vector2).y],
                "ankle_right":[(leg_right["wrist"] as Vector2).x,(leg_right["wrist"] as Vector2).y],
                "knee_left":[(leg_left["elbow"] as Vector2).x,(leg_left["elbow"] as Vector2).y],
                "knee_right":[(leg_right["elbow"] as Vector2).x,(leg_right["elbow"] as Vector2).y],
                "hip_left":[hip_left.x,hip_left.y],"hip_right":[hip_right.x,hip_right.y],
                "foot_angle_left":angle_left,"foot_angle_right":angle_right,
                "ik_error_left":leg_left["target_error"],"ik_error_right":leg_right["target_error"]}})

func segment(a:Vector2,b:Vector2,color:Color,width:float)->void:
    draw_line(a,b,color,width,true)

func limb(a:Vector2,b:Vector2,width:float,fill:Color)->void:
    draw_line(a,b,Color("28302f"),width+3.0,true)
    draw_line(a,b,fill,width,true)
    draw_circle(a,width*0.5,fill)
    draw_circle(b,width*0.5,fill)

func polygon(points:Array,fill:Color,border:Color)->void:
    var coords:PackedVector2Array=PackedVector2Array(points)
    draw_colored_polygon(coords,fill)
    var loop:PackedVector2Array=PackedVector2Array(points)
    loop.push_back(points[0])
    draw_polyline(loop,border,1.6,true)

func _draw()->void:
    if pose.is_empty():return
    for y in range(40,560,40):
        segment(Vector2(22.0,float(y)),Vector2(695.0,float(y)),Color("293848"),1.0)
    segment(Vector2(22.0,GROUND),Vector2(695.0,GROUND),Color("59717b"),2.0)
    var hip:Vector2=pose["root"]
    var shoulder_near:Vector2=pose["shoulder_near"]
    var shoulder_far:Vector2=pose["shoulder_far"]
    var left:Dictionary=pose["leg_left"]
    var right:Dictionary=pose["leg_right"]
    # PC57D: anatomical forward knees and stance heel lock are independently measured.
    for q in [right,left]:
        var near:bool=(q==right)
        var clr:Color=Color("687462") if near else Color("4b5954")
        var origin:Vector2=pose["hip_right"] if near else pose["hip_left"]
        limb(origin,q["elbow"],18.0,clr)
        draw_circle(q["elbow"],10.0,Color("485248") if near else Color("384842"))
        limb(q["elbow"],q["wrist"],15.0,Color("58675c") if near else Color("414c49"))
        var foot:Vector2=q["wrist"]
        var foot_pitch:float=pose["angle_right"] if near else pose["angle_left"]
        polygon([foot+Vector2(-12.0,-4.0).rotated(foot_pitch),
            foot+Vector2(11.0,-4.0).rotated(foot_pitch),
            foot+Vector2(23.0,3.0).rotated(foot_pitch),
            foot+Vector2(25.0,8.0).rotated(foot_pitch),
            foot+Vector2(-13.0,8.0).rotated(foot_pitch)],
            Color("534c3b") if near else Color("393f3b"),Color("9a9585"))
    # Far arm sleeve is occluded by body and rifle rather than drawn over it.
    var support:Dictionary=pose["support"]
    limb(shoulder_far,support["elbow"],17.0,Color("555d54"))
    draw_circle(support["elbow"],8.0,Color("454e48"))
    limb(support["elbow"],support["wrist"],14.0,Color("59675e"))
    var anchor:Vector2=pose["anchor"]
    var bag_size:Vector2=Vector2(35.0,64.0) if pose["variant"]==0 else Vector2(48.0,90.0)
    var bag_origin:Vector2=anchor+Vector2(-bag_size.x*0.85,-bag_size.y*0.48)
    draw_rect(Rect2(bag_origin,bag_size),Color("37423b"),true)
    draw_rect(Rect2(bag_origin+Vector2(3.0,3.0),bag_size-Vector2(6.0,6.0)),
        Color("68705b") if pose["variant"]==0 else Color("726e57"),true)
    draw_rect(Rect2(bag_origin+Vector2(5.0,bag_size.y*0.6),Vector2(bag_size.x-10.0,16.0)),Color("525c49"),true)
    segment(bag_origin+Vector2(6.0,9.0),bag_origin+Vector2(bag_size.x-6.0,9.0),Color("b0a285"),3.0)
    # Full torso, waist and belt silhouettes replace the stick-like centerline.
    polygon([hip+Vector2(-22.0,-7.0),hip+Vector2(21.0,-9.0),
        hip+Vector2(24.0,10.0),hip+Vector2(-22.0,10.0)],Color("444a40"),Color("262c2b"))
    polygon([shoulder_near+Vector2(-20.0,-10.0),shoulder_near+Vector2(15.0,-8.0),
        hip+Vector2(22.0,-25.0),hip+Vector2(16.0,-10.0),
        hip+Vector2(-18.0,-10.0),hip+Vector2(-23.0,-38.0)],Color("707963"),Color("313b35"))
    polygon([shoulder_near+Vector2(-13.0,4.0),shoulder_near+Vector2(10.0,4.0),
        hip+Vector2(14.0,-28.0),hip+Vector2(-13.0,-26.0)],Color("596255"),Color("303832"))
    segment(shoulder_near+Vector2(-11.0,0.0),hip+Vector2(11.0,-29.0),Color("a69a78"),4.0)
    draw_rect(Rect2(hip+Vector2(3.0,-63.0),Vector2(13.0,14.0)),Color("434a3c"),true)
    draw_rect(Rect2(hip+Vector2(-16.0,-42.0),Vector2(12.0,12.0)),Color("454e40"),true)
    segment(hip+Vector2(-20.0,-11.0),hip+Vector2(23.0,-11.0),Color("9f916e"),5.0)
    # Neck, head, hair, cap and mask all remain proportionate to shoulder/hip.
    var neck:Vector2=shoulder_near+Vector2(2.0,-12.0)
    limb(neck,neck+Vector2(1.0,-11.0),12.0,Color("c1aa90"))
    var head:Vector2=neck+Vector2(3.0,-24.0)
    draw_circle(head,17.0,Color("b69b7e"))
    polygon([head+Vector2(-16.0,-8.0),head+Vector2(-13.0,-16.0),
        head+Vector2(4.0,-20.0),head+Vector2(16.0,-15.0),
        head+Vector2(18.0,-7.0),head+Vector2(-12.0,-5.0)],Color("343a36"),Color("2b302c"))
    polygon([head+Vector2(-2.0,4.0),head+Vector2(18.0,-2.0),
        head+Vector2(20.0,10.0),head+Vector2(3.0,16.0)],Color("42473d"),Color("2f3531"))
    draw_circle(head+Vector2(9.0,0.0),1.7,Color("d7cfb0"))
    # Original weapon model proxy: receiver, stock, barrel and magazine.
    var rifle:Dictionary=pose["rifle"]
    segment(rifle["stock"],rifle["muzzle"],Color("282f30"),9.0)
    segment(rifle["stock"]+Vector2(15.0,0.0),rifle["foregrip"]+Vector2(9.0,-1.0),Color("666b62"),4.5)
    segment(rifle["foregrip"]+Vector2(15.0,0.0),rifle["muzzle"],Color("454d4c"),5.0)
    draw_rect(Rect2(rifle["trigger"]+Vector2(-15.0,-8.0),Vector2(28.0,16.0)),Color("343b38"),true)
    draw_rect(Rect2(rifle["trigger"]+Vector2(-2.0,8.0),Vector2(10.0,20.0)),Color("383934"),true)
    segment(rifle["trigger"]+Vector2(-8.0,-12.0),rifle["trigger"]+Vector2(4.0,-12.0),Color("a4a596"),4.0)
    # Foreground shoulder/elbow/glove assembly.
    var dominant:Dictionary=pose["dominant"]
    limb(shoulder_near,dominant["elbow"],19.0,Color("797f6c"))
    draw_circle(dominant["elbow"],9.0,Color("4f5a4b"))
    limb(dominant["elbow"],dominant["wrist"],15.0,Color("687460"))
    draw_circle(dominant["wrist"],7.0,Color("303a34"))
    draw_circle(support["wrist"],6.0,Color("333a35"))
    if OS.get_environment("PC57B_DEBUG_JOINTS")=="1":
        for point in [dominant["wrist"],support["wrist"],left["elbow"],right["elbow"]]:
            draw_circle(point,2.0,Color("ffeb93"))

func _capture()->void:
    var folder:String=OS.get_environment("PC57B_CAPTURE_DIR")
    if folder.is_empty():folder="/tmp/pc57b-evidence"
    DirAccess.make_dir_recursive_absolute(folder)
    for i in range(N):
        _pose(i)
        queue_redraw()
        await RenderingServer.frame_post_draw
        var image:Image=get_viewport().get_texture().get_image()
        var err:Error=image.save_png(folder.path_join("frame_%03d.png"%i))
        if err!=OK:
            push_error("PC57B_FRAME_SAVE_FAILED "+str(err))
            get_tree().quit(83)
            return
    var file:FileAccess=FileAccess.open(folder.path_join("frames.json"),FileAccess.WRITE)
    if file==null:
        push_error("PC57B_EVIDENCE_WRITE_FAILED")
        get_tree().quit(85)
        return
    file.store_string(JSON.stringify({"frames":evidence,"type":"original Godot mechanical QA"}))
    file.close()
    print("PC57B_NATIVE_CAPTURE_PASS frames=%d"%N)
    get_tree().quit()
