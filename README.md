# Data Smell Wiki

Navigation guide for a framework that maps data smells (Foidl, Felderer and Ramler, 2022) to data profiling tasks (Abedjan, Golab and Naumann, 2015). Site language: PT-BR.

Live: https://j-alencar.github.io/data-smell-wiki/

## Required toolchain

- [mise](https://mise.jdx.dev/installing-mise.html) (installs Node, Python and jq)
- [Docker](https://docs.docker.com/engine/install/) with Compose (runs PostgreSQL and MongoDB)

## Run

```sh
mise install && mise run setup
mise run dev        # http://localhost:8080/data-smell-wiki/
```

## Add or change a smell page

Each page is a Markdown file: `src/<mundo>/<smell-slug>.md`. The frontmatter holds the example and the body holds the world-specific note. Copy any existing page as a template.

```sh
mise run verify -- texto/casing   # run one page's example on DuckDB, PostgreSQL, MongoDB, jq
mise run verify                   # run all; writes src/_data/saidas.json
```

Pages render the outputs from `saidas.json`, so the site only shows real runs. CI fails if that file is stale. If an engine can't do a task, replace its block with `na: "<motivo>"`.

| Data | File |
|---|---|
| Smells (definition, type, tasks) | `src/_data/smells.yaml` |
| Worlds and archetypal smells | `src/_data/mundos.yaml` |
| Profiling tasks | `src/_data/tarefas.yaml` |
| ABNT references | `src/_data/referencias.yaml` |
| `pattern()` helper per engine | `helpers/` |

```sh
mise tasks          # all tasks
```
