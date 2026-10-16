extends Node2D
## PC62: ONE original artwork part. Independently authored 10x6 weighted grid.
## PRIVATE real B2B source mesh tested separately; NONE of its original UVs,
## triangles, source pixels or per-vertex bone weights are in this project.
const TX:Texture2D=preload("res://assets/SP_PC62_MaleRight_L_leg01_PROTOTYPE.png")
const W:int=49
const H:int=68
const NX:int=10
const NY:int=6
const N:int=32
const ZOOM:float=5.0
var vertices:Array[Vector2]=[]
var triangles:Array[PackedInt32Array]=[]
var frames:Array=[]
var t:float=0.0

func _ready()->void:
    for y in range(NY):
        for x in range(NX):
            vertices.append(Vector2((float(x)/float(NX-1))*float(W-1),
                (float(y)/float(NY-1))*float(H-1)))
    for y in range(NY-1):
        for x in range(NX-1):
            var a:int=y*NX+x
            triangles.append(PackedInt32Array([a,a+1,a+NX]))
            triangles.append(PackedInt32Array([a+1,a+NX+1,a+NX]))
    if triangles.size()!=90 or vertices.size()!=60:
        push_error("PC62_BAD_GRID")
        get_tree().quit(84)
        return
    if OS.get_environment("PC62_CAPTURE")=="1":
        call_deferred("_capture")
    else:
        queue_redraw()

func _deform(phase:float)->Array[Vector2]:
    var hip_angle:float=deg_to_rad(32.0*sin(phase))
    var knee_angle:float=deg_to_rad(38.0*(0.5+0.5*sin(phase+0.35)))
    var hip:Vector2=Vector2(0.0,0.0)
    var hinge:Vector2=Vector2(0.0,51.0)
    var output:Array[Vector2]=[]
    for v in vertices:
        var source:Vector2=v-Vector2(24.0,0.0)
        var upper:Vector2=source.rotated(hip_angle)
        var knee_world:Vector2=hinge.rotated(hip_angle)
        var bottom:Vector2=knee_world+(source-hinge).rotated(hip_angle+knee_angle)
        var q:float=clampf((v.y-31.0)/31.0,0.0,1.0)
        var smooth:float=q*q*(3.0-2.0*q)
        var mix:float=upper.lerp(bottom,smooth).x
        var miy:float=upper.lerp(bottom,smooth).y
        output.append(Vector2(360.0,205.0)+Vector2(mix,miy)*ZOOM)
    return output

func _draw()->void:
    var draw_vertices:Array[Vector2]=_deform(t)
    for tri in triangles:
        var coords:=PackedVector2Array()
        var tex_coords:=PackedVector2Array()
        var colors:=PackedColorArray()
        for index in tri:
            coords.append(draw_vertices[index])
            tex_coords.append(Vector2(vertices[index].x/float(W-1), vertices[index].y/float(H-1)))
            colors.append(Color.WHITE)
        draw_polygon(coords,colors,tex_coords,TX)

func _capture()->void:
    var directory:String=OS.get_environment("PC62_CAPTURE_DIR")
    if directory.is_empty():directory="/tmp/pc62-evidence"
    DirAccess.make_dir_recursive_absolute(directory)
    for i in range(N):
        t=TAU*float(i)/float(N)
        queue_redraw()
        await RenderingServer.frame_post_draw
        var image:Image=get_viewport().get_texture().get_image()
        if image.save_png(directory.path_join("frame_%03d.png"%i))!=OK:
            push_error("PC62_PNG_SAVE_FAIL")
            get_tree().quit(87)
            return
        var v:Array[Vector2]=_deform(t)
        var data:Array=[]
        for q in v:data.append([q.x,q.y])
        frames.append({"frame":i,"time_seconds":float(i)/30.0,
            "hip_angle":32.0*sin(t),"knee_angle":38.0*(0.5+0.5*sin(t+0.35)),
            "vertices":data})
    var file:FileAccess=FileAccess.open(directory.path_join("mesh_frames.json"),FileAccess.WRITE)
    if file==null:
        push_error("PC62_JSON_SAVE_FAIL")
        get_tree().quit(88)
        return
    file.store_string(JSON.stringify({"frames":frames,"triangles":triangles,
        "source_type":"original_SP_49x68_textured_mesh", "art_verdict":"PENDING"}))
    file.close()
    print("PC62_NATIVE_GODOT_PART_SWEEP_OK poses=%d vertices=%d triangles=%d"%
        [N,vertices.size(),triangles.size()])
    get_tree().quit()
