---
exemplos:
  - id: bernoulli
    titulo: amostra de Bernoulli
    sql: |
      CREATE TABLE sales (id int, region text, amount int);
      INSERT INTO sales VALUES
        (1, 'N', 95), (2, 'N', 110), (3, 'N', 100), (4, 'N', 120), (5, 'N', 90), (6, 'N', 105),
        (7, 'N', 115), (8, 'N', 98), (9, 'N', 102), (10, 'N', 108), (11, 'N', 93), (12, 'N', 112),
        (13, 'S', 300), (14, 'S', 280), (15, 'S', 320), (16, 'S', 310), (17, 'S', 290), (18, 'S', 330),
        (19, 'S', 270), (20, 'S', 305);
    duckdb: |
      SELECT count(*) AS n_sample,
             round(sum(amount) / 0.5, 1) AS est_sum,
             (SELECT sum(amount) FROM sales) AS exact_sum
      FROM sales
      WHERE (id * 2654435761) % 4294967296 < 0.5 * 4294967296;
    postgres: |
      SELECT count(*) AS n_sample,
             round(sum(amount) / 0.5, 1) AS est_sum,
             (SELECT sum(amount) FROM sales) AS exact_sum
      FROM sales
      WHERE (id * 2654435761) % 4294967296 < 0.5 * 4294967296;
    mongo:
      docs: |
        [95, 110, 100, 120, 90, 105, 115, 98, 102, 108, 93, 112, 300, 280, 320, 310, 290, 330, 270, 305]
          .map((v, i) => ({ _id: i + 1, region: i < 12 ? "N" : "S", amount: v }))
      pipeline: |
        [
          { $setWindowFields: { output: { exact_sum: { $sum: "$amount", window: { documents: ["unbounded", "unbounded"] } } } } },
          { $match: { $expr: { $lt: [{ $mod: [{ $multiply: ["$_id", 2654435761] }, 4294967296] }, 0.5 * 4294967296] } } },
          { $group: { _id: null, n_sample: { $sum: 1 }, s: { $sum: "$amount" }, exact_sum: { $first: "$exact_sum" } } },
          { $project: { _id: 0, n_sample: "$n_sample", est_sum: { $divide: ["$s", 0.5] }, exact_sum: "$exact_sum" } }
        ]
    jq:
      entrada: |
        [95, 110, 100, 120, 90, 105, 115, 98, 102, 108, 93, 112, 300, 280, 320, 310, 290, 330, 270, 305]
      filtro: |
        add as $exact
        | [to_entries[] | select(((.key + 1) * 2654435761) % 4294967296 < 0.5 * 4294967296) | .value]
        | {n_sample: length, est_sum: (add / 0.5), exact_sum: $exact}
    leitura: >-
      A moeda de cada linha é o hash do `id`: cara se cair na metade de baixo do intervalo, ou seja,
      p = 0,5. Saíram 10 linhas, e a soma da amostra dividida por p estima 3820 contra 3653 exatos
      (erro de 4,6%). O estimador é não enviesado, mas a amostra mistura valores perto de 100 e de
      300, e isso aumenta a variância.
  - id: estratificada
    titulo: amostra estratificada por região
    sql: |
      CREATE TABLE sales (id int, region text, amount int);
      INSERT INTO sales VALUES
        (1, 'N', 95), (2, 'N', 110), (3, 'N', 100), (4, 'N', 120), (5, 'N', 90), (6, 'N', 105),
        (7, 'N', 115), (8, 'N', 98), (9, 'N', 102), (10, 'N', 108), (11, 'N', 93), (12, 'N', 112),
        (13, 'S', 300), (14, 'S', 280), (15, 'S', 320), (16, 'S', 310), (17, 'S', 290), (18, 'S', 330),
        (19, 'S', 270), (20, 'S', 305);
    duckdb: |
      WITH r AS (
        SELECT *, row_number() OVER (PARTITION BY region ORDER BY (id * 2654435761) % 4294967296) AS rn,
                  count(*) OVER (PARTITION BY region) AS stratum_size,
                  sum(amount) OVER (PARTITION BY region) AS exact_sum
        FROM sales)
      SELECT region, max(stratum_size) AS stratum_size, count(*) AS n_sample,
             round(max(stratum_size) / count(*) * sum(amount), 1) AS est_sum, max(exact_sum) AS exact_sum
      FROM r
      WHERE rn <= 3
      GROUP BY region
      ORDER BY region;
    postgres: |
      WITH r AS (
        SELECT *, row_number() OVER (PARTITION BY region ORDER BY (id * 2654435761) % 4294967296) AS rn,
                  count(*) OVER (PARTITION BY region) AS stratum_size,
                  sum(amount) OVER (PARTITION BY region) AS exact_sum
        FROM sales)
      SELECT region, max(stratum_size) AS stratum_size, count(*) AS n_sample,
             round(max(stratum_size)::numeric / count(*) * sum(amount), 1) AS est_sum, max(exact_sum) AS exact_sum
      FROM r
      WHERE rn <= 3
      GROUP BY region
      ORDER BY region;
    mongo:
      docs: |
        [95, 110, 100, 120, 90, 105, 115, 98, 102, 108, 93, 112, 300, 280, 320, 310, 290, 330, 270, 305]
          .map((v, i) => ({ _id: i + 1, region: i < 12 ? "N" : "S", amount: v }))
      pipeline: |
        [
          { $set: { h: { $mod: [{ $multiply: ["$_id", 2654435761] }, 4294967296] } } },
          { $setWindowFields: { partitionBy: "$region", sortBy: { h: 1 }, output: {
              rn: { $documentNumber: {} },
              stratum_size: { $count: {}, window: { documents: ["unbounded", "unbounded"] } },
              exact_sum: { $sum: "$amount", window: { documents: ["unbounded", "unbounded"] } } } } },
          { $match: { rn: { $lte: 3 } } },
          { $group: { _id: "$region", stratum_size: { $first: "$stratum_size" }, n_sample: { $sum: 1 },
              s: { $sum: "$amount" }, exact_sum: { $first: "$exact_sum" } } },
          { $project: { _id: 0, region: "$_id", stratum_size: "$stratum_size", n_sample: "$n_sample",
              est_sum: { $round: [{ $multiply: [{ $divide: ["$stratum_size", "$n_sample"] }, "$s"] }, 1] },
              exact_sum: "$exact_sum" } },
          { $sort: { region: 1 } }
        ]
    jq:
      entrada: |
        [95, 110, 100, 120, 90, 105, 115, 98, 102, 108, 93, 112, 300, 280, 320, 310, 290, 330, 270, 305]
      filtro: |
        [to_entries[] | {id: (.key + 1), amount: .value, region: (if .key < 12 then "N" else "S" end)}]
        | group_by(.region)[]
        | (sort_by((.id * 2654435761) % 4294967296) | .[:3]) as $s
        | {region: .[0].region, stratum_size: length, n_sample: ($s | length),
           est_sum: (length / ($s | length) * ($s | map(.amount) | add) * 10 | round / 10),
           exact_sum: (map(.amount) | add)}
    leitura: >-
      Cada região (estrato) recebe uma amostra sem reposição de 3 linhas, e cada soma se estima com
      o peso do próprio estrato: 12/3 no Norte, 8/3 no Sul. Somadas, as estimativas dão 3765,3 contra
      3653 (erro de 3,1%) com 6 linhas, menos que as 10 da amostra de Bernoulli. Funciona porque cada
      estrato é homogêneo: valores perto de 100 no Norte e de 300 no Sul.
  - id: kmv
    titulo: sketch k Minimum Values (KMV) e similaridade de Jaccard
    sql: |
      CREATE TABLE cols AS
        SELECT 'A' AS col, array_agg(i ORDER BY i) AS vals FROM generate_series(1, 40) AS g(i)
        UNION ALL
        SELECT 'B', array_agg(i ORDER BY i) FROM generate_series(21, 60) AS g(i);
    duckdb: |
      WITH v AS (SELECT DISTINCT col, unnest(vals) AS x FROM cols),
      h AS (SELECT col, x, (y * y + 12345) % 67108859 AS hv
            FROM (SELECT col, x, (48271 * x::bigint + 11) % 67108859 AS y FROM v)),
      sk AS (SELECT * FROM (SELECT *, row_number() OVER (PARTITION BY col ORDER BY hv) AS rn FROM h)
             WHERE rn <= 16),
      u AS (SELECT x, count(*) AS in_both FROM sk GROUP BY x, hv ORDER BY hv LIMIT 16)
      SELECT (SELECT round(15 / (max(hv) / 67108859), 1) FROM sk WHERE col = 'A') AS est_distinct_a,
             (SELECT round(15 / (max(hv) / 67108859), 1) FROM sk WHERE col = 'B') AS est_distinct_b,
             round(avg((in_both = 2)::int), 2) AS est_jaccard,
             (SELECT round(count(*) FILTER (WHERE n = 2) / count(*), 2)
              FROM (SELECT x, count(*) AS n FROM v GROUP BY x)) AS exact_jaccard
      FROM u;
    postgres: |
      WITH v AS (SELECT DISTINCT col, unnest(vals) AS x FROM cols),
      h AS (SELECT col, x, (y * y + 12345) % 67108859 AS hv
            FROM (SELECT col, x, (48271 * x::bigint + 11) % 67108859 AS y FROM v) t),
      sk AS (SELECT * FROM (SELECT *, row_number() OVER (PARTITION BY col ORDER BY hv) AS rn FROM h) t
             WHERE rn <= 16),
      u AS (SELECT x, count(*) AS in_both FROM sk GROUP BY x, hv ORDER BY hv LIMIT 16)
      SELECT (SELECT round(15 / (max(hv) / 67108859.0), 1) FROM sk WHERE col = 'A') AS est_distinct_a,
             (SELECT round(15 / (max(hv) / 67108859.0), 1) FROM sk WHERE col = 'B') AS est_distinct_b,
             round(avg((in_both = 2)::int), 2) AS est_jaccard,
             (SELECT round(count(*) FILTER (WHERE n = 2)::numeric / count(*), 2)
              FROM (SELECT x, count(*) AS n FROM v GROUP BY x) t) AS exact_jaccard
      FROM u;
    mongo:
      docs: |
        [{ _id: "A", vals: Array.from({ length: 40 }, (_, i) => i + 1) },
         { _id: "B", vals: Array.from({ length: 40 }, (_, i) => i + 21) }]
      pipeline: |
        [
          { $project: { vals: 1, sk: { $slice: [{ $sortArray: { sortBy: { hv: 1 }, input: { $map: {
              input: { $setUnion: ["$vals"] }, as: "x", in: { x: "$$x", hv: { $let: {
                vars: { y: { $mod: [{ $add: [{ $multiply: [48271, "$$x"] }, 11] }, 67108859] } },
                in: { $mod: [{ $add: [{ $multiply: ["$$y", "$$y"] }, 12345] }, 67108859] } } } } } } } }, 16] } } },
          { $sort: { _id: 1 } },
          { $group: { _id: null, sks: { $push: "$sk" }, sets: { $push: "$vals" } } },
          { $project: { _id: 0,
              est_distinct_a: { $let: { vars: { s: { $arrayElemAt: ["$sks", 0] } },
                in: { $round: [{ $divide: [15, { $divide: [{ $last: "$$s.hv" }, 67108859] }] }, 1] } } },
              est_distinct_b: { $let: { vars: { s: { $arrayElemAt: ["$sks", 1] } },
                in: { $round: [{ $divide: [15, { $divide: [{ $last: "$$s.hv" }, 67108859] }] }, 1] } } },
              est_jaccard: { $let: {
                vars: { u: { $slice: [{ $sortArray: { sortBy: { hv: 1 },
                  input: { $setUnion: [{ $arrayElemAt: ["$sks", 0] }, { $arrayElemAt: ["$sks", 1] }] } } }, 16] } },
                in: { $round: [{ $divide: [{ $size: { $filter: { input: "$$u", cond: { $and: [
                  { $in: ["$$this", { $arrayElemAt: ["$sks", 0] }] },
                  { $in: ["$$this", { $arrayElemAt: ["$sks", 1] }] }] } } } }, 16] }, 2] } } },
              exact_jaccard: { $round: [{ $divide: [
                { $size: { $setIntersection: [{ $arrayElemAt: ["$sets", 0] }, { $arrayElemAt: ["$sets", 1] }] } },
                { $size: { $setUnion: [{ $arrayElemAt: ["$sets", 0] }, { $arrayElemAt: ["$sets", 1] }] } }] }, 2] } } }
        ]
    jq:
      entrada: |
        {"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
          25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
         "B": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
          43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]}
      filtro: |
        def hv: ((48271 * . + 11) % 67108859) as $y | ($y * $y + 12345) % 67108859;
        def r($d): . * pow(10; $d) | round / pow(10; $d);
        (.A | unique | map({x: ., hv: hv}) | sort_by(.hv) | .[:16]) as $a
        | (.B | unique | map({x: ., hv: hv}) | sort_by(.hv) | .[:16]) as $b
        | (($a + $b) | unique_by(.x) | sort_by(.hv) | .[:16]) as $u
        | {est_distinct_a: (15 / ($a[-1].hv / 67108859) | r(1)),
           est_distinct_b: (15 / ($b[-1].hv / 67108859) | r(1)),
           est_jaccard: ([$u[] | select(IN($a[]) and IN($b[]))] | length / 16 | r(2)),
           exact_jaccard: (((.A - (.A - .B)) | unique | length) / ((.A + .B) | unique | length) | r(2))}
    leitura: >-
      Com 16 valores de hash por coluna, o sketch estima uns 36 valores distintos em cada (são 40) e
      uma similaridade de Jaccard de 0,31 (exata: 0,33). A estimativa usa só a amostra da união: os
      16 menores hashes das duas colunas, e quantos deles estão nos dois sketches. Se a interseção
      for pequena, o sketch quase não a vê e o erro cresce.
  - id: minhash
    titulo: assinaturas MinHash e similaridade de Jaccard
    sql: |
      CREATE TABLE cols AS
        SELECT 'A' AS col, array_agg(i ORDER BY i) AS vals FROM generate_series(1, 40) AS g(i)
        UNION ALL
        SELECT 'B', array_agg(i ORDER BY i) FROM generate_series(21, 60) AS g(i);
    duckdb: |
      WITH v AS (SELECT DISTINCT col, unnest(vals) AS x FROM cols),
      f AS (SELECT i, (16807 * i) % 67108859 AS a, (7919 * i) % 67108859 AS b FROM generate_series(1, 16) AS t(i)),
      sig AS (SELECT col, i, min((y * y + 12345) % 67108859) AS m
              FROM (SELECT col, i, (a * x::bigint + b) % 67108859 AS y FROM v, f)
              GROUP BY col, i),
      r AS (SELECT count(*) AS k, avg((sa.m = sb.m)::int) AS rho
            FROM sig sa JOIN sig sb ON sa.i = sb.i AND sa.col = 'A' AND sb.col = 'B')
      SELECT k, round(rho, 2) AS est_jaccard,
             round(rho / (1 + rho) * (SELECT count(*) FROM v), 1) AS est_intersection
      FROM r;
    postgres: |
      WITH v AS (SELECT DISTINCT col, unnest(vals) AS x FROM cols),
      f AS (SELECT i, (16807 * i) % 67108859 AS a, (7919 * i) % 67108859 AS b FROM generate_series(1, 16) AS t(i)),
      sig AS (SELECT col, i, min((y * y + 12345) % 67108859) AS m
              FROM (SELECT col, i, (a * x::bigint + b) % 67108859 AS y FROM v, f) t
              GROUP BY col, i),
      r AS (SELECT count(*) AS k, avg((sa.m = sb.m)::int) AS rho
            FROM sig sa JOIN sig sb ON sa.i = sb.i AND sa.col = 'A' AND sb.col = 'B')
      SELECT k, round(rho, 2) AS est_jaccard,
             round(rho / (1 + rho) * (SELECT count(*) FROM v), 1) AS est_intersection
      FROM r;
    mongo:
      docs: |
        [{ _id: "A", vals: Array.from({ length: 40 }, (_, i) => i + 1) },
         { _id: "B", vals: Array.from({ length: 40 }, (_, i) => i + 21) }]
      pipeline: |
        [
          { $project: { n: { $size: { $setUnion: ["$vals"] } },
              sig: { $map: { input: { $range: [1, 17] }, as: "i", in: { $min: { $map: {
              input: "$vals", as: "x", in: { $let: {
                vars: { y: { $mod: [{ $add: [{ $multiply: [{ $mod: [{ $multiply: [16807, "$$i"] }, 67108859] }, "$$x"] },
                                             { $mod: [{ $multiply: [7919, "$$i"] }, 67108859] }] }, 67108859] } },
                in: { $mod: [{ $add: [{ $multiply: ["$$y", "$$y"] }, 12345] }, 67108859] } } } } } } } } } },
          { $sort: { _id: 1 } },
          { $group: { _id: null, sigs: { $push: "$sig" }, n: { $sum: "$n" } } },
          { $set: { k: { $size: { $arrayElemAt: ["$sigs", 0] } },
              rho: { $avg: { $map: { input: { $range: [0, 16] }, as: "i", in: { $cond: [
                { $eq: [{ $arrayElemAt: [{ $arrayElemAt: ["$sigs", 0] }, "$$i"] },
                        { $arrayElemAt: [{ $arrayElemAt: ["$sigs", 1] }, "$$i"] }] }, 1, 0] } } } } } },
          { $project: { _id: 0, k: "$k", est_jaccard: { $round: ["$rho", 2] },
              est_intersection: { $round: [{ $multiply: [{ $divide: ["$rho", { $add: [1, "$rho"] }] }, "$n"] }, 1] } } }
        ]
    jq:
      entrada: |
        {"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
          25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
         "B": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
          43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]}
      filtro: |
        def h($i): ((16807 * $i % 67108859) * . + (7919 * $i % 67108859)) % 67108859 as $y
                   | ($y * $y + 12345) % 67108859;
        def sig: . as $vals | [range(1; 17) as $i | [$vals[] | h($i)] | min];
        (.A | sig) as $a | (.B | sig) as $b
        | ([range(16) | select($a[.] == $b[.])] | length / 16) as $rho
        | {k: 16, est_jaccard: ($rho * 100 | round / 100),
           est_intersection: ($rho / (1 + $rho) * ((.A | unique | length) + (.B | unique | length)) * 10 | round / 10)}
    leitura: >-
      Cada coluna vira uma assinatura de 16 números, o menor hash sob cada uma de 16 funções. A
      fração de posições iguais estima a similaridade de Jaccard: 0,31 (exata: 0,33). Com os 40
      valores distintos de cada coluna, que o perfil já conhece, a fórmula de Dasu et al.[@dasu2002]
      estima uma interseção de 19 valores (exata: 20). Comparar duas assinaturas custa 16
      comparações, não importa o tamanho das colunas.
---
Além do agrupamento, outra forma de descrever os dados é criar resumos ou *sketches*, por amostragem ou por hashing dos valores para um domínio menor. Sketches respondem consultas aproximadas, processam fluxos de dados e estimam tamanhos de junções.[@abedjan2015]

São métodos de processamento aproximado de consultas (*Approximate Query Processing*, AQP), muitas vezes o único meio de manter a exploração interativa em conjuntos de dados enormes. Eles procedem "calculando uma sinopse compacta, com perdas, dos dados, e então executando a consulta de interesse sobre a sinopse em vez do conjunto de dados inteiro".[@cormode2011, p. 1]

## Amostragem

A amostra aleatória é a sinopse mais fundamental e mais implementada: executa-se a consulta sobre um subconjunto pequeno e representativo dos dados.[@cormode2011] Em perfilamento, isso permite, por exemplo, verificar se uma dependência vale numa amostra em vez da tabela inteira. Os esquemas básicos:[@cormode2011]

- **Amostragem aleatória simples, com ou sem reposição:** sorteie *n* itens de *R*; sem reposição, nenhum item entra duas vezes, e a variância das estimativas é menor.
- **Amostragem de Bernoulli:** lance uma moeda independente para cada linha, com a mesma probabilidade *p* de inclusão. O tamanho da amostra é aleatório, e a soma estimada é a soma da amostra dividida por *p*. Na amostragem de Poisson, cada linha tem a sua própria probabilidade.
- **Amostragem estratificada:** divida as linhas em estratos e faça uma amostragem sem reposição em cada um; estime cada estrato com o peso dele e some. Estratos internamente homogêneos reduzem muito a variância.
- **Reservatório:** para fluxos de tamanho desconhecido, guarde as *n* primeiras linhas e aceite a *i*-ésima com probabilidade *n*/*i*, no lugar de uma linha sorteada do reservatório; o conteúdo é sempre uma amostra uniforme de tamanho *n*.

DuckDB (`USING SAMPLE`), PostgreSQL (`TABLESAMPLE`) e MongoDB (`$sample`) sorteiam de verdade, então a saída muda a cada execução. Os exemplos abaixo usam o hash do `id` como moeda, para que a saída seja reprodutível.

## Sketches e similaridade de colunas

Uma tarefa de interesse é avaliar a similaridade de duas colunas *A* e *B* pela similaridade de Jaccard, |*A* ∩ *B*| / |*A* ∪ *B*|: o número de valores distintos em comum dividido pelo total de valores distintos nas duas. Como valores semanticamente iguais podem ter formatos diferentes, a mesma conta vale para as distribuições de n-gramas. Se os conjuntos de valores distintos não estiverem disponíveis, estime a similaridade pelas assinaturas MinHash das colunas.[@abedjan2015]

- **k Minimum Values (KMV):** aplique uma função de hash aos valores e guarde só os *k* menores hashes distintos. O número de valores distintos se estima por (*k* − 1)/*h*ₖ, com *h*ₖ o *k*-ésimo menor hash normalizado para [0, 1]. Para duas colunas, os *k* menores hashes da união dos dois sketches formam uma amostra uniforme da união; a fração desses itens presentes nos dois sketches estima |*A* ∩ *B*| / |*A* ∪ *B*|. A precisão depende do tamanho da união: se a interseção for pequena, é improvável que a amostra a encontre.[@cormode2011]
- **MinHash (hashing min-wise):** use *k* funções de hash independentes e guarde, para cada uma, o menor hash da coluna. Gasta mais tempo por valor que o KMV, que usa uma única função.[@cormode2011] Duas colunas têm o mesmo mínimo numa posição com probabilidade igual à similaridade de Jaccard; a fração de posições iguais a estima.[@dasu2002]

O sistema Bellman usa essas assinaturas para minerar a estrutura de bancos com milhares de tabelas e pouca documentação sobre chaves primárias e estrangeiras:[@dasu2002]

- **Semelhança (*resemblance*):** com *s*(*A*) = min *h*(*a*), vale Pr[*s*(*A*) = *s*(*B*)] = ρ, a similaridade de Jaccard. Um único mínimo é uma variável de Bernoulli de variância alta; a assinatura junta *N* mínimos, um por função de hash, e estima ρ pela fração de posições iguais.[@dasu2002, p. 241]
- **Tamanho da interseção:** como o perfil já guarda o número de valores distintos |*A*| e |*B*|, |*A* ∩ *B*| = ρ/(1 + ρ) · (|*A*| + |*B*|). A estimativa filtra pares de colunas com interseção pequena antes de testar junções.[@dasu2002, p. 241-242]
- **Contenção:** a fração de posições com *s*ᵢ(*A*) < *s*ᵢ(*B*) estima |*A* \ *B*| / |*A* ∪ *B*|. Se essa fração é pequena e a inversa é grande, *A* está em grande parte contido em *B*.[@dasu2002, p. 242]
- **Soma:** a assinatura de *A* ∪ *B* é o mínimo, posição a posição, das duas assinaturas.[@dasu2002, p. 242]
- **Em SQL:** as assinaturas ficam numa tabela (campo, número do hash, valor do hash), e uma junção nessa tabela conta as posições iguais entre um campo e todos os outros.[@dasu2002, p. 242]
- **q-gramas:** chaves em formatos diferentes, como `ddd-dd-dddd` e `SSddd-dd-dddd`, quase não têm valores em comum, mas seus conjuntos de q-gramas (substrings de *q* caracteres) são parecidos. A assinatura do conjunto de q-gramas aponta campos ligados por uma pequena transformação.[@dasu2002, p. 242-243]
- **Tamanho da assinatura:** nos experimentos dos autores, 50 posições bastaram para separar interseções pequenas, médias e grandes, e 100 separaram todos os pares testados. O erro cresce muito com similaridade de 25% ou menos.[@dasu2002, p. 246]

Nos exemplos, os valores são inteiros e o hash é uma função de módulo primo escrita à mão, para dar o mesmo resultado nos quatro motores. Em uso real, prefira a função de hash do motor (`hash` no DuckDB, `hashtext` no PostgreSQL).
