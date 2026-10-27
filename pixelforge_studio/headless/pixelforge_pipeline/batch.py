"""Data-only scriptable Pixel Forge commands, suitable for automated asset tasks."""
from __future__ import annotations
import json
from pathlib import Path
from . import studio
from .engine import load,save,render,export

# No expression language or executable mods: all operations are explicit.
COMMANDS={
    'edit_whole_image':studio.edit_whole_image,
    'edit_parts':studio.edit_parts,
    'stamp':studio.stamp,
    'rotate_region':studio.rotate_region,
    'extract_region':studio.extract_region,
    'recolor':studio.recolor,
    'rig_layer':studio.rig_layer,
    'socket':studio.socket,
    'joint_limits':studio.joint_limits,
    'set_pose':studio.set_pose,
    'timeline':studio.configure_timeline,
    'save_pose':studio.save_pose_template,
    'apply_pose':studio.apply_pose_template,
    'workspace':studio.set_workspace,
    'transform_layer':studio.transform_layer,
    'resize_sprite':studio.resize_sprite,
    'attach_socket':studio.attach_socket,
    'skeleton_preset':studio.skeleton_preset,
    'update_skeleton_point':studio.update_skeleton_point,
}

def apply_commands(project, commands):
    """Execute a bounded declarative sequence on an editable project in memory."""
    if not isinstance(commands,list) or len(commands)>500:
        raise ValueError('Expected an array of up to 500 commands')
    log=[]
    clipboard=None
    for index,item in enumerate(commands):
        if not isinstance(item,dict):raise ValueError(f'Command {index} must be an object')
        op=item.get('op');args=item.get('args',{})
        if not isinstance(args,dict):raise ValueError('args must be an object')
        if op=='copy_region':
            clipboard=studio.copy_region(project,**args)
            value={'size':clipboard.size}
        elif op=='cut_region':
            clipboard=studio.cut_region(project,**args)
            value={'size':clipboard.size}
        elif op=='paste_region':
            if clipboard is None:raise ValueError('No clipboard image to paste')
            value=studio.paste_region(project,clipboard,**args)
        elif op=='sample_color':value=studio.sample_color(project,**args)
        elif op=='sample_shades':
            color=studio.sample_color(project,args['x'],args['y'])
            value=studio.shades_from_color(color) if color else None
        elif op in COMMANDS:value=COMMANDS[op](project,**args)
        else:raise ValueError(f'Unsupported operation: {op}')
        log.append({'index':index,'operation':op,'result':value})
    return log


def run_batch(src,commands_path,destination):
    project=load(src)
    raw=json.loads(Path(commands_path).read_text(encoding='utf-8'))
    commands=raw.get('commands') if isinstance(raw,dict) else raw
    result=apply_commands(project,commands)
    save(project,destination)
    return result