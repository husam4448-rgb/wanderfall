extends Node2D
## PC49 original HUMAN engineering diagnostic; NOT production art.
## Godot-y-down coordinates, 2-bone geometric IK with continuity branch.
const AIM_DEGREES := [-20.0, 0.0, 20.0]
const ROOT := Vector2(0, 0)
const HIP := Vector2(0, 0)
const CHEST := Vector2(0, -66)
const NEAR_SHOULDER := Vector2(9, -76)
const FAR_SHOULDER := Vector2(-7, -73)
const UPPER := 32.0
const LOWER := 31.0
const RIFLE_PIVOT := Vector2(28, -81)
const DOMINANT_GRIP := Vector2(19, -74)
const SUPPORT_GRIP := Vector2(57, -80)
const THIGH := 40.0
const SHIN := 40.0
var elevation := 0.0
var walk_phase := 0.0
var mirrored := false
var visual_zoom := 2.4
var shoulder_delta := 0.0
var error_max := 0.0
var frame_failures := 0
var frames := 0
func _ready() -> void:
    get_viewport().transparent_bg = false
    for side in [false, true]:
        mirrored = side
        for degrees in AIM_DEGREES:
            elevation = degrees
            walk_phase = 0.0
            if not await capture("aim_%s_%s" % ["left" if side else "right", str(int(degrees)).replace("-", "m")]):
                get_tree().quit(71)
                return
        for index in range(16):
            elevation = 0.0
            walk_phase = TAU * float(index) / 16.0
            if not await capture("walk_%s_%02d" % ["left" if side else "right",index]):
                get_tree().quit(72)
                return
    print("PC49_HUMAN_ENGINEERING_CAPTURED frames=%d max_grip_error=%.4f failures=%d VISUAL_QA_PENDING" % [frames,error_max,frame_failures])
    get_tree().quit(0 if frame_failures == 0 else 73)

func solve_two_bone(a:Vector2, b:Vector2, l1:float, l2:float, downward:bool) -> Dictionary:
    var delta := b - a
    var distance := delta.length()
    if distance > l1+l2-0.001 or distance < absf(l1-l2)+0.001:
        return {"valid":false,"elbow":Vector2.ZERO,"wrist":Vector2.ZERO}
    var d := delta / distance
    var projection := (l1*l1 + distance*distance - l2*l2) / (2.0*distance)
    var rise := sqrt(maxf(0.0,l1*l1-projection*projection))
    var perpendicular := Vector2(-d.y,d.x)
    var elbow := a + d*projection + perpendicular*rise*(1.0 if downward else -1.0)
    return {"valid":true,"elbow":elbow,"wrist":b}

func rifle_socket(offset:Vector2)->Vector2:
    return RIFLE_PIVOT + (offset-RIFLE_PIVOT).rotated(deg_to_rad(elevation))

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO,Vector2(1580,660)),Color(0.1,0.12,0.15))
    draw_set_transform(Vector2(790,355),0.0,Vector2(visual_zoom * (-1.0 if mirrored else 1.0),visual_zoom))
    # Legs use independent, complete symmetric stride cycles with IK endpoints.
    for i in range(2):
        var sign := 1.0 if i == 0 else -1.0
        var stride := sin(walk_phase + (0.0 if i == 0 else PI))
        var lift := maxf(0.0,cos(walk_phase + (0.0 if i == 0 else PI)))*10.0
        var hip := Vector2(sign*7,0)
        var foot := Vector2(sign*7 + stride*15.0,78.0-lift)
        var leg := solve_two_bone(hip,foot,THIGH,SHIN,false if i==0 else true)
        if bool(leg["valid"]):
            line_segment(hip,leg["elbow"],Color(0.35,0.43,0.48),11)
            line_segment(leg["elbow"],foot,Color(0.31,0.33,0.35),9)
            draw_circle(leg["elbow"],7,Color(0.24,0.29,0.33))
            line_segment(foot,foot+Vector2(17,0),Color(0.22,0.20,0.18),8)
    draw_circle(Vector2.ZERO,15,Color(0.36,0.36,0.31))
    line_segment(Vector2(0,-5),CHEST,Color(0.36,0.42,0.37),35)
    draw_circle(CHEST,19,Color(0.37,0.43,0.37))
    line_segment(Vector2(0,-63),Vector2(0,-89),Color(0.61,0.51,0.4),9)
    draw_circle(Vector2(0,-105),17,Color(0.7,0.57,0.46))
    var dominant := rifle_socket(DOMINANT_GRIP)
    var support := rifle_socket(SUPPORT_GRIP)
    # Forearm driven to grip by two-bone solver (hands are NOT parented to rifle).
    var far := solve_two_bone(FAR_SHOULDER,support,UPPER,LOWER,true)
    var near := solve_two_bone(NEAR_SHOULDER,dominant,UPPER,LOWER,false)
    if bool(far["valid"]):
        line_segment(FAR_SHOULDER,far["elbow"],Color(0.24,0.34,0.30),15)
        line_segment(far["elbow"],support,Color(0.28,0.39,0.34),13)
        draw_circle(far["elbow"],7,Color(0.27,0.37,0.33))
        draw_circle(support,7,Color(0.69,0.51,0.37))
    var muzzle := rifle_socket(Vector2(91,-79))
    var stock := rifle_socket(Vector2(10,-79))
    line_segment(stock,muzzle,Color(0.13,0.15,0.16),8)
    draw_circle(RIFLE_PIVOT,5,Color(0.63,0.57,0.31))
    if bool(near["valid"]):
        line_segment(NEAR_SHOULDER,near["elbow"],Color(0.43,0.48,0.37),15)
        line_segment(near["elbow"],dominant,Color(0.41,0.46,0.36),13)
        draw_circle(near["elbow"],7,Color(0.40,0.45,0.35))
        draw_circle(dominant,7,Color(0.78,0.58,0.42))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func line_segment(a:Vector2,b:Vector2,c:Color,width:float)->void:
    draw_line(a,b,c,width,true)

func capture(label:String)->bool:
    var dominant := rifle_socket(DOMINANT_GRIP)
    var support := rifle_socket(SUPPORT_GRIP)
    var n := solve_two_bone(NEAR_SHOULDER,dominant,UPPER,LOWER,false)
    var f := solve_two_bone(FAR_SHOULDER,support,UPPER,LOWER,true)
    if not bool(n["valid"]) or not bool(f["valid"]):
        frame_failures += 1
        print("PC49_INVALID_IK label=%s near=%s far=%s" % [label,n["valid"],f["valid"]])
        return false
    var err := maxf((n["wrist"] as Vector2).distance_to(dominant),(f["wrist"] as Vector2).distance_to(support))
    error_max = maxf(error_max,err)
    if err > 0.05:
        frame_failures += 1
        return false
    queue_redraw()
    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var filename := "res://evidence/pc49_%s.png" % label
    var path := ProjectSettings.globalize_path(filename)
    var rc := get_viewport().get_texture().get_image().save_png(path)
    if rc != OK:
        push_error("PC49_PNG_SAVE_FAILED "+str(rc))
        return false
    frames += 1
    print("PC49_FRAME %s grip_error_px=%.4f" % [label,err])
    return true
