# smell-wiki-prototype

**PROTOTYPE — throwaway.** It answers one question: *what should the data-smell → profiling framework tree look like as a wiki?*

Live: https://j-alencar.github.io/smell-wiki-prototype/

- `/classic/`: hand-rolled HTML with an old-school wiki skin and no JavaScript.
- `/starlight/`: Astro Starlight.

Both are generated from `model.py`. The tree starts from the field's world (Time-series / Numeric / Text). Each smell links to a tailored page, and each page links to base profiling-task pages. The tree is `<details>` plus CSS `:has()` filters by Foidl category, with no JS.

## Commands

```sh
python verify.py   # run every example on DuckDB, MongoDB 7 (docker), jq -> outputs.json
python gen.py      # build/classic + starlight/src/content/docs
cd starlight && npm ci && npm run build
```

Pages shows `outputs.json`, so every displayed output comes from a real run.

See `NOTES.md` for open questions and the verdict.
