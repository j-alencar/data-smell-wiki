"""PROTOTYPE — run every example on real engines, write outputs.json.

Needs: duckdb (pip), jq, docker. The site shows outputs.json, so canned
outputs are always real execution results.
"""
import json, subprocess, tempfile, os, time
import duckdb
from model import EXAMPLES, HELPERS

out = {}
keys = list(EXAMPLES)

# --- SQL (DuckDB) ---
for k in keys:
    e = EXAMPLES[k]
    con = duckdb.connect()
    con.execute(HELPERS["patterns"]["sql"])
    con.execute(e["sql"]["setup"])
    inp_name = e["sql"]["setup"].split()[2]
    r = con.execute(f"SELECT * FROM {inp_name}")
    inp = ([d[0] for d in r.description], [[str(v) for v in row] for row in r.fetchall()])
    r = con.execute(e["sql"]["query"])
    res = ([d[0] for d in r.description], [[str(v) for v in row] for row in r.fetchall()])
    out["|".join(k)] = {"sql_input": inp, "sql_output": res}

# --- jq ---
helper = HELPERS["patterns"]["jq"]
for k in keys:
    j = EXAMPLES[k]["jq"]
    args = ["jq", "-c"] + (["-s"] if j.get("slurp") else []) + [helper + "\n" + j["filter"]]
    p = subprocess.run(args, input=j["input"], capture_output=True, text=True, check=True)
    out["|".join(k)]["jq_output"] = p.stdout.strip()

# --- MongoDB 7 in docker ---
name = "smellwiki-proto-mongo"
subprocess.run(["docker", "rm", "-f", name], capture_output=True)
subprocess.run(["docker", "run", "-d", "--name", name, "mongo:7"], check=True, capture_output=True)
try:
    for _ in range(60):
        if subprocess.run(["docker", "exec", name, "mongosh", "--quiet", "--eval", "db.runCommand({ping:1}).ok"],
                          capture_output=True, text=True).stdout.strip() == "1":
            break
        time.sleep(1)
    script = [HELPERS["patterns"]["mongo"], "db = db.getSiblingDB('proto');"]
    for i, k in enumerate(keys):
        m = EXAMPLES[k]["mongo"]
        script.append(f"""db.c{i}.drop(); db.c{i}.insertMany({m['docs']});
print('@@{i}'); db.c{i}.aggregate({m['pipeline']}).forEach(d => print(EJSON.stringify(d, {{relaxed: true}})));""")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write("\n".join(script))
    subprocess.run(["docker", "cp", f.name, f"{name}:/s.js"], check=True)
    os.unlink(f.name)
    p = subprocess.run(["docker", "exec", name, "mongosh", "--quiet", "/s.js"], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stdout + p.stderr)
    cur = None
    buf = {}
    for line in p.stdout.splitlines():
        if line.startswith("@@"):
            cur = int(line[2:]); buf[cur] = []
        elif cur is not None:
            buf[cur].append(line)
    for i, k in enumerate(keys):
        out["|".join(k)]["mongo_output"] = "\n".join(buf[i])
finally:
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)

json.dump(out, open("outputs.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items():
    print("==", k)
    print("  sql:", v["sql_output"])
    print("  mongo:", v["mongo_output"].replace("\n", " | "))
    print("  jq:", v["jq_output"].replace("\n", " | "))
