shader_type canvas_item;
render_mode unshaded, blend_mix;
// v265.1: sample the exact baked alpha of the displayed 112x112 canopy.
// The shader tints the player's actual precomposited silhouette only.
uniform vec4 silhouette_tint : source_color = vec4(1.0, 0.53, 0.12, 0.69);
uniform sampler2D canopy_alpha_atlas : filter_nearest, repeat_disable;
uniform int canopy_count = 0;
uniform vec2 canopy_centers[24];
uniform int canopy_types[24];
varying vec2 pixel_world;

void vertex() {
    pixel_world = (MODEL_MATRIX * vec4(VERTEX,0.0,1.0)).xy;
}
void fragment() {
    float covered = 0.0;
    for (int i=0;i<24;i++) {
        if (i>=canopy_count) { break; }
        vec2 offset_world = pixel_world-canopy_centers[i];
        if (canopy_types[i] >= 0) {
            // v265 canopy visual rect is centered on origin minus 43 pixels.
            // The 3x3 alpha atlas is 336px and each source occupies 112px.
            vec2 uv = (offset_world + vec2(56.0))/112.0;
            if (all(greaterThanEqual(uv,vec2(0.0))) &&
                all(lessThan(uv,vec2(1.0)))) {
                int cell = canopy_types[i];
                vec2 origin = vec2(float(cell % 3),float(cell / 3));
                float actual_alpha = texture(canopy_alpha_atlas,(origin+uv)/3.0).a;
                if (actual_alpha>0.15) {covered=1.0;break;}
            }
        } else {
            // Legacy atlas art for the six not-yet-repainted biomes.
            vec2 ellipse=offset_world/vec2(50.0,57.0);
            if (dot(ellipse,ellipse)<=1.0) {covered=1.0;break;}
        }
    }
    COLOR = vec4(silhouette_tint.rgb, silhouette_tint.a*COLOR.a*covered);
}
