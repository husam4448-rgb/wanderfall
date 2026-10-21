extends Node2D
## Path-only exits. Guide the survivor from local terrain into adjacent region.
var region:Vector2i=Vector2i.ZERO
var chunk_size:int=768
const SIDE:int=2
const WIDTH:float=140.0
const PATH_LENGTH:float=155.0

func _ready()->void:
    name="RegionalPathGates"
    z_index=26

func set_region(value:Vector2i,size:int)->void:
    region=value
    chunk_size=size
    queue_redraw()

func _draw()->void:
    var rect:=Rect2(Vector2(region*SIDE)*float(chunk_size),Vector2.ONE*float(SIDE*chunk_size))
    var c:Vector2=rect.get_center()
    var entries: Array[Vector2]=[
        Vector2(c.x,rect.position.y+1.0),Vector2(rect.end.x-1.0,c.y),
        Vector2(c.x,rect.end.y-1.0),Vector2(rect.position.x+1.0,c.y)]
    var inside: Array[Vector2]=[Vector2.DOWN,Vector2.LEFT,Vector2.UP,Vector2.RIGHT]
    for i in range(entries.size()):
        var end:Vector2=entries[i]
        var delta:Vector2=inside[i]
        var start:Vector2=end+delta*PATH_LENGTH
        var sideways:Vector2=Vector2(-delta.y,delta.x)
        var pale:=Color(0.42,0.38,0.31,0.76)
        draw_line(end,start,pale,WIDTH,false)
        draw_line(end+sideways*WIDTH*0.45,start+sideways*WIDTH*0.45,Color(0.18,0.25,0.15,0.72),3.0)
        draw_line(end-sideways*WIDTH*0.45,start-sideways*WIDTH*0.45,Color(0.18,0.25,0.15,0.72),3.0)
        var tip:Vector2=end+delta*12.0
        var basis:Vector2=end+delta*47.0
        draw_colored_polygon(PackedVector2Array([
            tip,basis+sideways*16.0,basis-sideways*16.0]),
            Color(0.88,0.78,0.44,0.91))
