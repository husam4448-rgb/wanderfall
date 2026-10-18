extends RefCounted
## SP v264 — deterministic seamless biome-specific terrain and ground ecology.
## A purely visual layer: no physics bodies, NPC spawns, collision or save changes.
## All details are generated inside the chunk's existing _draw() cache.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const GRID: int = 10

static func _random_grid(x: int, y: int, seed_value: int) -> float:
    var f: float = sin(float(x) * 127.17 + float(y) * 311.73 +
        float(posmod(seed_value, 65521)) * 0.1517) * 43758.5453
    return f - floorf(f)

static func _noise(position: Vector2, seed_value: int) -> float:
    var cell: Vector2 = position.floor()
    var fx: float = position.x - cell.x
    var fy: float = position.y - cell.y
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)
    var x: int = int(cell.x)
    var y: int = int(cell.y)
    var low: float = lerpf(_random_grid(x, y, seed_value),
        _random_grid(x + 1, y, seed_value), fx)
    var high: float = lerpf(_random_grid(x, y + 1, seed_value),
        _random_grid(x + 1, y + 1, seed_value), fx)
    return lerpf(low, high, fy)

static func _ground_at(position: Vector2, seed_value: int) -> Color:
    var base: Color = ATLAS.smooth_ground_color(position, seed_value)
    var broad: float = _noise(position * 1.7, seed_value + 79)
    var fine: float = _noise(position * 11.0, seed_value + 139)
    var shade: float = 0.88 + broad * 0.15 + fine * 0.085
    return Color(base.r * shade, base.g * shade, base.b * shade, 1.0)

static func _paint_surface(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    # Each quad is Gouraud interpolated. Neighboring chunks share exact
    # world-space vertex colors, including seeded low-frequency soil noise.
    var samples: Array[Color] = []
    for iy in range(GRID + 1):
        for ix in range(GRID + 1):
            var world_location: Vector2 = Vector2(coord) + Vector2(
                float(ix) / float(GRID), float(iy) / float(GRID))
            samples.append(_ground_at(world_location, seed_value))
    var step: float = chunk_size / float(GRID)
    for iy in range(GRID):
        for ix in range(GRID):
            var left: float = float(ix) * step
            var top: float = float(iy) * step
            var pts: PackedVector2Array = PackedVector2Array([
                Vector2(left, top), Vector2(left + step, top),
                Vector2(left + step, top + step), Vector2(left, top + step)])
            var a: int = iy * (GRID + 1) + ix
            canvas.draw_polygon(pts, PackedColorArray([
                samples[a], samples[a + 1],
                samples[a + GRID + 2], samples[a + GRID + 1]]))

static func _stroke(canvas: CanvasItem, p: Vector2, d: Vector2, c: Color,
        width: float = 1.0) -> void:
    canvas.draw_line(p, p + d, c, width, false)

static func _stone(canvas: CanvasItem, p: Vector2, radius: float,
        dark: Color, lit: Color) -> void:
    var poly: PackedVector2Array = PackedVector2Array([
        p + Vector2(-radius, radius * 0.4),
        p + Vector2(-radius * 0.65, -radius * 0.72),
        p + Vector2(radius * 0.40, -radius),
        p + Vector2(radius, radius * 0.22),
        p + Vector2(radius * 0.25, radius * 0.83)])
    canvas.draw_polygon(poly, PackedColorArray([dark, lit, lit, dark, dark]))
    _stroke(canvas, p + Vector2(-radius * 0.5, -radius * 0.3),
        Vector2(radius * 0.72, -radius * 0.25), lit)

static func _fern(canvas: CanvasItem, p: Vector2, scale: float,
        leaf: Color, stalk: Color) -> void:
    for side in [-1.0, 1.0]:
        _stroke(canvas, p, Vector2(side * scale * 0.75, -scale), stalk)
        for i in range(1, 4):
            var t: float = float(i) / 4.0
            var node: Vector2 = p + Vector2(side * scale * 0.75 * t, -scale * t)
            _stroke(canvas, node,
                Vector2(side * scale * (0.25 + t * 0.1), scale * 0.1), leaf)
            _stroke(canvas, node, Vector2(-side * scale * 0.15, -scale * 0.32), leaf)

static func _grass(canvas: CanvasItem, p: Vector2, s: float,
        a: Color, b: Color) -> void:
    _stroke(canvas, p, Vector2(-s * 0.45, -s), a)
    _stroke(canvas, p + Vector2(s * 0.12, 0.0), Vector2(s * 0.28, -s * 1.25), b)
    _stroke(canvas, p + Vector2(-s * 0.16, 0.0), Vector2(-s * 0.18, -s * 0.80), a)
    _stroke(canvas, p + Vector2(s * 0.26, -s * 0.73),
        Vector2(s * 0.35, -s * 0.2), b)

static func _dry_crack(canvas: CanvasItem, p: Vector2, s: float,
        c: Color) -> void:
    _stroke(canvas, p + Vector2(-s, s * 0.2), Vector2(s * 0.8, -s * 0.35), c)
    _stroke(canvas, p + Vector2(-s * 0.2, -s * 0.15), Vector2(s * 0.9, s * 0.15), c)
    _stroke(canvas, p + Vector2(s * 0.4, 0.0), Vector2(s * 0.2, s * 0.65), c)

static func _clutter(canvas: CanvasItem, p: Vector2, id: int,
        rng: RandomNumberGenerator, size: float) -> void:
    var v: float = rng.randf()
    match id:
        0: # Temperate woodland: litter, bracken, twig clusters.
            if v < 0.38:
                _fern(canvas, p, size * 0.68,
                    Color(0.23, 0.40, 0.21, 0.92), Color(0.14, 0.26, 0.15, 0.9))
            elif v < 0.72:
                for i in range(4):
                    var d: Vector2 = Vector2(rng.randf_range(-size, size),
                        rng.randf_range(-size * 0.35, size * 0.35))
                    _stroke(canvas, p + d, Vector2(size * 0.36, size * 0.13),
                        Color(0.33, 0.28, 0.16, 0.8), 1.4)
            else:
                _grass(canvas, p, size * 0.68,
                    Color(0.21, 0.42, 0.20, 0.85), Color(0.43, 0.48, 0.22, 0.90))
        1: # Dark forest: broad ferns, decaying bark, dense shade.
            if v < 0.63:
                _fern(canvas, p, size * 1.05,
                    Color(0.12, 0.33, 0.19, 0.95), Color(0.10, 0.23, 0.12, 0.95))
            else:
                canvas.draw_rect(Rect2(p - Vector2(size, 2.0),
                    Vector2(size * 2.0, 4.0)), Color(0.20, 0.17, 0.12, 0.78))
                _stroke(canvas, p - Vector2(size * 0.6, 0.3),
                    Vector2(size, -0.1), Color(0.34, 0.31, 0.21, 0.75))
                for i in range(3):
                    canvas.draw_circle(p + Vector2(rng.randf_range(-size, size),
                        rng.randf_range(-2.0, 3.0)), 1.2,
                        Color(0.35, 0.44, 0.28, 0.74))
        2: # Plains: gold and olive tufts, small flower/seed heads.
            _grass(canvas, p, size * 1.1, Color(0.57, 0.55, 0.26, 0.9),
                Color(0.31, 0.45, 0.21, 0.86))
            if v < 0.18:
                canvas.draw_circle(p + Vector2(size * 0.35, -size),
                    1.2, Color(0.84, 0.73, 0.43, 0.90))
        3: # Marsh: reeds, peat pools, rushes.
            if v < 0.68:
                for i in range(4):
                    var dx: float = float(i - 2) * 2.6
                    var top: float = size * rng.randf_range(0.9, 1.5)
                    _stroke(canvas, p + Vector2(dx, 0),
                        Vector2(dx * 0.15, -top), Color(0.40, 0.47, 0.28, 0.95), 1.3)
                    if i % 2 == 0:
                        _stroke(canvas, p + Vector2(dx, -top),
                            Vector2(0, -2.6), Color(0.31, 0.25, 0.15, 0.90), 2.0)
            else:
                canvas.draw_circle(p, size * 0.80,
                    Color(0.15, 0.30, 0.29, 0.34))
                _stroke(canvas, p - Vector2(size * 0.47, 0),
                    Vector2(size * 0.72, -1.1), Color(0.43, 0.55, 0.52, 0.36))
        4: # Badlands: wind-cut mineral ripples, dry roots, cracked soil.
            if v < 0.60:
                for i in range(3):
                    _stroke(canvas, p + Vector2(-size * 0.9, float(i) * 3.0),
                        Vector2(size * 1.7, -size * 0.18),
                        Color(0.51, 0.42, 0.28, 0.44), 1.0)
            elif v < 0.84:
                _dry_crack(canvas, p, size,
                    Color(0.46, 0.36, 0.24, 0.75))
            else:
                _grass(canvas, p, size * 0.6,
                    Color(0.39, 0.37, 0.21, 0.80), Color(0.53, 0.45, 0.27, 0.75))
        5: # Highland: scree, chipped slate, geological fractures.
            _stone(canvas, p, size * rng.randf_range(0.62, 1.16),
                Color(0.26, 0.27, 0.27, 0.96), Color(0.59, 0.58, 0.52, 0.98))
            if v < 0.45:
                _dry_crack(canvas, p + Vector2(size, size * 0.5), size * 0.8,
                    Color(0.27, 0.28, 0.27, 0.72))
        6: # Tundra: blown ice, frozen gravel, stubborn brown stems.
            if v < 0.63:
                for i in range(3):
                    _stroke(canvas, p + Vector2(-size, float(i) * 3.2),
                        Vector2(size * rng.randf_range(1.2, 2.3), -2.0),
                        Color(0.96, 0.98, 0.98, 0.68), 1.2)
            elif v < 0.85:
                _stone(canvas, p, size * 0.70,
                    Color(0.48, 0.56, 0.58, 0.84),
                    Color(0.84, 0.88, 0.87, 0.95))
            else:
                _grass(canvas, p, size * 0.38,
                    Color(0.47, 0.42, 0.33, 0.65),
                    Color(0.40, 0.48, 0.41, 0.65))
        7: # Freshwater margins: river pebbles, reeds, ripple lines.
            if v < 0.36:
                _stone(canvas, p, size * 0.57,
                    Color(0.29, 0.37, 0.36, 0.88),
                    Color(0.55, 0.61, 0.56, 0.9))
            elif v < 0.72:
                for i in range(2):
                    _stroke(canvas, p + Vector2(-size, 3.1 * float(i)),
                        Vector2(size * 1.8, 0.0),
                        Color(0.49, 0.68, 0.66, 0.40))
            else:
                _grass(canvas, p, size,
                    Color(0.26, 0.43, 0.35, 0.9),
                    Color(0.47, 0.56, 0.32, 0.85))
        8: # Urban ruins: fractured asphalt, rebar, concrete/brick rubble.
            if v < 0.51:
                _stone(canvas, p, size * 1.12,
                    Color(0.23, 0.24, 0.24, 0.94),
                    Color(0.53, 0.52, 0.48, 0.93))
                if v < 0.18:
                    _stroke(canvas, p - Vector2(size, 0),
                        Vector2(size * 2.1, -size * 0.8),
                        Color(0.31, 0.23, 0.19, 0.93), 1.6)
            elif v < 0.81:
                _dry_crack(canvas, p, size * 1.1,
                    Color(0.19, 0.19, 0.18, 0.80))
            else:
                canvas.draw_rect(Rect2(p - Vector2(size * 0.65, size * 0.4),
                    Vector2(size * 1.3, size * 0.8)),
                    Color(0.42, 0.31, 0.27, 0.84))
                _stroke(canvas, p - Vector2(size * 0.5, 0),
                    Vector2(size * 0.95, 0),
                    Color(0.22, 0.21, 0.20, 0.80))

static func _paint_ecology(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    # Stable sparse occupancy; guaranteed independent from camera updates.
    var rng: RandomNumberGenerator = RandomNumberGenerator.new()
    rng.seed = seed_value + coord.x * 73856093 + coord.y * 19349663 + 99223
    var center_pair: Vector3 = ATLAS.smooth_biome_pair(
        Vector2(coord) + Vector2(0.5, 0.5), seed_value)
    var first: int = int(center_pair.x)
    var second: int = int(center_pair.y)
    var density: PackedInt32Array = PackedInt32Array([
        49, 65, 59, 54, 34, 44, 39, 43, 54])
    var max_features: int = int(lerpf(
        float(density[first]), float(density[second]), center_pair.z))
    for i in range(max_features):
        var position: Vector2 = Vector2(
            rng.randf_range(4.0, chunk_size - 4.0),
            rng.randf_range(4.0, chunk_size - 4.0))
        var world_location: Vector2 = Vector2(coord) + position / chunk_size
        var pair: Vector3 = ATLAS.smooth_biome_pair(world_location, seed_value)
        var chosen: int = int(pair.x)
        if rng.randf() < pair.z:
            chosen = int(pair.y)
        _clutter(canvas, position, chosen, rng, rng.randf_range(3.2, 8.4))
    # Micro-flecks break up large solid patches without adding game entities.
    for i in range(90):
        var p: Vector2 = Vector2(rng.randf() * chunk_size,
            rng.randf() * chunk_size)
        var pair: Vector3 = ATLAS.smooth_biome_pair(
            Vector2(coord) + p / chunk_size, seed_value)
        var id: int = int(pair.x)
        if rng.randf() < pair.z:
            id = int(pair.y)
        var ground: Color = ATLAS.GROUND_PALETTE[id]
        var fleck: Color = ground.darkened(0.16 + rng.randf() * 0.14)
        fleck.a = 0.56
        var width: float = rng.randf_range(0.8, 2.3)
        _stroke(canvas, p, Vector2(width * 1.8, -width * 0.30),
            fleck, width)

static func paint(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    _paint_surface(canvas, coord, seed_value, chunk_size)
    _paint_ecology(canvas, coord, seed_value, chunk_size)
