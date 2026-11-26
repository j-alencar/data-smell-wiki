---
exemplos:
  - id: outliers
    titulo: cercas de Tukey, z-score e MAD
    sql: |
      CREATE TABLE requests (id int, ms int);
      INSERT INTO requests VALUES
        (1, 12), (2, 15), (3, 18), (4, 22), (5, 25), (6, 31), (7, 45), (8, 60), (9, 480);
    duckdb: |
      WITH s AS (SELECT quantile_cont(ms, 0.25) AS q1, quantile_cont(ms, 0.75) AS q3,
                        avg(ms) AS mean, stddev_samp(ms) AS sd, median(ms) AS med
                 FROM requests),
      m AS (SELECT median(abs(ms - med)) AS mad FROM requests, s)
      SELECT ms,
             CASE WHEN ms < q1 - 3 * (q3 - q1) OR ms > q3 + 3 * (q3 - q1) THEN 'extreme'
                  WHEN ms < q1 - 1.5 * (q3 - q1) OR ms > q3 + 1.5 * (q3 - q1) THEN 'mild'
                  ELSE '-' END AS tukey,
             round((ms - mean) / sd, 2) AS z,
             round(0.6745 * (ms - med) / mad, 2) AS mod_z
      FROM requests, s, m
      ORDER BY ms;
    postgres: |
      WITH s AS (SELECT percentile_cont(0.25) WITHIN GROUP (ORDER BY ms) AS q1,
                        percentile_cont(0.75) WITHIN GROUP (ORDER BY ms) AS q3,
                        avg(ms) AS mean, stddev_samp(ms) AS sd,
                        percentile_cont(0.5) WITHIN GROUP (ORDER BY ms) AS med
                 FROM requests),
      m AS (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(ms - med)) AS mad FROM requests, s)
      SELECT ms,
             CASE WHEN ms < q1 - 3 * (q3 - q1) OR ms > q3 + 3 * (q3 - q1) THEN 'extreme'
                  WHEN ms < q1 - 1.5 * (q3 - q1) OR ms > q3 + 1.5 * (q3 - q1) THEN 'mild'
                  ELSE '-' END AS tukey,
             round((ms - mean) / sd, 2) AS z,
             round((0.6745 * (ms - med) / mad)::numeric, 2) AS mod_z
      FROM requests, s, m
      ORDER BY ms;
    mongo:
      docs: |
        [12, 15, 18, 22, 25, 31, 45, 60, 480].map((v, i) => ({ _id: i + 1, ms: v }))
      pipeline: |
        [
          { $group: { _id: null, vs: { $push: "$ms" }, mean: { $avg: "$ms" }, sd: { $stdDevSamp: "$ms" },
              q: { $percentile: { input: "$ms", p: [0.25, 0.5, 0.75], method: "approximate" } } } },
          { $set: { q1: { $arrayElemAt: ["$q", 0] }, med: { $arrayElemAt: ["$q", 1] }, q3: { $arrayElemAt: ["$q", 2] } } },
          { $set: { iqr: { $subtract: ["$q3", "$q1"] },
              mad: { $median: { input: { $map: { input: "$vs", in: { $abs: { $subtract: ["$$this", "$med"] } } } },
                                method: "approximate" } } } },
          { $unwind: "$vs" },
          { $project: { _id: 0, ms: "$vs",
              tukey: { $switch: { branches: [
                { case: { $or: [{ $lt: ["$vs", { $subtract: ["$q1", { $multiply: [3, "$iqr"] }] }] },
                                { $gt: ["$vs", { $add: ["$q3", { $multiply: [3, "$iqr"] }] }] }] }, then: "extreme" },
                { case: { $or: [{ $lt: ["$vs", { $subtract: ["$q1", { $multiply: [1.5, "$iqr"] }] }] },
                                { $gt: ["$vs", { $add: ["$q3", { $multiply: [1.5, "$iqr"] }] }] }] }, then: "mild" } ],
                default: "-" } },
              z: { $round: [{ $divide: [{ $subtract: ["$vs", "$mean"] }, "$sd"] }, 2] },
              mod_z: { $round: [{ $divide: [{ $multiply: [0.6745, { $subtract: ["$vs", "$med"] }] }, "$mad"] }, 2] } } },
          { $sort: { ms: 1 } }
        ]
    jq:
      entrada: |
        [12, 15, 18, 22, 25, 31, 45, 60, 480]
      filtro: |
        def q(p): sort as $s | (length - 1) * p | floor as $i | (. - $i) as $f
                  | $s[$i] + $f * (($s[$i + 1] // $s[$i]) - $s[$i]);
        def r2: . * 100 | round / 100;
        . as $v | length as $n | q(0.25) as $q1 | q(0.75) as $q3 | ($q3 - $q1) as $iqr
        | q(0.5) as $med | (add / $n) as $mean
        | (map(pow(. - $mean; 2)) | add / ($n - 1) | sqrt) as $sd
        | (map(. - $med | fabs) | q(0.5)) as $mad
        | sort[]
        | {ms: .,
           tukey: (if . < $q1 - 3 * $iqr or . > $q3 + 3 * $iqr then "extreme"
                   elif . < $q1 - 1.5 * $iqr or . > $q3 + 1.5 * $iqr then "mild" else "-" end),
           z: ((. - $mean) / $sd | r2),
           mod_z: (0.6745 * (. - $med) / $mad | r2)}
    leitura: >-
      As cercas de Tukey marcam 480 como outlier extremo, e o z-score modificado dá 30,69, muito
      acima de 3,5. O z-score clássico dá só 2,65 e não passa do corte usual de 3: o próprio 480 infla
      a média e o desvio padrão. Com n = 9, nenhum valor pode passar de (n − 1)/√n ≈ 2,67.
  - id: k-means
    titulo: k-means com k = 3
    sql: |
      CREATE TABLE parcels (id int, kg double precision);
      INSERT INTO parcels VALUES
        (1, 0.9), (2, 1.0), (3, 1.1), (4, 1.2), (5, 4.8), (6, 5.0), (7, 5.1), (8, 5.3), (9, 48);
    duckdb: |
      WITH RECURSIVE k(it, c1, c2, c3) AS (
        SELECT 0, min(kg), quantile_disc(kg, 0.5), max(kg) FROM parcels
        UNION ALL
        SELECT it + 1, a.c1, a.c2, a.c3
        FROM k, LATERAL (
          SELECT avg(kg) FILTER (WHERE cl = 1) AS c1, avg(kg) FILTER (WHERE cl = 2) AS c2,
                 avg(kg) FILTER (WHERE cl = 3) AS c3
          FROM (SELECT kg, CASE WHEN abs(kg - k.c1) <= least(abs(kg - k.c2), abs(kg - k.c3)) THEN 1
                                WHEN abs(kg - k.c2) <= abs(kg - k.c3) THEN 2 ELSE 3 END AS cl
                FROM parcels)) a
        WHERE it < 5),
      c AS (SELECT * FROM k ORDER BY it DESC LIMIT 1)
      SELECT cl AS cluster, round(any_value(CASE cl WHEN 1 THEN c1 WHEN 2 THEN c2 ELSE c3 END), 2) AS centroid,
             count(*) AS n, string_agg(CAST(kg AS text), ', ' ORDER BY kg) AS members
      FROM (SELECT kg, c1, c2, c3,
                   CASE WHEN abs(kg - c1) <= least(abs(kg - c2), abs(kg - c3)) THEN 1
                        WHEN abs(kg - c2) <= abs(kg - c3) THEN 2 ELSE 3 END AS cl
            FROM parcels, c)
      GROUP BY cl
      ORDER BY cl;
    postgres: |
      WITH RECURSIVE k(it, c1, c2, c3) AS (
        SELECT 0, min(kg), percentile_disc(0.5) WITHIN GROUP (ORDER BY kg), max(kg) FROM parcels
        UNION ALL
        SELECT it + 1, a.c1, a.c2, a.c3
        FROM k, LATERAL (
          SELECT avg(kg) FILTER (WHERE cl = 1) AS c1, avg(kg) FILTER (WHERE cl = 2) AS c2,
                 avg(kg) FILTER (WHERE cl = 3) AS c3
          FROM (SELECT kg, CASE WHEN abs(kg - k.c1) <= least(abs(kg - k.c2), abs(kg - k.c3)) THEN 1
                                WHEN abs(kg - k.c2) <= abs(kg - k.c3) THEN 2 ELSE 3 END AS cl
                FROM parcels) p) a
        WHERE it < 5),
      c AS (SELECT * FROM k ORDER BY it DESC LIMIT 1)
      SELECT cl AS cluster, round(min(CASE cl WHEN 1 THEN c1 WHEN 2 THEN c2 ELSE c3 END)::numeric, 2) AS centroid,
             count(*) AS n, string_agg(CAST(kg AS text), ', ' ORDER BY kg) AS members
      FROM (SELECT kg, c1, c2, c3,
                   CASE WHEN abs(kg - c1) <= least(abs(kg - c2), abs(kg - c3)) THEN 1
                        WHEN abs(kg - c2) <= abs(kg - c3) THEN 2 ELSE 3 END AS cl
            FROM parcels, c) p
      GROUP BY cl
      ORDER BY cl;
    mongo:
      docs: |
        [0.9, 1.0, 1.1, 1.2, 4.8, 5.0, 5.1, 5.3, 48].map((v, i) => ({ _id: i + 1, kg: v }))
      pipeline: |
        [
          { $group: { _id: null, vs: { $push: "$kg" }, lo: { $min: "$kg" }, hi: { $max: "$kg" },
              med: { $median: { input: "$kg", method: "approximate" } } } },
          { $set: { c: { $reduce: { input: { $range: [0, 5] }, initialValue: ["$lo", "$med", "$hi"], in: {
              $let: { vars: { cs: "$$value" }, in: { $map: { input: [0, 1, 2], as: "i", in: { $avg: {
                $filter: { input: "$vs", as: "v", cond: { $eq: ["$$i", { $let: {
                  vars: { d: { $map: { input: "$$cs", as: "ci", in: { $abs: { $subtract: ["$$v", "$$ci"] } } } } },
                  in: { $indexOfArray: ["$$d", { $min: "$$d" }] } } }] } } } } } } } } } } } },
          { $unwind: "$vs" },
          { $set: { cl: { $let: { vars: { d: { $map: { input: "$c", as: "ci", in: { $abs: { $subtract: ["$vs", "$$ci"] } } } } },
              in: { $add: [{ $indexOfArray: ["$$d", { $min: "$$d" }] }, 1] } } } } },
          { $sort: { vs: 1 } },
          { $group: { _id: "$cl", centroid: { $first: { $arrayElemAt: ["$c", { $subtract: ["$cl", 1] }] } },
              n: { $sum: 1 }, members: { $push: "$vs" } } },
          { $project: { _id: 0, cluster: "$_id", centroid: { $round: ["$centroid", 2] }, n: "$n", members: "$members" } },
          { $sort: { cluster: 1 } }
        ]
    jq:
      entrada: |
        [0.9, 1.0, 1.1, 1.2, 4.8, 5.0, 5.1, 5.3, 48]
      filtro: |
        def nearest($cs): . as $v | [$cs[] | . - $v | fabs] | index(min);
        sort as $v
        | reduce range(5) as $_ ([$v[0], $v[$v | length / 2 | floor], $v[-1]];
            . as $cs | [range(3) as $i | [$v[] | select(nearest($cs) == $i)] | add / length])
        | . as $c
        | $v | group_by(nearest($c))
        | map((.[0] | nearest($c)) as $i
              | {cluster: ($i + 1), centroid: ($c[$i] * 100 | round / 100), n: length, members: .})[]
    leitura: >-
      Com centroides iniciais no mínimo, na mediana e no máximo, o k-means converge para três grupos:
      pacotes de 1 kg, pacotes de 5 kg e um grupo de um único pacote de 48 kg. Um grupo com um só
      membro é um registro que não se encaixa em nenhum outro: candidato a outlier. Com k = 2, os grupos de 1 kg e 5 kg se fundiriam. A escolha de k e dos centroides iniciais muda o resultado.
  - id: aplicado
    smell: Synonym
    mundo: texto
    sql: |
      CREATE TABLE people (id int, name text);
      INSERT INTO people VALUES
        (1, 'Bill Clinton'), (2, 'President Clinton'), (3, 'William Jefferson Clinton'), (4, 'Hillary Clinton'),
        (5, 'George Bush'), (6, 'President Bush'), (7, 'George W. Bush');
    duckdb: |
      SELECT lower(string_split(name, ' ')[-1]) AS key, count(*) AS n,
             string_agg(name, ' | ' ORDER BY name) AS members
      FROM people
      GROUP BY key
      ORDER BY n DESC, key;
    postgres: |
      SELECT lower(split_part(name, ' ', -1)) AS key, count(*) AS n,
             string_agg(name, ' | ' ORDER BY name) AS members
      FROM people
      GROUP BY key
      ORDER BY n DESC, key;
    mongo:
      docs: |
        ["Bill Clinton", "President Clinton", "William Jefferson Clinton", "Hillary Clinton",
         "George Bush", "President Bush", "George W. Bush"].map((v, i) => ({ _id: i + 1, name: v }))
      pipeline: |
        [
          { $sort: { name: 1 } },
          { $group: { _id: { $toLower: { $arrayElemAt: [{ $split: ["$name", " "] }, -1] } },
              n: { $sum: 1 }, members: { $push: "$name" } } },
          { $sort: { n: -1, _id: 1 } },
          { $project: { _id: 0, key: "$_id", n: "$n", members: "$members" } }
        ]
    jq:
      entrada: |
        ["Bill Clinton", "President Clinton", "William Jefferson Clinton", "Hillary Clinton",
         "George Bush", "President Bush", "George W. Bush"]
      filtro: |
        group_by(split(" ")[-1] | ascii_downcase)
        | map({key: (.[0] | split(" ")[-1] | ascii_downcase), n: length, members: sort})
        | sort_by([-.n, .key])[]
    leitura: >-
      A chave (último nome, em minúsculas) agrupa as grafias em dois grupos, candidatos a sinônimos.
      O grupo `clinton` mistura duas pessoas: Hillary Clinton não é sinônimo de Bill Clinton.
      O agrupamento só propõe candidatos, porque confirmar que valores diferentes nomeiam a mesma coisa exige conhecer o
      domínio.
---
Agrupe registros semelhantes e examine os grupos pequenos ou distantes: podem indicar valores suspeitos.[@abedjan2015]

<h2 id="outliers">Detecção de outliers</h2>

Os exemplos usam estes critérios:

- **Cercas de Tukey:** com os [quartis](/tarefas/quartiles/) Q1 e Q3 e o intervalo interquartil IQ = Q3 − Q1, as cercas internas ficam em Q1 − 1,5·IQ e Q3 + 1,5·IQ, e as externas em Q1 − 3·IQ e Q3 + 3·IQ. Um ponto além de uma cerca interna é um outlier leve; além de uma externa, extremo.[@nist-handbook]
- **Z-score:** *z* = (*x* − média) / desvio padrão. É prática comum, mas pode enganar, sobretudo em amostras pequenas: o maior *z* possível é (*n* − 1)/√*n*.[@nist-handbook]
- **MAD:** o z-score modificado é *M* = 0,6745·(*x* − mediana) / MAD, em que MAD é o desvio absoluto mediano. |*M*| > 3,5 indica outlier potencial. O MAD resiste melhor a valores extremos que o desvio padrão.[@nist-handbook]
- **k-means:** agrupa os valores em *k* grupos em torno de centroides. Um grupo pequeno e distante, ou um ponto longe do próprio centroide, é candidato a outlier.[@jain1999]

No exemplo de nomes, a chave normalizada forma grupos que ainda precisam de confirmação: o mesmo sobrenome não garante que os valores sejam sinônimos.
