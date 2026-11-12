# NOTES — prototype verdict

**Question:** what should the framework tree look like as a static wiki, starting from the field's world?

**Verdict:** _TBD by author_. Classic or Starlight? Keep the world-first model?

## Open questions surfaced while building

1. **Unplaced smells:** *Ambiguous Value* and *Integer as Floating-point Number* are in Foidl's catalogue but not in the sketch. Which world do they go in?
2. **Duplicates:** the sketch lists *Extraneous Value* and *Intermingled Data Type* both as time-series-specific and as archetypal. The prototype keeps them only as archetypal.
3. **Missing definitions:** *Suspect Precision* and *Precision Inconsistency* have no definition in the rb-data-smell-detection docstrings or in the CAIN'22 paper. The source would be Foidl's online catalogue (bit.ly/2WpPauB), which hasn't been checked.
4. **Engine-dependent patterns:** the same value 6215.0 yields `9999.99` in DuckDB (DECIMAL), `9999` in MongoDB and `9999.9` in jq. Pattern profiling has to stay within one engine.
5. **Coverage:** only 9 of 46 tailored pages have worked examples. The other 37 are stubs (red links).
