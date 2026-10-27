import copy
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from pixelforge_pipeline import demo_project,save,load,render
from pixelforge_pipeline.engine import image_of
from pixelforge_pipeline.studio import (
    BRUSH_SHAPES,brush_mask,edit_whole_image,edit_parts,stamp,copy_region,cut_region,
    paste_region,rotate_region,extract_region,recolor,shades_from_color,sample_color,
    palette_import,set_workspace,rig_layer,socket,joint_limits,set_pose,
    configure_timeline,save_pose_template,apply_pose_template)

class StudioTest(unittest.TestCase):
    def test_brush_shapes_and_preview(self):
        for s in BRUSH_SHAPES:
            offsets=brush_mask(9,s)
            self.assertTrue(offsets)
            self.assertTrue(all(-4<=x<=4 and -4<=y<=4 for x,y in offsets))
        self.assertEqual(len(brush_mask(5,'square')),25)
        self.assertEqual(len(brush_mask(5,'horizontal')),5)
        self.assertEqual(len(brush_mask(5,'outline')),16)
    def test_whole_image_and_restore_parts(self):
        p=demo_project();d=p['documents']['character'];n=len(d['layers'])
        lid=edit_whole_image(p)
        self.assertEqual(len(d['layers']),n+1)
        self.assertTrue(d['wholeCanvas']['active'])
        self.assertEqual(image_of(d['layers'][-1]).size,(48,56))
        stamp(p,45,50,'#ff0000',size=1)
        self.assertEqual(image_of(d['layers'][-1]).getpixel((45,50)),(255,0,0,255))
        self.assertTrue(edit_parts(p));self.assertFalse(d['wholeCanvas']['active'])
        self.assertEqual(len(d['layers']),n+1)
        self.assertEqual(edit_whole_image(p),lid)
        self.assertEqual(image_of(d['layers'][-1]).getpixel((45,50)),(255,0,0,255))
    def test_selection_rotation_copy_cut_extract(self):
        p=demo_project();edit_whole_image(p)
        stamp(p,4,4,'#8800ff',size=3)
        cp=copy_region(p,(3,3,3,3))
        self.assertEqual(cp.size,(3,3))
        box=rotate_region(p,(3,3,3,3),90)
        self.assertTrue(box[2]>=3)
        src=cut_region(p,(box[0],box[1],box[2],box[3]))
        self.assertEqual(src.size,(box[2],box[3]))
        paste_region(p,src,15,15)
        id=extract_region(p,(15,15,3,3),name='Extracted mask',role='mask')
        self.assertIn(id,[a['id'] for a in p['documents']['character']['layers']])
    def test_colors_palette_workspace(self):
        p=demo_project()
        self.assertEqual(len(shades_from_color('#807040')),15)
        w=set_workspace(p,preset='Obsidian',checker_brightness=10)
        self.assertEqual(w['outside'],'#080b0e')
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/'palette.gpl';f.write_text('GIMP Palette\nName: Sample\n255 0 128 Pink\n12 34 56 Dark\n')
            self.assertEqual(palette_import(f),['#ff0080','#0c2238'])
            save(p,Path(temp)/'x.pixelforge')
            self.assertEqual(load(Path(temp)/'x.pixelforge')['studioSettings']['workspace']['preset'],'Obsidian')
    def test_rig_pivots_socket_constraints_timeline(self):
        p=demo_project();ls=p['documents']['character']['layers']
        head=next(l for l in ls if l['name']=='head')
        torso=next(l for l in ls if l['name']=='torso')
        rig_layer(p,head['id'],'head',pivot=(5,7),parent_id=torso['id'])
        self.assertEqual(head['rig']['pivot'],{'x':5.,'y':7.})
        socket(p,torso['id'],'backpack',(3),(10))
        self.assertEqual(len(torso['rig']['sockets']),1)
        joint_limits(p,head['id'],-20,20)
        pose=set_pose(p,head['id'],'walk',0,rotation=80)
        self.assertEqual(pose['rotation'],20)
        configure_timeline(p,'walk',12,10)
        save_pose_template(p,'pose1','walk',0)
        set_pose(p,head['id'],'walk',0,rotation=-10)
        apply_pose_template(p,'pose1','walk',1)
        self.assertEqual(head['poses']['walk']['1']['rotation'],20)
        self.assertEqual(p['documents']['character']['timelines']['walk']['count'],12)
    def test_recolor_and_no_alpha_damage(self):
        p=demo_project(); lid=edit_whole_image(p)
        stamp(p,44,55,'#123456')
        count=recolor(p,'#123456','#abcdef')
        self.assertGreater(count,0)
        self.assertEqual(image_of(p['documents']['character']['layers'][-1]).getpixel((44,55)),(171,205,239,255))
        self.assertIsNone(sample_color(p,47,55))

if __name__=='__main__':unittest.main()

class BatchTest(unittest.TestCase):
    def test_batch_roundtrip(self):
        from pixelforge_pipeline.batch import apply_commands
        p=demo_project()
        commands=[{'op':'edit_whole_image'},
                  {'op':'stamp','args':{'x':44,'y':53,'color':'#eeaa00','size':1}},
                  {'op':'copy_region','args':{'rect':[44,53,1,1]}},
                  {'op':'paste_region','args':{'x':42,'y':51}},
                  {'op':'timeline','args':{'animation':'walk','frames':16,'fps':12}},
                  {'op':'workspace','args':{'preset':'Charcoal'}}]
        result=apply_commands(p,commands)
        self.assertEqual(len(result),6)
        self.assertEqual(image_of(p['documents']['character']['layers'][-1]).getpixel((42,51)),(238,170,0,255))
    def test_data_only_no_code_execution(self):
        from pixelforge_pipeline.batch import apply_commands
        with self.assertRaises(ValueError):apply_commands(demo_project(),[{'op':'eval','args':{'code':'x'}}])

class AdvancedTest(unittest.TestCase):
    def test_geometry_and_modular_attachment(self):
        from pixelforge_pipeline.studio import (transform_layer,resize_sprite,
             skeleton_preset,update_skeleton_point,solve_two_bone_ik,attach_socket)
        p=demo_project();ls=p['documents']['character']['layers']
        torso=next(x for x in ls if x['name']=='torso');head=next(x for x in ls if x['name']=='head')
        transform_layer(p,head['id'],rotation=45,scale_x=1.2,scale_y=.8)
        self.assertEqual(head['rotation'],45)
        resize_sprite(p,head['id'],24,20)
        self.assertEqual(image_of(head).size,(24,20))
        nodes=skeleton_preset(p,'minimal')
        self.assertEqual([x['name'] for x in nodes],['head','torso','legs'])
        update_skeleton_point(p,'head',x=12,y=13,layer_id=head['id'])
        self.assertEqual(nodes[0]['layerId'],head['id'])
        from pixelforge_pipeline.studio import socket
        socket(p,torso['id'],'neck',7,1)
        attach_socket(p,head['id'],torso['id'],'neck')
        self.assertEqual(head['rig']['attachSocket'],'neck')
        sol=solve_two_bone_ik((0,0),8,8,(10,0))
        self.assertAlmostEqual(sol['wrist'][0],10,places=3)
        self.assertAlmostEqual(sum(v*v for v in sol['elbow']),64,places=3)