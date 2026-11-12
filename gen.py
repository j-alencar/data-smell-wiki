"""PROTOTYPE — generate both site variants from model.py + outputs.json.

  build/index.html            variant chooser
  build/classic/...           hand-rolled old-school wiki (variant A)
  starlight/src/content/docs  Starlight sources (variant B, built by astro)
"""
import json, shutil, html
from pathlib import Path
import markdown
from model import (CATS, TASKS, SMELLS, WORLDS, ARCHETYPAL, MIGRATES, UNPLACED,
                   EXAMPLES, HELPERS, NOTES, NON_RELATIONAL, ABEDJAN, slug)

BASE = "/smell-wiki-prototype"
ROOT = Path(__file__).parent
OUT = json.load(open(ROOT / "outputs.json"))
BUILD = ROOT / "build"
DOCS = ROOT / "starlight/src/content/docs"


# ---------- page inventory ----------
def world_smells(w):
    return [(s, False) for s in WORLDS[w][2]] + [(s, True) for s in ARCHETYPAL]

PAGES = {"": ("Smell tree", None), "non-relational": ("Non-relational data", None)}
for w in WORLDS:
    for s, _ in world_smells(w):
        PAGES[f"{w}/{slug(s)}"] = (s, (w, s))
for t, v in TASKS.items():
    PAGES[f"tasks/{t}"] = (v[0], None)


class Linker:
    def __init__(self, variant, here):
        self.variant, self.here = variant, here

    def __call__(self, path):
        if self.variant == "starlight":
            return f"{BASE}/starlight/{path + '/' if path else ''}"
        depth = self.here.count("/")
        return "../" * depth + (path or "index") + ".html"

    def other(self):
        if self.variant == "starlight":
            return f"{BASE}/classic/{self.here or 'index'}.html"
        return f"{BASE}/starlight/{self.here + '/' if self.here else ''}"


# ---------- markdown pieces ----------
def md_table(cols, rows):
    out = "| " + " | ".join(f"`{c}`" for c in cols) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows:
        out += "| " + " | ".join(f"`{v}`" for v in r) + " |\n"
    return out


def fence(lang, code):
    return f"```{lang}\n{code}\n```\n"


def cat_badge(code):
    name, _ = CATS[code]
    return f'<span class="cat c-{code}">{html.escape(name)}</span>'


def tree_html(L):
    filters = "".join(
        f'<label class="c-{c}"><input type="checkbox" id="f-{c}" checked> {html.escape(n)}</label> '
        for c, (n, _) in CATS.items())
    parts = ['<div class="smell-tree">',
             f'<fieldset class="filters"><legend>Data Smell type</legend>{filters}</fieldset>']
    for w, (label, question, _) in WORLDS.items():
        parts.append(f'<details class="world" open><summary><b>{label}</b> — <i>{question}</i></summary><ul>')
        def li(s, arch):
            cat, _, _, tasks = SMELLS[s]
            done = (w, s) in EXAMPLES
            cls = "" if done else ' class="stub" title="no worked example yet"'
            extra = ""
            if arch and s in MIGRATES and w != "text":
                extra = f' <a class="migr" href="{L("text/" + slug(s))}">→ may migrate to Text</a>'
            tnames = " · ".join(TASKS[t][0].split(" (")[0] for t in tasks)
            star = " ★" if done else ""
            return (f'<li class="smell c-{cat}"><a{cls} href="{L(w + "/" + slug(s))}">{s}</a>{star}'
                    f' <small>{tnames}</small>{extra}</li>')
        for s in WORLDS[w][2]:
            parts.append(li(s, False))
        parts.append('<li class="arch"><span>Archetypal smells</span><ul>')
        for s in ARCHETYPAL:
            parts.append(li(s, True))
        parts.append("</ul></li></ul></details>")
    parts.append("</div>")
    return "\n".join(parts)


def page_index(L):
    unplaced = ", ".join(UNPLACED)
    return f"""Coming from a field? Start from the world it seemingly belongs to, pick a smell, and follow the link to its tailored profiling page.

{tree_html(L)}

★ = worked example (SQL, MongoDB, jq). <span class="stub">Red links</span> are stubs that have the task list but no example yet. Smells in *Archetypal smells* can show up in any world.

**Not yet placed in a world:** {unplaced}.

See also: [Non-relational data]({L("non-relational")}).
"""


def page_smell(L, w, s):
    cat, definition, dsrc, tasks = SMELLS[s]
    wlabel = WORLDS[w][0]
    arch = s in ARCHETYPAL
    md = f'<p class="meta">{cat_badge(cat)} · World: <b>{wlabel}</b>{" · Archetypal smell" if arch else ""}</p>\n\n'
    if definition:
        md += f"> {definition}\n>\n> — {dsrc}\n\n"
    else:
        md += "> *Definition pending: not in the rb-data-smell-detection docstrings; see Foidl's online catalogue.*\n\n"
    ex = EXAMPLES.get((w, s))
    note = (ex or {}).get("note") or NOTES.get((w, s))
    if note:
        md += f"**In the {wlabel} world.** {note}\n\n"
    if arch and s in MIGRATES and w != "text":
        md += f"This smell may migrate the field to the [Text world]({L('text/' + slug(s))}).\n\n"
    if arch:
        others = [f"[{WORLDS[o][0]}]({L(o + '/' + slug(s))})" for o in WORLDS if o != w]
        md += f"**Also in:** {' · '.join(others)}\n\n"

    md += "## Profiling tasks\n\n| Task | Abedjan category | Scope |\n|---|---|---|\n"
    for t in tasks:
        name, acat, scope, _, _ = TASKS[t]
        star = " ★" if ex and ex["task"] == t else ""
        md += f"| [{name}]({L('tasks/' + t)}){star} | {acat} | {scope} |\n"
    md += "\n"

    if not ex:
        md += "## Worked example\n\n*None yet (stub).*\n"
        return md

    o = OUT[f"{w}|{s}"]
    tname = TASKS[ex["task"]][0]
    uses_pattern = "pattern(" in ex["sql"]["query"] + ex["mongo"]["pipeline"] + ex["jq"]["filter"]
    helper = (f"Uses the `pattern` helper from [patterns]({L('tasks/patterns')}).\n\n" if uses_pattern else "")
    md += f"## Worked example: {tname}\n\n{helper}"
    md += "### SQL (DuckDB)\n\n**Input**\n\n" + md_table(*o["sql_input"]) + "\n"
    md += "**Query**\n\n" + fence("sql", ex["sql"]["query"]) + "\n**Output**\n\n" + md_table(*o["sql_output"]) + "\n"
    md += "### MongoDB (document store)\n\n**Documents**\n\n" + fence("js", ex["mongo"]["docs"])
    md += "\n**Pipeline**\n\n" + fence("js", ex["mongo"]["pipeline"]) + "\n**Output**\n\n" + fence("json", o["mongo_output"])
    flag = " (`jq -s`, input is NDJSON)" if ex["jq"].get("slurp") else ""
    md += f"\n### jq (JSON documents){flag}\n\n**Input**\n\n" + fence("json", ex["jq"]["input"])
    md += "\n**Filter**\n\n" + fence("txt", ex["jq"]["filter"]) + "\n**Output**\n\n" + fence("json", o["jq_output"])
    md += f"\n## Reading the result\n\n{ex['reading']}\n\n## Sources\n\n"
    md += "".join(f"- {x}\n" for x in ex["sources"])
    md += "- Outputs above are real runs: DuckDB, MongoDB 7, jq (`verify.py`).\n"
    return md


def page_task(L, t):
    name, acat, scope, desc, where = TASKS[t]
    md = f"<p class=\"meta\">{acat} · {scope}</p>\n\n> {desc}\n>\n> — {ABEDJAN}, {where}\n\n"
    if t in HELPERS:
        h = HELPERS[t]
        md += "## Helpers\n\nThe tailored examples call these.\n\n**SQL (DuckDB)**\n\n" + fence("sql", h["sql"])
        md += "\n**MongoDB (mongosh)**\n\n" + fence("js", h["mongo"]) + "\n**jq**\n\n" + fence("txt", h["jq"]) + "\n"
    md += "## Tailored pages\n\n"
    for w, (wl, _, _) in WORLDS.items():
        users = [s for s, _ in world_smells(w) if t in SMELLS[s][3]]
        if users:
            links = []
            for s in users:
                star = " ★" if (w, s) in EXAMPLES and EXAMPLES[(w, s)]["task"] == t else ""
                links.append(f"[{s}]({L(w + '/' + slug(s))}){star}")
            md += f"- **{wl}:** " + " · ".join(links) + "\n"
    return md


def page_nonrel(L):
    return f"""{NON_RELATIONAL}

— Framework author

The worked examples show this. The [Integer as String]({L('numeric/integer-as-string')}) example finds `qty` inside an array of objects, and the [text Unit Inconsistency]({L('text/unit-inconsistency')}) example reads `maxspeed` from GeoJSON feature properties.
"""


def body(L, path):
    if path == "":
        return page_index(L)
    if path == "non-relational":
        return page_nonrel(L)
    if path.startswith("tasks/"):
        return page_task(L, path[6:])
    w, _ = path.split("/")
    return page_smell(L, w, PAGES[path][0])


def variant_bar(L):
    if L.variant == "classic":
        return f'<div class="vbar">PROTOTYPE · variant: <b>classic</b> | <a href="{L.other()}">starlight</a></div>'
    return f'<div class="vbar">PROTOTYPE · variant: <a href="{L.other()}">classic</a> | <b>starlight</b></div>'


# ---------- classic ----------
CLASSIC_TPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Data Smell Wiki</title>
<link rel="stylesheet" href="{css}"></head>
<body>
<div id="side">
<div id="logo"><a href="{home}">Data&nbsp;Smell<br>Wiki</a></div>
<div class="portlet"><h3>navigation</h3><ul>
<li><a href="{home}">Smell tree</a></li>
<li><a href="{nonrel}">Non-relational data</a></li></ul></div>
<div class="portlet"><h3>profiling tasks</h3><ul>{tasks}</ul></div>
</div>
<div id="content">
<div id="crumbs">{crumbs}</div>
<h1>{title}</h1>
{body}
<div id="foot">Prototype. Mapping from the TCC framework tree (Foidl et al. 2022 × Abedjan et al. 2015). Generated by <code>gen.py</code>.</div>
</div>
{vbar}
</body></html>"""


def build_classic():
    out = BUILD / "classic"
    shutil.rmtree(out, ignore_errors=True)
    for path, (title, ws) in PAGES.items():
        L = Linker("classic", path)
        html_body = markdown.markdown(body(L, path), extensions=["tables", "fenced_code"])
        crumbs = f'<a href="{L("")}">Smell tree</a>'
        if ws:
            crumbs += f" › {WORLDS[ws[0]][0]} › {title}"
        elif path.startswith("tasks/"):
            crumbs += f" › Profiling tasks › {title}"
        elif path:
            crumbs += f" › {title}"
        tasks = "".join(f'<li><a href="{L("tasks/" + t)}">{v[0].split(" (")[0]}</a></li>' for t, v in TASKS.items())
        page = CLASSIC_TPL.format(title=html.escape(title), css=L("style").replace(".html", ".css"),
                                  home=L(""), nonrel=L("non-relational"), tasks=tasks, crumbs=crumbs,
                                  body=html_body, vbar=variant_bar(L))
        f = out / ((path or "index") + ".html")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(page)
    shutil.copy(ROOT / "classic.css", out / "style.css")


# ---------- starlight ----------
def build_starlight():
    shutil.rmtree(DOCS, ignore_errors=True)
    order = {}
    for w in WORLDS:
        for i, (s, _) in enumerate(world_smells(w)):
            order[f"{w}/{slug(s)}"] = i
    for path, (title, ws) in PAGES.items():
        L = Linker("starlight", path)
        fm = [f"title: {json.dumps(title)}"]
        if path in order:
            fm.append(f"sidebar:\n  order: {order[path]}")
            if ws and ws in EXAMPLES:
                fm.append("  badge: ★")
        if path == "":
            fm.append("tableOfContents: false")
        text = "---\n" + "\n".join(fm) + "\n---\n\n" + body(L, path) + "\n\n" + variant_bar(L) + "\n"
        f = DOCS / ((path or "index") + ".md")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)


def build_root():
    BUILD.mkdir(exist_ok=True)
    (BUILD / "index.html").write_text(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Data Smell Wiki — prototype</title></head>
<body style="font-family:sans-serif;max-width:40em;margin:3em auto;padding:0 1em;line-height:1.5">
<h1>Data Smell Wiki (prototype)</h1>
<p>The same content rendered two ways. Question: <i>what should the framework's tree look like as a wiki?</i></p>
<ul>
<li><a href="classic/index.html"><b>A: classic</b></a>: hand-rolled HTML with an old-school wiki look and no JavaScript.</li>
<li><a href="starlight/"><b>B: starlight</b></a>: Astro Starlight with search, sidebar and dark mode.</li>
</ul>
<p>Both variants have a bar at the bottom that switches to the same page in the other variant.</p>
</body></html>""")


if __name__ == "__main__":
    build_root()
    build_classic()
    build_starlight()
    print(f"{len(PAGES)} pages, {len(EXAMPLES)} worked examples")
