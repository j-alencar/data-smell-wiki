"""Run every smell page example on its engine and record the outputs.

Pages show src/_data/saidas.json, so every output on the site is a real run.

  mise run verify               # run all, rewrite saidas.json
  mise run verify -- -c         # fail if saidas.json is stale (CI)
  mise run verify -- texto/casing   # only pages whose key contains this
"""
import argparse
import csv
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import duckdb
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
HELPERS = ROOT / "helpers"
OUT = SRC / "_data" / "saidas.json"
WORLDS = ["serie-temporal", "numerico", "texto"]
COMPOSE = ["docker", "compose", "-f", str(ROOT / "compose.yaml")]


def need(binary, hint):
    if shutil.which(binary) is None:
        sys.exit(f"verify: {binary} not found -- {hint}")


def load_pages(only):
    pages = {}
    for world in WORLDS:
        for md in sorted((SRC / world).glob("*.md")):
            key = f"{world}/{md.stem}"
            if only and not any(o in key for o in only):
                continue
            front = md.read_text().split("---\n")[1]
            try:
                ex = (yaml.safe_load(front) or {}).get("exemplo")
            except yaml.YAMLError as e:
                sys.exit(f"verify: bad frontmatter in {md.relative_to(ROOT)}\n{e}")
            if ex:
                pages[key] = ex
    return pages


def na(block):
    return isinstance(block, dict) and "na" in block


def run_duckdb(ex):
    con = duckdb.connect()
    con.execute((HELPERS / "duckdb.sql").read_text())
    con.execute(ex["sql"])
    table = re.search(r"CREATE TABLE (\w+)", ex["sql"]).group(1)
    r = con.execute(f"SELECT * FROM {table}")
    entrada = {"cols": [d[0] for d in r.description], "rows": [[fmt(v) for v in row] for row in r.fetchall()]}
    if na(ex["duckdb"]):
        return entrada, None
    r = con.execute(ex["duckdb"])
    return entrada, {"cols": [d[0] for d in r.description], "rows": [[fmt(v) for v in row] for row in r.fetchall()]}


def fmt(v):
    return "NULL" if v is None else str(v)


def run_postgres(ex):
    script = "BEGIN;\n" + (HELPERS / "postgres.sql").read_text() + ex["sql"] + "\n" + ex["postgres"] + "\nROLLBACK;\n"
    p = subprocess.run(COMPOSE + ["exec", "-T", "postgres", "psql", "-U", "postgres", "-X", "-q", "--csv",
                                  "-v", "ON_ERROR_STOP=1", "-P", "null=NULL"],
                       input=script, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    rows = list(csv.reader(io.StringIO(p.stdout)))
    return {"cols": rows[0], "rows": rows[1:]}


def run_jq(ex):
    j = ex["jq"]
    prog = (HELPERS / "pattern.jq").read_text() + j["filtro"]
    args = ["jq", "-c"] + (["-s"] if j.get("slurp") else []) + [prog]
    p = subprocess.run(args, input=j["entrada"], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


def run_mongo(pages):
    keys = [k for k, ex in pages.items() if not na(ex["mongo"])]
    if not keys:
        return {}
    parts = [(HELPERS / "mongo.js").read_text(), "db = db.getSiblingDB('verify'); db.dropDatabase();"]
    for i, k in enumerate(keys):
        m = pages[k]["mongo"]
        parts.append(f"""print('@@{i}');
try {{ db.c{i}.insertMany({m['docs']});
  db.c{i}.aggregate({m['pipeline']}).forEach(d => print(EJSON.stringify(d, {{relaxed: true}})));
}} catch (e) {{ print('@@ERR ' + e.message); }}""")
    p = subprocess.run(COMPOSE + ["exec", "-T", "mongo", "mongosh", "--quiet", "--eval", "\n".join(parts)],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    out, cur = {}, None
    for line in p.stdout.splitlines():
        if line.startswith("@@") and not line.startswith("@@ERR"):
            cur = keys[int(line[2:])]
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="substring of page keys to run")
    ap.add_argument("-c", "--check", action="store_true", help="fail if saidas.json differs from a fresh run")
    a = ap.parse_args()
    need("docker", "https://docs.docker.com/engine/install/")
    need("jq", "run: mise install")

    pages = load_pages(a.only)
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    new = dict(old) if a.only else {}
    errors = []
    mongo = run_mongo(pages)
    for key, ex in pages.items():
        res = {}
        try:
            res["entrada"], res["duckdb"] = run_duckdb(ex)
            res["postgres"] = None if na(ex["postgres"]) else run_postgres(ex)
            res["mongo"] = None if na(ex["mongo"]) else mongo.get(key)
            res["jq"] = None if na(ex["jq"]) else run_jq(ex)
        except Exception as e:  # report every broken page, not just the first
            errors.append(f"{key}: {e}")
            continue
        for engine in ("mongo",):
            if res[engine] is not None and "@@ERR" in res[engine]:
                errors.append(f"{key}: {engine}: {res[engine]}")
        new[key] = res
        print(f"ok  {key}")

    if errors:
        sys.exit("verify: failed\n  " + "\n  ".join(errors))
    if a.check:
        if new != old:
            stale = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
            sys.exit("verify: saidas.json is stale for: " + ", ".join(stale) + "\n  run: mise run verify")
        print("verify: saidas.json is up to date")
        return
    OUT.write_text(json.dumps(new, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"verify: wrote {len(new)} pages to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
