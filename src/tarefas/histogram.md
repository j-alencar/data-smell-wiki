---
exemplos:
  - id: equi-width
    titulo: faixas de mesma largura (equi-width)
    sql: |
      CREATE TABLE requests (id int, ms int);
      INSERT INTO requests VALUES
        (1, 12), (2, 15), (3, 18), (4, 22), (5, 25), (6, 31), (7, 45), (8, 60), (9, 120), (10, 480);
    duckdb: |
      WITH r AS (SELECT min(ms) AS lo, max(ms) AS hi, (max(ms) - min(ms)) / 4 AS w FROM requests)
      SELECT b AS bucket, lo + (b - 1) * w AS from_ms, lo + b * w AS to_ms, count(*) AS n
      FROM (SELECT least(floor((ms - lo) / w) + 1, 4)::int AS b, lo, w FROM requests, r)
      GROUP BY b, lo, w
      ORDER BY b;
    postgres: |
      WITH r AS (SELECT min(ms) AS lo, max(ms) AS hi, ((max(ms) - min(ms)) / 4.0)::float8 AS w FROM requests)
      SELECT b AS bucket, lo + (b - 1) * w AS from_ms, lo + b * w AS to_ms, count(*) AS n
      FROM (SELECT least(floor((ms - lo) / w) + 1, 4)::int AS b, lo, w FROM requests, r) t
      GROUP BY b, lo, w
      ORDER BY b;
    mongo:
      docs: |
        [12, 15, 18, 22, 25, 31, 45, 60, 120, 480].map((v, i) => ({ _id: i + 1, ms: v }))
      pipeline: |
        [
          { $setWindowFields: { output: { lo: { $min: "$ms" }, hi: { $max: "$ms" } } } },
          { $set: { w: { $divide: [{ $subtract: ["$hi", "$lo"] }, 4] } } },
          { $set: { b: { $min: [{ $add: [{ $floor: { $divide: [{ $subtract: ["$ms", "$lo"] }, "$w"] } }, 1] }, 4] } } },
          { $group: { _id: "$b", lo: { $first: "$lo" }, w: { $first: "$w" }, n: { $sum: 1 } } },
          { $project: { _id: 0, bucket: "$_id",
              from_ms: { $add: ["$lo", { $multiply: [{ $subtract: ["$_id", 1] }, "$w"] }] },
              to_ms: { $add: ["$lo", { $multiply: ["$_id", "$w"] }] }, n: "$n" } },
          { $sort: { bucket: 1 } }
        ]
    jq:
      entrada: |
        [12, 15, 18, 22, 25, 31, 45, 60, 120, 480]
      filtro: |
        min as $lo | ((max - $lo) / 4) as $w
        | map([((. - $lo) / $w | floor) + 1, 4] | min)
        | group_by(.)
        | map(.[0] as $b | {bucket: $b, from_ms: ($lo + ($b - 1) * $w), to_ms: ($lo + $b * $w), n: length})[]
    leitura: >-
      Nove dos dez valores caem na primeira faixa. As faixas 2 e 3 nem aparecem, porque estão vazias. Um único valor alto (480) estica a amplitude e esmaga o resto. Com cauda longa, a
      largura igual esconde a forma da distribuição.
  - id: equi-depth
    titulo: faixas com o mesmo número de valores (equi-depth)
    sql: |
      CREATE TABLE requests (id int, ms int);
      INSERT INTO requests VALUES
        (1, 12), (2, 15), (3, 18), (4, 22), (5, 25), (6, 31), (7, 45), (8, 60), (9, 120), (10, 480);
    duckdb: |
      SELECT bucket, min(ms) AS from_ms, max(ms) AS to_ms, count(*) AS n
      FROM (SELECT ms, ntile(4) OVER (ORDER BY ms) AS bucket FROM requests)
      GROUP BY bucket
      ORDER BY bucket;
    postgres: |
      SELECT bucket, min(ms) AS from_ms, max(ms) AS to_ms, count(*) AS n
      FROM (SELECT ms, ntile(4) OVER (ORDER BY ms) AS bucket FROM requests) t
      GROUP BY bucket
      ORDER BY bucket;
    mongo:
      docs: |
        [12, 15, 18, 22, 25, 31, 45, 60, 120, 480].map((v, i) => ({ _id: i + 1, ms: v }))
      pipeline: |
        [
          { $setWindowFields: { sortBy: { ms: 1 }, output: {
              r: { $documentNumber: {} }, n: { $count: {}, window: { documents: ["unbounded", "unbounded"] } } } } },
          { $set: { q: { $floor: { $divide: ["$n", 4] } }, rem: { $mod: ["$n", 4] } } },
          { $set: { bucket: { $cond: [
              { $lte: ["$r", { $multiply: ["$rem", { $add: ["$q", 1] }] }] },
              { $ceil: { $divide: ["$r", { $add: ["$q", 1] }] } },
              { $add: ["$rem", { $ceil: { $divide: [{ $subtract: ["$r", { $multiply: ["$rem", { $add: ["$q", 1] }] }] }, "$q"] } }] }] } } },
          { $group: { _id: "$bucket", from_ms: { $min: "$ms" }, to_ms: { $max: "$ms" }, n: { $sum: 1 } } },
          { $project: { _id: 0, bucket: "$_id", from_ms: "$from_ms", to_ms: "$to_ms", n: "$n" } },
          { $sort: { bucket: 1 } }
        ]
    jq:
      entrada: |
        [12, 15, 18, 22, 25, 31, 45, 60, 120, 480]
      filtro: |
        sort | length as $n | ($n / 4 | floor) as $q | ($n % 4) as $rem
        | [to_entries[] | (.key + 1) as $r
           | {ms: .value,
              bucket: (if $r <= $rem * ($q + 1) then ($r / ($q + 1) | ceil)
                       else $rem + (($r - $rem * ($q + 1)) / $q | ceil) end)}]
        | group_by(.bucket)
        | map({bucket: .[0].bucket, from_ms: .[0].ms, to_ms: .[-1].ms, n: length})[]
    leitura: >-
      Cada faixa tem 2 ou 3 valores, como `ntile` distribui o resto. Agora a forma aparece: as três
      primeiras faixas cabem em 12–45 ms, a última vai de 60 a 480 ms. Os limites das faixas são quantis, que com quatro faixas se chamam [quartis](/tarefas/quartiles/).
---
Um histograma conta os valores por grupo (faixa). O equi-depth fixa o número de valores por faixa e define os limites ordenando os valores, como os [quartis](/tarefas/quartiles/).[@abedjan2015]

Os exemplos usam 4 faixas sobre os mesmos 10 tempos de resposta, para comparar os dois tipos.
