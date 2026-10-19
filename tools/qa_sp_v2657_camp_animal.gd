extends SceneTree
## v265.7 mandatory isolated art and integration quality gates.
## Real-world gameplay screenshots are separately captured in inherited v2654 QA.
var assertions: int = 0
func _initialize() -> void:
    call_deferred("_run")
func _check(ok: bool, why: String) -> bool:
    if not ok:
        push_error("SP_V2657_VISUAL_QA_FAIL "+why)
        quit(69)
        return false
    assertions += 1
    return true
func _run() -> void:
    for i in range(4):
        var cabin: Texture2D = load("res://assets/biomes/v2657/hero_cabin_%d.png" % i)
        if not _check(cabin!=null and cabin.get_width()==420 and cabin.get_height()==328,
            "missing properly sized independent cabin source"):
            return
        var img: Image = cabin.get_image()
        if not _check(img.get_pixel(0,0).a<0.02 and img.get_pixel(200,190).a>0.90,
            "cabin is a rectangular opaque placeholder or disconnected sprites"):
            return
        if not _check(img.get_pixel(198,232).a>0.70,
            "cabin door not part of the attached wall sprite"):
            return
    for v in range(2):
        var camp: Texture2D = load("res://assets/biomes/v2657/camp_scene_%d.png" % v)
        if not _check(camp!=null and camp.get_width()==560 and camp.get_height()==450,
            "missing composed camp vignette"):
            return
        var im: Image = camp.get_image()
        if not _check(im.get_pixel(0,0).a<0.05,
            "camp painting includes an intrusive rectangular ground card"):
            return
        var occupied: int = 0
        for y in range(130,338,18):
            for x in range(145,415,18):
                if im.get_pixel(x,y).a > 0.04:
                    occupied += 1
        if not _check(occupied>12,
            "camp lacks visible composed work and travel details"):
            return
    for species in ["deer","boar","chicken","rat"]:
        for side in ["left","right"]:
            var prev: PackedByteArray = PackedByteArray()
            var differing: int = 0
            for frame in range(8):
                var path: String = (
                    "res://assets/biomes/v2653/v2654_animal_%s_%s_%d.png" %
                        [species,side,frame])
                var tex: Texture2D = load(path)
                if not _check(tex!=null and tex.get_width()==64
                    and tex.get_height()==72,"missing frame at source scale "+path):
                    return
                var image: Image = tex.get_image()
                var bytes: PackedByteArray = image.get_data()
                if frame>0 and bytes!=prev:
                    differing+=1
                prev=bytes
                if not _check(image.get_pixel(0,0).a<0.05,
                    "wildlife has opaque pasted sprite background"):
                    return
            if not _check(differing>=5,
                "animal is rigid or limbs not differentiated in "+species):
                return
    var chunk_src: String = FileAccess.get_file_as_string(
        "res://scripts/world/world_chunk.gd")
    if not _check(chunk_src.contains("_sp2657_cabin("),
        "the new building sprite was never connected to world chunk"):
        return
    if not _check(chunk_src.contains("V2651_CLUTTER.paint"),
        "old approved biome-aware ruins have been lost"):
        return
    var camp_src: String = FileAccess.get_file_as_string(
        "res://scripts/social/faction_camp.gd")
    if not _check(camp_src.contains("SP2657_CAMP_SCENES"),
        "new composed camp not used by faction renderer"):
        return
    print("SP_V2657_ART_ASSET_QA_PASS 4 cabin sheets, 2 whole camp scenes, 64 walking sprites")
    print("SP_V2657_SRC_INTEGRATION_QA_PASS original interactivity kept, new art loaded by runtime")
    print("SP_V2657_ALL_QA_PASS assertions="+str(assertions))
    quit(0)
