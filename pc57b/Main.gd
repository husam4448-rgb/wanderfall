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
    var root:Vector2=Vector2(295.0+1.8*f,359.0-1.5*sin(f*TAU/16.0))
    var tilt:float=deg_to_rad(2.0)*sin(f*TAU/16.0)
    var shoulder_near:Vector2=root+Vector2(3.0,-88.0).rotated(tilt)
    var shoulder_far:Vector2=root+Vector2(-9.0,-92.0).rotated(tilt)
    var pivot:Vector2=root+Vector2(37.0,-58.0)+Vector2(0.0,1.4*sin(f*TAU/16.0+0.3))
    var rifle:Dictionary=IK.sockets(pivot,deg_to_rad(-4.0+1.5*sin(f*TAU/32.0)))
    var dominant:Dictionary=IK.solve(shoulder_near,rifle["trigger"],47.0,44.0,1.0)
    var support:Dictionary=IK.solve(shoulder_far,rifle["foregrip"],63.0,58.0,1.0)
    var stance_left:bool=i<16
    var foot_left:Vector2
    var foot_right:Vector2
    if stance_left:
        foot_left=Vector2(282.0,GROUND)
        foot_right=swing(Vector2(272.0,GROUND),Vector2(334.0,GROUND),f/15.0)
    else:
        foot_left=swing(Vector2(282.0,GROUND),Vector2(369.0,GROUND),(f-16.0)/15.0)
        foot_right=Vector2(334.0,GROUND)
    var hip_left:Vector2=root+Vector2(-15.0,6.0)
    var hip_right:Vector2=root+Vector2(14.0,6.0)
    var leg_left:Dictionary=IK.solve(hip_left,foot_left,75.0,76.0,1.0)
    var leg_right:Dictionary=IK.solve(hip_right,foot_right,76.0,76.0,1.0)
    if not dominant["valid"] or not support["valid"] or not leg_left["valid"] or not leg_right["valid"]:
        push_error("PC57B_INVALID_IK")
        get_tree().quit(82)
        return
    if not dominant["reachable"] or not support["reachable"]:
        push_error("PC57B_UNREACHABLE_RIFLE_GRIP")
        get_tree().quit(84)
        return
    var anchor:Vector2=IK.equipment_anchor(root,tilt)
    pose={"root":root,"shoulder_near":shoulder_near,"shoulder_far":shoulder_far,
        "rifle":rifle,"dominant":dominant,"support":support,
        "hip_left":hip_left,"hip_right":hip_right,
        "leg_left":leg_left,"leg_right":leg_right,
        "anchor":anchor,"variant":0 if i<16 else 1}
    evidence.append({"time_seconds":f/30.0,
        "feet":{"left":{"heel_world":[foot_left.x,foot_left.y],"stance":stance_left},
                "right":{"heel_world":[foot_right.x,foot_right.y],"stance":not stance_left}},
        "hands":{"dominant":{"actual_world":[dominant["wrist"].x,dominant["wrist"].y],
                              "grip_world":[rifle["trigger"].x,rifle["trigger"].y]},
                 "support":{"actual_world":[support["wrist"].x,support["wrist"].y],
                            "grip_world":[rifle["foregrip"].x,rifle["foregrip"].y]}},
        "equipment":{"anchor_world":[anchor.x,anchor.y],"variant":pose["variant"]}})

func segment(a:Vector2,b:Vector2,color:Color,width:float)->void:
    draw_line(a,b,color,width,true)

func _draw()->void:
    if pose.is_empty():return
    for y in range(40,560,40):
        segment(Vector2(22.0,float(y)),Vector2(695.0,float(y)),Color("293848"),1.0)
    segment(Vector2(22.0,GROUND),Vector2(695.0,GROUND),Color("59717b"),2.0)
    var left:Dictionary=pose["leg_left"]
    var right:Dictionary=pose["leg_right"]
    for q in [right,left]:
        var color:Color=Color("d9b070") if q==right else Color("71c3cd")
        var hip:Vector2=pose["hip_right"] if q==right else pose["hip_left"]
        segment(hip,q["elbow"],color,12.0)
        segment(q["elbow"],q["wrist"],color,11.0)
        draw_circle(q["elbow"],5.0,color)
        segment(q["wrist"]+Vector2(-12.0,0.0),q["wrist"]+Vector2(17.0,0.0),Color("b3c0b9"),8.0)
    segment(pose["root"],pose["shoulder_near"],Color("bec6cc"),23.0)
    draw_circle(pose["shoulder_near"]+Vector2(0.0,-23.0),14.0,Color("bec6cc"))
    var anchor:Vector2=pose["anchor"]
    if pose["variant"]==0:
        draw_rect(Rect2(anchor+Vector2(-17.0,-23.0),Vector2(26.0,49.0)),Color("657359"),true)
    else:
        draw_rect(Rect2(anchor+Vector2(-24.0,-36.0),Vector2(33.0,67.0)),Color("74806b"),true)
        segment(anchor+Vector2(-21.0,-12.0),anchor+Vector2(5.0,-12.0),Color("b4a78b"),4.0)
    draw_circle(anchor,3.0,Color("eddaa2"))
    var support:Dictionary=pose["support"]
    segment(pose["shoulder_far"],support["elbow"],Color("a58abb"),10.0)
    segment(support["elbow"],support["wrist"],Color("a58abb"),9.0)
    var rifle:Dictionary=pose["rifle"]
    segment(rifle["stock"],rifle["muzzle"],Color("e17c76"),9.0)
    draw_circle(rifle["trigger"],5.0,Color("fff2ae"))
    draw_circle(rifle["foregrip"],5.0,Color("8ce5b8"))
    var dominant:Dictionary=pose["dominant"]
    segment(pose["shoulder_near"],dominant["elbow"],Color("84c9a4"),11.0)
    segment(dominant["elbow"],dominant["wrist"],Color("84c9a4"),10.0)
    draw_circle(dominant["wrist"],6.0,Color("d9eddb"))
    draw_circle(support["wrist"],5.0,Color("d8bde7"))

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
