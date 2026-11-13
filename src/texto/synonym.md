---
smell: Synonym
exemplo:
  tarefa: summaries-sketches
  sql: |
    CREATE TABLE people (id int, name text);
    INSERT INTO people VALUES
      (1, 'Bill Clinton'), (2, 'President Clinton'), (3, 'William Jefferson Clinton'), (4, 'George Bush');
  duckdb: |
    WITH t AS (SELECT name, string_split(name, ' ') AS tok FROM people)
    SELECT a.name AS a, b.name AS b,
           round(len(list_intersect(a.tok, b.tok))
                 / len(list_distinct(list_concat(a.tok, b.tok))), 2) AS jaccard
    FROM t a JOIN t b ON a.name < b.name
    WHERE len(list_intersect(a.tok, b.tok)) > 0
    ORDER BY jaccard DESC, a, b;
  postgres: |
    WITH t AS (SELECT name, string_to_array(name, ' ') AS tok FROM people)
    SELECT a.name AS a, b.name AS b,
           round(cardinality(ARRAY(SELECT unnest(a.tok) INTERSECT SELECT unnest(b.tok)))::numeric
                 / cardinality(ARRAY(SELECT unnest(a.tok) UNION SELECT unnest(b.tok))), 2) AS jaccard
    FROM t a JOIN t b ON a.name < b.name
    WHERE a.tok && b.tok
    ORDER BY jaccard DESC, a, b;
  mongo:
    docs: |
      [
        { _id: 1, name: "Bill Clinton" }, { _id: 2, name: "President Clinton" },
        { _id: 3, name: "William Jefferson Clinton" }, { _id: 4, name: "George Bush" }
      ]
    pipeline: |
      [
        { $group: { _id: null, xs: { $push: { name: "$name", tok: { $split: ["$name", " "] } } } } },
        { $project: { a: "$xs", b: "$xs" } }, { $unwind: "$a" }, { $unwind: "$b" },
        { $match: { $expr: { $lt: ["$a.name", "$b.name"] } } },
        { $project: { _id: 0, a: "$a.name", b: "$b.name",
            jaccard: { $round: [{ $divide: [
              { $size: { $setIntersection: ["$a.tok", "$b.tok"] } },
              { $size: { $setUnion: ["$a.tok", "$b.tok"] } }] }, 2] } } },
        { $match: { jaccard: { $gt: 0 } } },
        { $sort: { jaccard: -1, a: 1, b: 1 } }
      ]
  jq:
    entrada: |
      [{"name": "Bill Clinton"}, {"name": "President Clinton"},
       {"name": "William Jefferson Clinton"}, {"name": "George Bush"}]
    filtro: |
      [.[].name] as $n
      | [range(0; $n | length) as $i | range($i + 1; $n | length) as $j
         | [$n[$i], $n[$j]] | sort
         | (.[0] | split(" ")) as $ta | (.[1] | split(" ")) as $tb
         | {a: .[0], b: .[1],
            jaccard: (([$ta[] | select(IN($tb[]))] | unique | length)
                      / (($ta + $tb) | unique | length) * 100 | round / 100)}
         | select(.jaccard > 0)]
      | sort_by([-.jaccard, .a, .b])[]
  leitura: >-
    Os três "Clinton" se sobrepõem; "George Bush" não aparece em par nenhum. A similaridade só
    aponta candidatos: confirmar que são a mesma pessoa exige conhecer o domínio. Em escala,
    assinaturas MinHash estimam essa similaridade sem comparar todos os pares (ABEDJAN; GOLAB;
    NAUMANN, 2015).
---
Compare os valores dois a dois pela similaridade de Jaccard dos tokens. Pares parecidos e diferentes são candidatos a sinônimo.
