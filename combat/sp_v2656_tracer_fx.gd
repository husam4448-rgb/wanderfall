extends Node2D
## SP-v265.6: brief visual-only hitscan tracers, never real lasers.
## Uses the original shot's selected hit target/range; no second damage query.
## Reusable CanvasItem: no projectile node spawning or particle allocations.
const MAX_STREAKS: int = 6
var streaks: Array[Dictionary] = []

static func profile(weapon: String, ammo: String) -> Dictionary:
    if weapon.contains("shotgun") or ammo.contains("12g"):
        return {"life":0.120,"width":1.35,"color":Color("#f8aa69"),"count":4,"flash":1.2}
    if weapon.contains("revolver") or ammo.contains("357"):
        return {"life":0.105,"width":1.75,"color":Color("#ffce79"),"count":1,"flash":1.15}
    if weapon.contains("hunting") or ammo.contains("762"):
        return {"life":0.082,"width":1.18,"color":Color("#ffead5"),"count":1,"flash":1.05}
    if weapon.contains("rifle") or ammo.contains("556"):
        return {"life":0.070,"width":0.94,"color":Color("#ffe5a2"),"count":1,"flash":0.95}
    if weapon.contains("smg"):
        return {"life":0.066,"width":0.86,"color":Color("#f9c66e"),"count":1,"flash":0.67}
    return {"life":0.085,"width":0.99,"color":Color("#ffcb71"),"count":1,"flash":0.90}

func _ready() -> void:
    top_level = true
    z_index = 75
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    set_process(false)

func fire_visual(muzzle_world: Vector2, end_world: Vector2,
        weapon: String, ammo: String, suppressed: bool = false,
        reduced_flash: bool = false, density: float = 1.0) -> void:
    if density < 0.32:
        return
    var diff: Vector2 = end_world-muzzle_world
    if diff.length_squared() < 16.0:
        return
    # This is a tracer indicator, not continuous weapon light or hit detection.
    var spec: Dictionary = profile(weapon,ammo)
    if suppressed:
        spec["flash"] = 0.18
    if reduced_flash:
        spec["flash"] = 0.0
    var duration: float = float(spec["life"])
    streaks.append({
        "a": muzzle_world,
        "b": end_world,
        "t": duration,
        "life": duration,
        "width": float(spec["width"]),
        "color": spec["color"],
        "count": int(spec["count"]),
        "flash": float(spec["flash"])
    })
    if streaks.size()>MAX_STREAKS:
        streaks.remove_at(0)
    set_process(true)
    queue_redraw()

func _process(delta: float) -> void:
    for i in range(streaks.size()-1,-1,-1):
        streaks[i]["t"]=float(streaks[i]["t"])-delta
        if float(streaks[i]["t"])<=0.0:
            streaks.remove_at(i)
    if streaks.is_empty():
        set_process(false)
    queue_redraw()

func _draw() -> void:
    for shot in streaks:
        var time_left: float = float(shot["t"])
        var life: float = float(shot["life"])
        var ratio: float = clampf(time_left/life,0.0,1.0)
        var a: Vector2 = shot["a"]
        var b: Vector2 = shot["b"]
        var path: Vector2 = b-a
        var length: float = path.length()
        if length < 4.0: continue
        var dir: Vector2 = path/length
        var side: Vector2 = dir.orthogonal()
        var shade: Color = shot["color"]
        var width: float = float(shot["width"])
        var pellets: int = int(shot["count"])
        # The entire path is faintly visible for only ~0.07–0.12 s.
        # The bright core travels during that interval instead of a static beam.
        for k in range(pellets):
            var offset: float = float(k)-float(pellets-1)*0.5
            var deviation: Vector2 = side*offset*(2.1 if pellets>1 else 0.0)
            var end_point: Vector2 = b+deviation*(length/260.0)
            draw_line(a,end_point,Color(shade.r,shade.g,shade.b,0.16*ratio),
                width+1.1,true)
            var head: float = 1.0-ratio
            var front: float = clampf(head+0.22,0.0,1.0)
            var rear: float = maxf(0.0,front-0.23)
            var core_a: Vector2 = a.lerp(end_point,rear)
            var core_b: Vector2 = a.lerp(end_point,front)
            draw_line(core_a,core_b,
                Color(shade.r,shade.g,shade.b,0.68*ratio),width,true)
            draw_line(core_a.lerp(core_b,0.38),core_b,
                Color(1.0,0.96,0.78,0.88*ratio),0.65,true)
        # Existing firearm art owns the true muzzle flash shape.
        # Small secondary spike exists ONLY for NPCs or non-weapon renderers.
        # No circular legacy muzzle flash and no large orange glow.
        if float(shot["flash"])>0.0:
            var reach: float = (6.0+float(shot["flash"])*4.0)*ratio
            if reach > 0.5:
                var tip: Vector2 = a+dir*reach
                draw_colored_polygon(PackedVector2Array([
                    a-side*1.1, a+side*1.1, tip]),
                    Color(1.0,0.88,0.52,0.66*ratio))
