---
smell: Special Character Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE footnotes (id int, ref text);
    INSERT INTO footnotes VALUES (1, '(2)'), (2, '(44)'), (3, '[32]'), (4, '(32)');
  duckdb: |
    SELECT left(ref, 1) || right(ref, 1) AS brackets, count(*) AS n
    FROM footnotes
    GROUP BY 1
    ORDER BY n DESC;
  postgres: |
    SELECT left(ref, 1) || right(ref, 1) AS brackets, count(*) AS n
    FROM footnotes
    GROUP BY 1
    ORDER BY n DESC;
  mongo:
    docs: |
      [ { _id: 1, ref: "(2)" }, { _id: 2, ref: "(44)" }, { _id: 3, ref: "[32]" }, { _id: 4, ref: "(32)" } ]
    pipeline: |
      [
        { $group: { _id: { $concat: [
            { $substrCP: ["$ref", 0, 1] },
            { $substrCP: ["$ref", { $subtract: [{ $strLenCP: "$ref" }, 1] }, 1] }] },
          n: { $sum: 1 } } },
        { $sort: { n: -1 } }
      ]
  jq:
    entrada: |
      [{"ref": "(2)"}, {"ref": "(44)"}, {"ref": "[32]"}, {"ref": "(32)"}]
    filtro: |
      [.[].ref | .[0:1] + .[-1:]]
      | group_by(.) | map({brackets: .[0], n: length})
      | sort_by(-.n)[]
  leitura: Parênteses em três referências, colchetes em uma.
---
Isole os caracteres especiais que envolvem o valor e conte as variações.
