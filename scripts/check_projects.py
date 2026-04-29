#!/usr/bin/env python3
"""Run `msnoise db init --tech 1 --from-yaml` for every project*.yaml found
under papers/. Used by CI and can be run locally too:

    python scripts/check_projects.py
    python scripts/check_projects.py papers/2024_Yates_RuapehuSnow/project.yaml
"""
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(__file__).parent.parent

if len(sys.argv) > 1:
    yamls = [pathlib.Path(a) for a in sys.argv[1:]]
else:
    yamls = sorted(root.glob("papers/**/project*.yaml"))

if not yamls:
    print("No project*.yaml files found.")
    sys.exit(1)

failures = []
for yaml_path in yamls:
    print(f"\n── {yaml_path} ──")
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["msnoise", "db", "init", "--tech", "1",
             "--from-yaml", str(yaml_path.resolve())],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            input="3\n",
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            failures.append(str(yaml_path))
            print(f"FAIL: {yaml_path}")
        else:
            print(f"OK:   {yaml_path}")

if failures:
    print(f"\n{len(failures)} failure(s):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print(f"\nAll {len(yamls)} project file(s) passed.")
