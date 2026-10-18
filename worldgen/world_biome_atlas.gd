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


# v264: visible ground palettes are opaque. v263 PALETTE remains available for
# QA atlas previews and backward-compatible biome queries.
const GROUND_PALETTE := [
    Color(0.29, 0.39, 0.24, 1.0), # temperate: moss/leaf soil
    Color(0.15, 0.26, 0.18, 1.0), # dense forest: deep humus
    Color(0.46, 0.48, 0.27, 1.0), # grassland: straw/grass
    Color(0.24, 0.33, 0.29, 1.0), # wetlands: silt/peat
    Color(0.67, 0.56, 0.38, 1.0), # dry mineral earth
    Color(0.43, 0.42, 0.39, 1.0), # scree
    Color(0.79, 0.83, 0.83, 1.0), # snow cover
    Color(0.35, 0.46, 0.37, 1.0), # lake shore / river bank
    Color(0.37, 0.36, 0.34, 1.0)  # post-collapse urban dust
]

static func smooth_biome_pair(location: Vector2, seed_value: int) -> Vector3:
    # x = closest biome, y = next closest biome, z = second biome mix amount.
    # The same continuous world-coordinate function is evaluated by neighbors
    # at shared polygon vertices. No chunk edge can introduce a hard tint seam.
    var sites: Array[Vector2i] = _anchors(seed_value)
    var phase: float = float(posmod(seed_value, 65521)) * 0.00037
    var warped: Vector2 = location + Vector2(
        sin(location.y * 0.13 + phase) * 3.4,
        cos(location.x * 0.11 - phase) * 3.4
    )
    var closest: int = 0
    var second: int = 1
    var closest_d: float = INF
    var second_d: float = INF
    for i in range(sites.size()):
        var region_scale: float = 0.88 + 0.21 * absf(sin(phase * 11.0 + float(i) * 2.2))
        var distance: float = warped.distance_to(Vector2(sites[i])) / sqrt(region_scale)
        if distance < closest_d:
            second_d = closest_d
            second = closest
            closest_d = distance
            closest = i
        elif distance < second_d:
            second_d = distance
            second = i
    var separation: float = maxf(0.0, second_d - closest_d)
    # A ~6 chunk transition width with zero discontinuity when sites exchange.
    var t: float = clampf(separation / 6.0, 0.0, 1.0)
    var fraction: float = 0.5 * (1.0 - t * t * (3.0 - 2.0 * t))
    return Vector3(float(closest), float(second), fraction)

static func smooth_ground_color(location: Vector2, seed_value: int) -> Color:
    var biome_pair: Vector3 = smooth_biome_pair(location, seed_value)
    return GROUND_PALETTE[int(biome_pair.x)].lerp(
        GROUND_PALETTE[int(biome_pair.y)], biome_pair.z)
