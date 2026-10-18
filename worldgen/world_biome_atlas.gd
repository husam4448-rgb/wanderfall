extends RefCounted
## Survival Paradise world atlas v263.
## All nine biomes are mandatory in EVERY seed; seed changes anchor placement,
## region shape and boundaries, not membership. Chunk streaming stays unchanged.
const WORLD_RADIUS_CHUNKS: int = 60
const BIOME_IDS := [
    "temperate_forest", "dense_forest", "grassland", "wetlands",
    "desert_wasteland", "rocky_highlands", "snow_tundra",
    "lakes_rivers", "urban_ruins"
]
const PALETTE := [
    Color(0.22, 0.40, 0.21, 0.10), # temperate
    Color(0.12, 0.29, 0.17, 0.23), # deep canopy
    Color(0.40, 0.54, 0.21, 0.12), # meadows
    Color(0.14, 0.37, 0.39, 0.20), # wetlands
    Color(0.74, 0.56, 0.26, 0.33), # dry wasteland
    Color(0.41, 0.39, 0.36, 0.26), # rocky highlands
    Color(0.69, 0.78, 0.82, 0.35), # snow/ice
    Color(0.16, 0.41, 0.65, 0.22), # freshwater/coasts
    Color(0.39, 0.37, 0.35, 0.30)  # urban ruins / ash
]

static func is_inside_world(coord: Vector2i) -> bool:
    return coord.length_squared() <= WORLD_RADIUS_CHUNKS * WORLD_RADIUS_CHUNKS

static func biome_name(index: int) -> String:
    if index < 0 or index >= BIOME_IDS.size():
        return "outside"
    return BIOME_IDS[index]

static func _anchors(seed_value: int) -> Array[Vector2i]:
    var rng := RandomNumberGenerator.new()
    rng.seed = int(seed_value) ^ 0x52BA29
    var coords: Array[Vector2i] = []
    # Initial camp remains safe and temperate; its exact center varies by seed.
    coords.append(Vector2i(rng.randi_range(-3,3),rng.randi_range(-3,3)))
    # Each of 8 remaining biomes gets one guaranteed macro region.
    var slots: Array[int] = [1,2,3,4,5,6,7,8]
    for i in range(slots.size()-1,0,-1):
        var j: int = rng.randi_range(0,i)
        var swap: int = slots[i]
        slots[i] = slots[j]
        slots[j] = swap
    var rotation: float = rng.randf_range(0.0, TAU)
    coords.resize(BIOME_IDS.size())
    for i in range(8):
        var angle: float = rotation + TAU * float(i)/8.0
        var radius: float = rng.randf_range(33.0,42.0)
        coords[slots[i]] = Vector2i(roundi(cos(angle)*radius),roundi(sin(angle)*radius))
    return coords

static func guaranteed_anchors(seed_value: int) -> Array[Vector2i]:
    return _anchors(seed_value)

static func _dominant_at(location: Vector2,seed_value: int) -> int:
    var anchors: Array[Vector2i] = _anchors(seed_value)
    # Guaranteed anchor identity is never displaced by boundary warping.
    for i in range(anchors.size()):
        if location.distance_squared_to(Vector2(anchors[i])) < 0.001:
            return i
    var phase: float = float(posmod(seed_value,65521)) * 0.00037
    var point: Vector2 = location + Vector2(
        sin(location.y*0.13 + phase) * 3.4,
        cos(location.x*0.11 - phase) * 3.4)
    var best_id: int = 0
    var best_dist: float = INF
    for i in range(anchors.size()):
        var region_center: Vector2 = Vector2(anchors[i])
        var dist: float = point.distance_squared_to(region_center)
        # Subtle deterministic site-scale variation creates unequal regions.
        var region_scale: float = 0.88 + 0.21*absf(sin(phase*11.0 + float(i)*2.2))
        dist /= region_scale
        if dist < best_dist:
            best_dist = dist
            best_id = i
    return best_id

static func biome_for_chunk(coord: Vector2i, seed_value: int) -> int:
    if not is_inside_world(coord):
        return -1
    return _dominant_at(Vector2(coord),seed_value)

static func biome_at_position(chunk_location: Vector2,seed_value: int) -> int:
    if chunk_location.length() > float(WORLD_RADIUS_CHUNKS):
        return -1
    return _dominant_at(chunk_location,seed_value)

static func surface_tint(chunk_location: Vector2,seed_value: int) -> Color:
    var id: int = biome_at_position(chunk_location,seed_value)
    if id < 0:
        return Color(0.10,0.25,0.40,0.40)
    return PALETTE[id]

static func legacy_band(index: int) -> int:
    # Existing ecology expects only four grass/wet/dry/forest buckets.
    # This compatibility mapping keeps the proven v262 performance profile.
    match index:
        0,1: return 3
        2: return 1
        3,7: return 0
        4,5: return 2
        6: return 1
        8: return 1
    return 1

static func biome_counts(seed_value: int) -> PackedInt32Array:
    var counts := PackedInt32Array()
    counts.resize(BIOME_IDS.size())
    for i in range(counts.size()):
        counts[i] = 0
    for y in range(-WORLD_RADIUS_CHUNKS,WORLD_RADIUS_CHUNKS+1):
        for x in range(-WORLD_RADIUS_CHUNKS,WORLD_RADIUS_CHUNKS+1):
            var id: int = biome_for_chunk(Vector2i(x,y),seed_value)
            if id >= 0:
                counts[id] += 1
    return counts
