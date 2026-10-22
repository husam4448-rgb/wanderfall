from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(); s=s.replace('var chunk: Node2D = _work.pop_front()', 'var chunk: Variant = _work.pop_front()'); p.write_text(s)
