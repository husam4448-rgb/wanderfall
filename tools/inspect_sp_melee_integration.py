#!/usr/bin/env python3
"""Read-only source inspection before integrating SP melee into actual game."""
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); out=Path('sp_melee_source_inspection.txt')
paths=sorted(x for x in p.rglob('*') if x.is_file() and x.suffix in ('.gd','.tscn','.godot'))
terms=re.compile(r'(?i)melee|knife|slash|attack|shoot|fire|gun|weapon|aim|player|touch|inventory|quickbar|hotbar')
matches=[]
for path in paths:
    if path.suffix!='.gd':continue
    name=path.name.lower()
    lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
    hits=[i for i,line in enumerate(lines) if terms.search(line)]
    ranking=sum(w in name for w in ('player','combat','weapon','actor','character','aim','input','controller','main'))
    if ranking>=1 or len(hits)>18:
        matches.append((ranking,len(hits),path,lines,hits))
matches.sort(key=lambda t:(-t[0],-t[1],str(t[2])))
with out.open('w') as f:
    f.write(f'FILE COUNTS: {len(paths)} scene/script files, {len(matches)} relevant scripts\n\n')
    f.write('SOURCE SCRIPT PATHS (first 200):\n')
    for path in paths[:200]:
        f.write(str(path.relative_to(p))+'\n')
    f.write('\nRELEVANT FUNCTIONS/REFERENCES:\n')
    for rank,n,path,lines,hits in matches[:28]:
        f.write(f'\n--- {path.relative_to(p)} ({len(lines)} lines; {n} term hits) ---\n')
        kept=set()
        for i in hits[:24]:
            for j in range(max(0,i-1), min(len(lines),i+2)):
                if j not in kept:
                    f.write(f'{j+1:5d} {lines[j][:190]}\n')
                    kept.add(j)
    f.write('\nMAIN SCENE EXCERPT:\n')
    for name in ('scenes/main.tscn','project.godot'):
        file=p/name
        if file.exists():
            f.write(f'\n-- {name} --\n')
            f.write('\n'.join(file.read_text(encoding='utf-8',errors='replace').splitlines()[:180]))
            f.write('\n')
print('SP_MELEE_SOURCE_INSPECTION_DONE',out.stat().st_size,'bytes')
