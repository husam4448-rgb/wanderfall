extends RefCounted
## v267 actually paints extracted, transparent Batch03 art into LIVE streamed
## world chunks. Cosmetic-only placement: no fabricated collision, loot or doors.
const ROOT: String = "res://assets/world/props_v267/"
const COUNTS := {"nature":30,"urban":24,"ruins":24,"camp":18,
                 "wreck":16,"rock":4,"deadwood":4}
const POOLS := [
    ["nature","nature","nature","rock","deadwood"], # temperate
    ["nature","nature","rock","deadwood","deadwood"], # deep forest
    ["nature","nature","nature","rock"], # grassland
    ["nature","nature","deadwood","rock"], # wetland
    ["rock","rock","deadwood","nature","ruins"], # wasteland
    ["rock","rock","deadwood","ruins"], # rock highlands
    ["rock","deadwood","camp"], # snow
    ["nature","rock","deadwood","camp"], # rivers/coasts
    ["urban","ruins","urban","wreck","ruins","camp"] # ruined city
]
static var _cache: Dictionary = {}

static func _load_art(family: String,index: int) -> Texture2D:
    var key: String = family + "/" + family + "_%02d.png" % index
    if not _cache.has(key):
        var path: String = ROOT + key
        _cache[key] = load(path) if ResourceLoader.exists(path) else null
    return _cache[key] as Texture2D

static func _size_for(family: String) -> float:
    match family:
        "nature": return 105.0
        "rock": return 96.0
        "deadwood": return 110.0
        "ruins": return 145.0
        "urban": return 115.0
        "wreck": return 152.0
        "camp": return 97.0
    return 102.0

static func paint_props(canvas: CanvasItem, biome_id: int,
        coord: Vector2i, seed: int, chunk_size: float,
        buildings: Array) -> void:
    if biome_id<0 or biome_id>=POOLS.size():
        return
    var pool: Array=POOLS[biome_id]
    var rng:=RandomNumberGenerator.new()
    rng.seed=int(abs(coord.x*73856093+coord.y*19349663+seed*9719+267321))
    # Balanced 5 x 4 per-chunk occupancy, no uncontrolled per-frame spawn.
    # Constant density lets Android render consistently while streaming.
    for i in range(20):
        var col: int=i%5
        var row: int=int(i/5)
        var px: float=(float(col)+rng.randf_range(0.20,0.80))*chunk_size/5.0
        var py: float=(float(row)+rng.randf_range(0.20,0.80))*chunk_size/4.0
        var point:=Vector2(px,py)
        # Preserve central travel corridor and existing player-safe camp.
        if absf(px-chunk_size*0.5)<52.0 or absf(py-chunk_size*0.5)<52.0:
            continue
        var blocked: bool=false
        for b in buildings:
            if b is Rect2 and (b as Rect2).grow(60.0).has_point(point):
                blocked=true
                break
        if blocked:
            continue
        var family: String=pool[rng.randi_range(0,pool.size()-1)]
        var index: int=rng.randi_range(0,int(COUNTS[family])-1)
        var tex: Texture2D=_load_art(family,index)
        if tex==null:
            continue
        var scale: float=rng.randf_range(0.79,1.19)
        var max_extent: float=_size_for(family)*scale
        var original_size: Vector2=tex.get_size()
        var scaled: Vector2=original_size*(max_extent/maxf(original_size.x,original_size.y))
        var where:=Rect2(point-scaled*0.5,scaled)
        canvas.draw_texture_rect(tex,where,false)
