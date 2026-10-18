shader_type canvas_item;
render_mode unshaded, blend_mix;

// Exact sprite/CanvasItem alpha remains authoritative. Canopies are represented
// by the same ellipses as WorldChunk.is_world_point_under_tree_canopy.
uniform vec4 silhouette_tint : source_color = vec4(1.0, 0.53, 0.12, 0.69);
uniform int canopy_count = 0;
uniform vec2 canopy_centers[24];
varying vec2 pixel_world;

void vertex() {
    pixel_world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}
void fragment() {
    float covered = 0.0;
    for (int i = 0; i < 24; i++) {
        if (i >= canopy_count) {
            break;
        }
        vec2 elliptical = (pixel_world - canopy_centers[i]) / vec2(50.0,57.0);
        if (dot(elliptical, elliptical) <= 1.0) {
            covered = 1.0;
            break;
        }
    }
    // For Sprite2D, incoming COLOR.a already contains original texture alpha;
    // for procedural 2D actor nodes, incoming alpha comes from draw primitives.
    COLOR = vec4(silhouette_tint.rgb, silhouette_tint.a * COLOR.a * covered);
}
