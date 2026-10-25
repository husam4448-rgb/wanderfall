import unittest
from pixelforge_pipeline.engine import demo_project, poses_for, render, generate
class RigExpansion09Tests(unittest.TestCase):
    def test_socket_tracks_parent_rotation(self):
        p=demo_project();ls=p["documents"]["character"]["layers"]
        torso=next(x for x in ls if x["name"]=="torso")
        head=next(x for x in ls if x["name"]=="head")
        torso["rig"]["sockets"]=[{"name":"top","x":7,"y":1}]
        head["rig"].update({"attachSocket":"top","linkMode":"rigid","offsetX":0,"offsetY":-1})
        first=poses_for(ls,0,"idle")[0][head["id"]]
        torso["poses"]["idle"]["0"]={"rotation":35}
        second=poses_for(ls,0,"idle")[0][head["id"]]
        self.assertNotEqual((first["x"],first["y"]),(second["x"],second["y"]))
        self.assertAlmostEqual(second["rotation"]-first["rotation"],35)
    def test_nonuniform_scale_affects_image(self):
        p=demo_project();part=next(x for x in p["documents"]["character"]["layers"] if x["name"]=="head")
        base=render(p,"idle",0).tobytes()
        part["rig"]["scaleX"]=1.5;part["rig"]["scaleY"]=.8
        self.assertNotEqual(base,render(p,"idle",0).tobytes())
    def test_timeline_persisted(self):
        p=demo_project();generate(p,anim="walk",frames=16)
        self.assertEqual(p["documents"]["character"]["timelines"]["walk"]["count"],16)
if __name__=="__main__":unittest.main()
