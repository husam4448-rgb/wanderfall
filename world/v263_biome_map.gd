extends RefCounted
## SP v263: deterministic finite world with ALL biomes guaranteed per seed.
## Independent of chunk loading order and frame rate. One seed = one coherent
## geography; only active 3x3 chunks are instantiated in memory.
const RADIUS: int = 36
const COUNT: int = 9
const SIZE: int = RADIUS*2+1
const NAMES: Array[String] = [
    "temperate_forest", "dense_forest", "grassland_farmland",
    "swamp_wetland", "desert_wasteland", "rocky_highlands",
    "snowy_tundra", "lakes_rivers_coast", "urban_industrial_ruins"
]
# The existing ecology/canopy renderer knows only biome_id 0..3.
# Keep its physics and harvesting rules, and assign v263 macro id separately.
const LEGACY_BANDS: Array[int] = [3,3,1,0,2,2,0,0,2]
const PALETTE: Array[Color] = [
    Color("#728b59"),Color("#486344"),Color("#aaa06b"),
    Color("#607761"),Color("#beaa79"),Color("#8c887a"),
    Color("#c3c9bb"),Color("#7199a1"),Color("#77756e")
]

static func is_inside(coord: Vector2i) -> bool:
    return maxi(absi(coord.x),absi(coord.y)) <= RADIUS

static func _hash(seed: int, k: int) -> int:
    var n: int = (seed ^ (k*374761393)) & 0x7fffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0x7fffffff
    return (n ^ (n >> 16)) & 0x7fffffff

static func anchor(seed: int, biome: int) -> Vector2i:
    # The multiplier 5 is coprime with 9, guaranteeing unique sectors.
    var slot: int = posmod(biome*5 + posmod(seed,COUNT),COUNT)
    var h: int = _hash(seed, biome+1)
    var rotation: float = TAU * float(posmod(seed,997))/997.0
    var angle: float = rotation + TAU*float(slot)/float(COUNT)
    angle += float(posmod(h,101)-50)*0.0017
    var radius: float = 17.5 + float(posmod(h>>7,71)-35)*0.060
    return Vector2i(roundi(cos(angle)*radius),roundi(sin(angle)*radius))

static func _warp_at(p: Vector2, seed: int) -> Vector2:
    var phase: float = float(posmod(seed,8191))*0.0032
    return Vector2(
        sin(p.y*0.29+phase)*1.20 + cos(p.x*0.19-phase)*0.62,
        sin(p.x*0.27-phase)*1.20 + cos(p.y*0.21+phase)*0.62
    )

static func biome_at(p: Vector2, seed: int) -> int:
    var warped: Vector2 = p + _warp_at(p,seed)
    var best: int = 0
    var best_d: float = INF
    for i in range(COUNT):
        var delta: Vector2 = warped - Vector2(anchor(seed,i))
        var distance: float = delta.length_squared()
        if distance < best_d:
            best_d = distance
            best = i
    return best

static func biome_for_chunk(coord: Vector2i, seed: int) -> int:
    if not is_inside(coord):
        return -1
    return biome_at(Vector2(coord)+Vector2(0.5,0.5),seed)

static func legacy_band(biome: int) -> int:
    return LEGACY_BANDS[clampi(biome,0,COUNT-1)]

static func name_for(biome: int) -> String:
    return NAMES[clampi(biome,0,COUNT-1)]

static func counts_for_seed(seed: int) -> PackedInt32Array:
    var counts := PackedInt32Array()
    counts.resize(COUNT)
    for y in range(-RADIUS,RADIUS+1):
        for x in range(-RADIUS,RADIUS+1):
            var id: int = biome_for_chunk(Vector2i(x,y),seed)
            if id >= 0:
                counts[id] += 1
    return counts

static func every_biome_exists(seed: int) -> bool:
    # Anchors are protected guaranteed samples. Also checked exhaustively
    # by QA for many seeds, independent from this O(9) verification.
    for i in range(COUNT):
        if biome_for_chunk(anchor(seed,i),seed) != i:
            return false
    return true
