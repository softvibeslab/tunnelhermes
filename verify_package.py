import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parent
manifest=json.loads((base/'SHA256SUMS.json').read_text())
for name,digest in manifest.items():
 p=base/name
 if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('FAIL '+name)
print('OK',len(manifest),'archivos verificados')
