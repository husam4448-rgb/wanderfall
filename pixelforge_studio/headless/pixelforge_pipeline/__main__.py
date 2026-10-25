"""Usage: python -m pixelforge_pipeline --help"""
import argparse
from pathlib import Path
from .engine import load,save,auto_rig,generate,export,demo_project,add_layer,ANIMATIONS

def main():
    p=argparse.ArgumentParser(description='Pixel Forge headless game asset pipeline')
    subs=p.add_subparsers(dest='command',required=True)
    d=subs.add_parser('demo',help='Create a sample compatible .pixelforge project and spritesheets')
    d.add_argument('output',type=Path)
    ins=subs.add_parser('inspect',help='Validate and report body parts of existing .pixelforge project')
    ins.add_argument('project',type=Path)
    rig=subs.add_parser('rig',help='Auto-assign roles and parent/pivot suggestions into a new project')
    rig.add_argument('project',type=Path);rig.add_argument('output',type=Path)
    gen=subs.add_parser('generate',help='Generate procedural animation poses and save editable project')
    gen.add_argument('project',type=Path);gen.add_argument('output',type=Path)
    gen.add_argument('--animation',choices=ANIMATIONS,default='walk')
    gen.add_argument('--frames',type=int,default=8);gen.add_argument('--strength',type=float,default=.9)
    ex=subs.add_parser('export',help='Render project to sprite sheets, GIF preview, rig JSON, manifest')
    ex.add_argument('project',type=Path);ex.add_argument('output',type=Path)
    ex.add_argument('--frames',type=int,default=8);ex.add_argument('--scale',type=int,default=1)
    ex.add_argument('--fps',type=int,default=8);ex.add_argument('--no-gif',action='store_true')
    attach=subs.add_parser('attach',help='Add PNG equipment/limb as layer to existing project')
    attach.add_argument('project',type=Path);attach.add_argument('png',type=Path)
    attach.add_argument('output',type=Path);attach.add_argument('--name',required=True)
    attach.add_argument('--role',default='other');attach.add_argument('--x',type=float,default=0)
    attach.add_argument('--y',type=float,default=0);attach.add_argument('--parent',default=None)
    args=p.parse_args()
    if args.command=='demo':
        args.output.mkdir(parents=True,exist_ok=True)
        project=demo_project();save(project,args.output/'SP_Demo_Character.pixelforge')
        export(project,args.output/'spritesheets')
        print('Created demo editable project and 8 sprite sheets in',args.output)
        return
    project=load(args.project)
    if args.command=='inspect':
        from .engine import role_of
        for name,doc in project['documents'].items():
            print(name,doc['w'],doc['h'],'layers=',len(doc['layers']))
            for layer in doc['layers']:
                print(' -',layer.get('id'),layer.get('name'),role_of(layer),'parent=',(layer.get('rig') or {}).get('parentId'))
    elif args.command=='rig':
        n=auto_rig(project);save(project,args.output);print('Rigged parts:',n)
    elif args.command=='generate':
        n=generate(project,args.animation,args.frames,args.strength)
        save(project,args.output);print('Generated poses for',n,'parts')
    elif args.command=='export':
        if args.frames < 1 or args.frames > 64: raise SystemExit('frames must be 1..64')
        if args.fps < 1 or args.fps > 60: raise SystemExit('fps must be 1..60')
        manifest=export(project,args.output,frames=args.frames,scale=args.scale,fps=args.fps,gif=not args.no_gif)
        print('Exported',len(manifest['animations'])*2,'sprite sheets in',args.output)
    elif args.command=='attach':
        id=add_layer(project,args.png,args.name,args.role,args.x,args.y,parent_id=args.parent)
        save(project,args.output);print('Added editable layer',id)

if __name__ == '__main__': main()