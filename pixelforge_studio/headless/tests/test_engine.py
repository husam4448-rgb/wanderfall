import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from pixelforge_pipeline import demo_project,save,load,generate,render,export,auto_rig,blank_project,add_layer
from pixelforge_pipeline.engine import poses_for, image_of, put_image, validate

class EngineTest(unittest.TestCase):
 def test_project_roundtrip(self):
    p=demo_project()
    with tempfile.TemporaryDirectory() as td:
        fn=Path(td)/'test.pixelforge'
        save(p,fn);q=load(fn)
        self.assertEqual(len(p['documents']['character']['layers']),len(q['documents']['character']['layers']))
        self.assertEqual(image_of(q['documents']['character']['layers'][0]).size,(14,17))
 def test_frame_changes_without_proportion_drift(self):
    p=demo_project()
    a=render(p,'walk',0)
    b=render(p,'walk',2)
    self.assertNotEqual(a.tobytes(),b.tobytes())
    self.assertEqual(a.size,b.size)
 def test_character_directions(self):
    p=demo_project()
    right=render(p,'idle',0,'right')
    left=render(p,'idle',0,'left')
    self.assertEqual(left,right.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
 def test_joint_parent_follow(self):
    p=demo_project();ls=p['documents']['character']['layers']
    torso=next(x for x in ls if x['name']=='torso')
    head=next(x for x in ls if x['name']=='head')
    self.assertEqual(head['rig']['parentId'],torso['id'])
    original=poses_for(ls,0,'idle')[0][head['id']]['rotation']
    torso['poses']['idle']['0']={'rotation':33}
    rotated=poses_for(ls,0,'idle')[0][head['id']]['rotation']
    self.assertAlmostEqual(rotated-original,33)
 def test_manual_rig_preserved(self):
    p=demo_project();ls=p['documents']['character']['layers']; ls[0]['rig']['pivot']={'x':1,'y':3}
    auto_rig(p);self.assertEqual(ls[0]['rig']['pivot'],{'x':1,'y':3})
 def test_generate_12_frames(self):
    p=demo_project();generate(p,'run',frames=12)
    self.assertEqual(len(p['documents']['character']['layers'][0]['poses']['run']),12)
 def test_export_manifest_and_alpha(self):
    with tempfile.TemporaryDirectory() as td:
        p=demo_project();x=export(p,td,animations=('walk',),faces=('right',),frames=8,gif=True)
        self.assertEqual(Image.open(Path(td)/'SP_walk_right.png').size,(48*8,56))
        self.assertTrue((Path(td)/'SP_walk_right.gif').exists())
        self.assertTrue((Path(td)/'SP_Character_Rig.json').exists())
        self.assertEqual(x['animations']['walk']['right']['frames'],8)
 def test_import_layer(self):
    with tempfile.TemporaryDirectory() as td:
        im=Image.new('RGBA',(5,4),'#cc8822');src=Path(td)/'a.png';im.save(src)
        p=blank_project();lid=add_layer(p,src,'Bag','backpack',10,12)
        save(p,Path(td)/'saved.pixelforge')
        self.assertEqual(image_of(p['documents']['character']['layers'][0]).size,(5,4))
 def test_invalid_cycle(self):
    p=demo_project();ls=p['documents']['character']['layers']
    a,b=ls[0],ls[1];a['rig']['parentId']=b['id'];b['rig']['parentId']=a['id']
    with self.assertRaisesRegex(ValueError,'cycle'):poses_for(ls,0,'walk')
 def test_invalid_dimensions(self):
    with self.assertRaises(ValueError):blank_project(100000,10)

if __name__=='__main__':unittest.main()