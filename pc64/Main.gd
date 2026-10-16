extends Node2D
## PC64: original Survival Paradise RIGHT-facing trouser & boot.
## Source-free implementation. B2B informed topology: weighted continuous
## trouser textile + ONE rigid L_foot boot. No commercial vertex arrays/UVs.
const TROUSERS:Texture2D=preload("res://assets/SP_PC62_MaleRight_L_leg01_PROTOTYPE.png")
const BOOT:Texture2D=preload("res://assets/SP_PC63_MaleRight_L_leg02_BOOT.png")
const GRID_W:int=10
const GRID_H:int=6
const FRAMES:int=32
const GROUND:float=502.0
const BOOT_SCALE:float=1.02
const BOOT_PIVOT:Vector2=Vector2(22.0,21.0)
const BOOT_HEEL_PIXEL:Vector2=Vector2(18.0,52.0)
const CLOTH_WIDTH:float=1.16
var uv_points:Array[Vector2]=[]
var triangles:Array[PackedInt32Array]=[]
var pose:Dictionary={}
var records:Array=[]
var layer:String="both"

func _ready()->void:
    for y in range(GRID_H):
        for x in range(GRID_W):
            uv_points.append(Vector2(float(x)*48.0/float(GRID_W-1),
                                     float(y)*67.0/float(GRID_H-1)))
    for y in range(GRID_H-1):
        for x in range(GRID_W-1):
            var a:int=y*GRID_W+x
            triangles.append(PackedInt32Array([a,a+1,a+GRID_W]))
            triangles.append(PackedInt32Array([a+1,a+GRID_W+1,a+GRID_W]))
    if uv_points.size()!=60 or triangles.size()!=90:
        push_error("PC64_GRID_INVALID")
        get_tree().quit(71)
        return
    if OS.get_environment("PC64_CAPTURE")=="1":
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

func _pose(i:int)->void:
    var frame:float=float(i)
    var stance:bool=i<16
    var root_x:float=303.0+56.0*frame/32.0
    var hip:Vector2=Vector2(root_x,327.0-1.6*pow(sin(PI*frame/16.0),2.0))
    var boot_heel:Vector2
    var foot_pitch:float=0.0
    if stance:
        boot_heel=Vector2(345.0,GROUND)
    else:
        var swing_u:float=(frame-16.0)/16.0
        boot_heel=_swing(Vector2(345.0,GROUND),Vector2(401.0,GROUND),swing_u)
        foot_pitch=deg_to_rad(-8.0*sin(PI*swing_u))
    var ankle:Vector2=boot_heel-((BOOT_HEEL_PIXEL-BOOT_PIVOT)*BOOT_SCALE).rotated(foot_pitch)
    var ik:Dictionary=_two_bone(hip,ankle,80.0,80.0)
    if not ik["ok"]:
        push_error("PC64_UNREACHABLE_ANKLE frame="+str(i)+" dist="+str(ik["distance"]))
        get_tree().quit(72)
        return
    var knee:Vector2=ik["knee"]
    # Smooth through the actual knee pivot WITHOUT the previous piecewise
    # tangent discontinuity that folded 10 triangles during the swing.
    # A quadratic centerline still passes exactly through knee at t=0.54.
    var at_knee:float=0.54
    var other:float=1.0-at_knee
    var control:Vector2=(knee-hip*other*other-ankle*at_knee*at_knee)/(2.0*at_knee*other)
    var vtx:Array[Vector2]=[]
    for tex_coord in uv_points:
        var t:float=tex_coord.y/67.0
        var one_minus:float=1.0-t
        var center:Vector2=hip*one_minus*one_minus+control*2.0*one_minus*t+ankle*t*t
        var tangent:Vector2=(control-hip)*one_minus+(ankle-control)*t
        var direction:Vector2=tangent.normalized()
        var normal:Vector2=Vector2(direction.y,-direction.x)
        var width_offset:float=(tex_coord.x-24.0)*CLOTH_WIDTH
        vtx.append(center+normal*width_offset)
    pose={"trouser_vertices":vtx,"hip":hip,"knee":knee,
          "ankle":ankle,"boot_heel":boot_heel,"pitch":foot_pitch,
          "stance":stance,"ik":ik,"phase":i}

func _draw()->void:
    if pose.is_empty():
        return
    if layer=="both":
        draw_line(Vector2(55.0,GROUND),Vector2(810.0,GROUND),Color(0.60,0.62,0.63),2.0)
    if layer!="boot":
        var shape:Array=pose["trouser_vertices"]
        for tri in triangles:
            var positions:=PackedVector2Array()
            var tex_coords:=PackedVector2Array()
            var colors:=PackedColorArray()
            for k in tri:
                positions.append(shape[k])
                tex_coords.append(Vector2(uv_points[k].x/48.0,uv_points[k].y/67.0))
                colors.append(Color.WHITE)
            draw_polygon(positions,colors,tex_coords,TROUSERS)
    if layer!="trousers":
        draw_set_transform(pose["ankle"],pose["pitch"],Vector2(BOOT_SCALE,BOOT_SCALE))
        draw_texture(BOOT,-BOOT_PIVOT)
        draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _capture()->void:
    var folder:String=OS.get_environment("PC64_CAPTURE_DIR")
    if folder.is_empty():folder="/tmp/pc64-native"
    DirAccess.make_dir_recursive_absolute(folder)
    for i in range(FRAMES):
        _pose(i)
        layer="both"
        queue_redraw()
        await RenderingServer.frame_post_draw
        var picture:Image=get_viewport().get_texture().get_image()
        if picture.save_png(folder.path_join("frame_%03d.png"%i))!=OK:
            push_error("PC64_FRAME_SAVE_FAILURE")
            get_tree().quit(74)
            return
        var per_part:Dictionary={}
        for k in ["trousers","boot"]:
            if i%4==0:
                layer=k
                queue_redraw()
                await RenderingServer.frame_post_draw
                var separate:Image=get_viewport().get_texture().get_image()
                if separate.save_png(folder.path_join("%s_%03d.png"%[k,i]))!=OK:
                    push_error("PC64_LAYER_SAVE_FAILURE "+k)
                    get_tree().quit(75)
                    return
        var world:Array=[]
        for point in pose["trouser_vertices"]:
            world.append([point.x,point.y])
        var heel:Vector2=pose["boot_heel"]
        var hip:Vector2=pose["hip"]
        var ankle:Vector2=pose["ankle"]
        var knee:Vector2=pose["knee"]
        var ik:Dictionary=pose["ik"]
        records.append({"frame":i,"time_seconds":float(i)/30.0,
            "leg_facing":"RIGHT","stance":pose["stance"],"hip":[hip.x,hip.y],
            "knee":[knee.x,knee.y],"ankle":[ankle.x,ankle.y],
            "heel":[heel.x,heel.y],"boot_pitch":pose["pitch"],
            "forward_knee_clearance":ik["knee_forward"],
            "upper_segment_residual":ik["upper_error"],
            "lower_segment_residual":ik["lower_error"],
            "cloth_vertices":world})
    layer="both"
    var output:FileAccess=FileAccess.open(folder.path_join("pose_metrics.json"),FileAccess.WRITE)
    if output==null:
        push_error("PC64_JSON_WRITE_FAILURE")
        get_tree().quit(76)
        return
    var triangles_serialized:Array=[]
    for tri in triangles:triangles_serialized.append(Array(tri))
    output.store_string(JSON.stringify({"frames":records,"triangles":triangles_serialized,
        "source":"Original SP trouser and boot images; new Godot deformable grid.",
        "commercial_reference_geometry_included":false,
        "visual_status":"PENDING"}))
    output.close()
    print("PC64_GODOT_ORIGINAL_PAIR_CAPTURED frames=32 cloth_vertices=60 tris=90 boot=rigid")
    get_tree().quit()
