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

SEP = "─" * 60

failures  = []
all_warns = []   # (yaml_path, [warning lines])

for yaml_path in yamls:
    print(f"\n{SEP}")
    print(f"  {yaml_path}")
    print(SEP)

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["msnoise", "db", "init", "--tech", "1",
             "--from-yaml", str(yaml_path.resolve())],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            input="3\n",
        )

    # stdout — strip blank lines for compactness
    for line in result.stdout.splitlines():
        if line.strip():
            print(f"  {line}")

    # stderr — split into warnings and real errors
    warns = [l for l in result.stderr.splitlines() if "WARNING" in l]
    errors = [l for l in result.stderr.splitlines() if l.strip() and "WARNING" not in l]

    if warns:
        print(f"\n  ⚠  {len(warns)} warning(s):")
        for w in warns:
            # strip the "WARNING:msnoise.core.config:" prefix for readability
            msg = w.split("WARNING")[-1].lstrip(":msnoise.core.config").lstrip(":")
            print(f"     {msg.strip()}")
        all_warns.append((str(yaml_path), warns))

    if result.returncode != 0:
        print(f"\n  ✖  FAILED")
        if errors:
            # print last 5 lines of traceback — enough to diagnose
            for line in errors[-5:]:
                print(f"     {line}")
        failures.append(str(yaml_path))
    else:
        print(f"\n  ✔  OK")

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'═' * 60}")
print(f"  Results: {len(yamls)} file(s) tested")

if all_warns:
    print(f"\n  Warnings ({sum(len(w) for _, w in all_warns)} total):")
    for path, warns in all_warns:
        print(f"    {path}: {len(warns)} warning(s)")
        for w in warns:
            msg = w.split("WARNING")[-1].lstrip(":msnoise.core.config").lstrip(":")
            print(f"      · {msg.strip()}")

if failures:
    print(f"\n  Failures ({len(failures)}):")
    for f in failures:
        print(f"    ✖  {f}")
    sys.exit(1)
else:
    print(f"\n  All passed ✔")
