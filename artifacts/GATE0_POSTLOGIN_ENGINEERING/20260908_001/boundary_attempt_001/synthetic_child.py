import os, json, sys
from pathlib import Path
p = Path(sys.argv[1])
parent = p.parent
os.makedirs(parent, exist_ok=True)
fd = os.open(p, os.O_WRONLY | os.O_TRUNC | os.O_CREAT, 0o600)
os.write(fd, b"synthetic native-pattern replacement\n")
os.fsync(fd)
os.close(fd)
blocked = False
try:
    fd = os.open(parent / "forbidden_sibling", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except OSError as e:
    blocked = e.errno in (1, 13, 30)
else:
    os.close(fd)
print(json.dumps({"same_file_write_completed": True, "existing_parent_create_dir_all_completed": True, "sibling_write_blocked": blocked, "network_requests_made": False}))
raise SystemExit(0 if blocked else 4)
