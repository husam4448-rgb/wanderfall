extends RefCounted
## v268 older-Android art draw path. The v267 approved sprites are consolidated
## into seven alpha atlases; max six additional draw calls in each streamed chunk.
## Exactly cosmetic: does not touch collision, object persistence, loot or AI.
const ROOT: String = "res://assets/world/props_v267/"
const CELL: int = 128
const COUNTS := {"nature":30,"urban":24,"ruins":24,"camp":18,
                 "wreck":16,"rock":4,"deadwood":4}
const COLS := {"nature":6,"urban":6,"ruins":6,"camp":6,
               "wreck":4,"rock":2,"deadwood":2}
const POOLS := [
    ["nature","nature","nature","rock","deadwood"],
    ["nature","nature","rock","deadwood"],
    ["nature","nature","nature","rock"],
    ["nature","deadwood","rock"],
    ["rock","rock","deadwood","nature","ruins"],
    ["rock","rock","deadwood","ruins"],
    ["rock","deadwood","camp"],
    ["nature","rock","deadwood"],
    ["urban","ruins","urban","wreck","ruins","camp"]
]
static var _atlases: Dictionary = {}

static func _atlas(family: String) -> Texture2D:
    if not _atlases.has(family):
        var path: String = ROOT + family + "_atlas.png"
        _atlases[family] = load(path) if ResourceLoader.exists(path) else null
    return _atlases[family] as Texture2D

static func _draw_extent(family: String) -> float:
    match family:
        "nature": return 47.0
        "rock": return 54.0
        "deadwood": return 59.0
        "ruins": return 68.0
        "urban": return 53.0
        "wreck": return 90.0
        "camp": return 49.0
    return 50.0

static func paint_props(canvas: CanvasItem, biome_id: int,
        coord: Vector2i, seed: int, chunk_size: float,
        buildings: Array) -> void:
    if biome_id < 0 or biome_id >= POOLS.size():
        return
    var pool: Array = POOLS[biome_id]
    var rng := RandomNumberGenerator.new()
    rng.seed = int(abs(coord.x * 73856093 + coord.y * 19349663 + seed * 9719 + 268321))
    # 3x2 deterministic positions, not 5x4. The pre-existing v265/2658
    # nature/clutter remains active. Small extra prop budget avoids overdraw.
    for i in range(6):
        if coord.length_squared() <= 2 and i >= 3:
            break # protect the dense starting camp from extra visual noise
        var col: int = i % 3
        var row: int = int(i / 3)
        var px: float = (float(col) + rng.randf_range(0.34, 0.66)) * chunk_size / 3.0
        var py: float = (float(row) + rng.randf_range(0.32, 0.68)) * chunk_size / 2.0
        var point := Vector2(px, py)
        # Existing central roads, settlement buildings and player corridor
        # must remain clearly readable. No huge overlapping sprite panels.
        if absf(px - chunk_size * 0.5) < 66.0 or absf(py - chunk_size * 0.5) < 46.0:
            continue
        var blocked: bool = false
        for b in buildings:
            if b is Rect2 and (b as Rect2).grow(76.0).has_point(point):
                blocked = true
                break
        if blocked:
            continue
        var family: String = pool[rng.randi_range(0, pool.size()-1)]
        var index: int = rng.randi_range(0, int(COUNTS[family])-1)
        var texture: Texture2D = _atlas(family)
        if texture == null:
            continue
        var size: float = _draw_extent(family) * rng.randf_range(0.83, 1.11)
        var dest := Rect2(point - Vector2.ONE * size * 0.5, Vector2.ONE * size)
        var src := Rect2(
            float((index % int(COLS[family])) * CELL),
            float((int(index / int(COLS[family]))) * CELL),
            float(CELL), float(CELL))
        canvas.draw_texture_rect_region(texture, dest, src)
