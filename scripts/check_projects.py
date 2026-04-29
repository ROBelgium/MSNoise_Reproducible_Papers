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
import threading

root = pathlib.Path(__file__).parent.parent

if len(sys.argv) > 1:
    yamls = [pathlib.Path(a) for a in sys.argv[1:]]
else:
    yamls = sorted(root.glob("papers/**/project*.yaml"))

if not yamls:
    print("No project*.yaml files found.")
    sys.exit(1)

SEP = "─" * 60


def stream(pipe, prefix, store):
    """Read lines from pipe, print immediately, and accumulate in store."""
    for raw in pipe:
        line = raw.rstrip()
        print(f"{prefix}{line}", flush=True)
        store.append(line)


failures  = []
all_warns = []

for yaml_path in yamls:
    print(f"\n{SEP}")
    print(f"  {yaml_path}")
    print(SEP, flush=True)

    stdout_lines = []
    stderr_lines = []

    with tempfile.TemporaryDirectory() as tmpdir:
        proc = subprocess.Popen(
            ["msnoise", "db", "init", "--tech", "1",
             "--from-yaml", str(yaml_path.resolve())],
            cwd=tmpdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        proc.stdin.write("3\n")
        proc.stdin.close()

        # stream stdout and stderr concurrently so neither blocks the other
        t_out = threading.Thread(target=stream, args=(proc.stdout, "  ", stdout_lines))
        t_err = threading.Thread(target=stream, args=(proc.stderr, "  ", stderr_lines))
        t_out.start()
        t_err.start()
        t_out.join()
        t_err.join()
        proc.wait()

    warns  = [l for l in stderr_lines if "WARNING" in l]
    errors = [l for l in stderr_lines if l.strip() and "WARNING" not in l]

    if warns:
        all_warns.append((str(yaml_path), warns))

    if proc.returncode != 0:
        print(f"\n  ✖  FAILED")
        if errors:
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
