---
exemplos:
  - id: base
    titulo: potências de 2 contra a Lei de Benford
    sql: |
      CREATE TABLE powers AS
        SELECT i AS id, CAST(power(2, i) AS bigint) AS v FROM generate_series(0, 29) AS g(i);
    duckdb: |
      SELECT d, count(v) AS n,
             round(count(v) / (SELECT count(*) FROM powers), 3) AS observed,
             round(log10(1 + 1 / d), 3) AS benford
      FROM generate_series(1, 9) AS g(d)
      LEFT JOIN powers ON left(CAST(v AS text), 1) = CAST(d AS text)
      GROUP BY d
      ORDER BY d;
    postgres: |
      SELECT d, count(v) AS n,
             round(count(v)::numeric / (SELECT count(*) FROM powers), 3) AS observed,
             round(log(1 + 1.0 / d), 3) AS benford
      FROM generate_series(1, 9) AS g(d)
      LEFT JOIN powers ON left(CAST(v AS text), 1) = CAST(d AS text)
      GROUP BY d
      ORDER BY d;
    mongo:
      docs: |
        Array.from({ length: 30 }, (_, i) => ({ _id: i, v: 2 ** i }))
      pipeline: |
        [
          { $group: { _id: null, ds: { $push: { $toInt: { $substrCP: [{ $toString: "$v" }, 0, 1] } } } } },
          { $project: { _id: 0, row: { $map: { input: { $range: [1, 10] }, as: "d", in: {
              d: "$$d",
              n: { $size: { $filter: { input: "$ds", cond: { $eq: ["$$this", "$$d"] } } } },
              total: { $size: "$ds" } } } } } },
          { $unwind: "$row" },
          { $project: { d: "$row.d", n: "$row.n",
              observed: { $round: [{ $divide: ["$row.n", "$row.total"] }, 3] },
              benford: { $round: [{ $log10: { $add: [1, { $divide: [1, "$row.d"] }] } }, 3] } } }
        ]
    jq:
      entrada: |
        30
      filtro: |
        [range(.) | pow(2; .) | tostring[0:1] | tonumber] as $ds
        | range(1; 10) as $d
        | ([$ds[] | select(. == $d)] | length) as $n
        | {d: $d, n: $n,
           observed: ($n / ($ds | length) * 1000 | round / 1000),
           benford: ((1 + 1 / $d | log10) * 1000 | round / 1000)}
    leitura: >-
      Trinta potências de 2 já seguem a curva: o 1 lidera com 30%, o 2 vem depois com 20%. Os
      dígitos 7 e 9 faltam porque a série é curta; com mais potências, as frequências se aproximam
      de P(*d*).
  - id: aplicado
    smell: Dummy Value
    mundo: numerico
    sql: |
      CREATE TABLE invoices (id int, amount int);
      INSERT INTO invoices VALUES
        (1, 1200), (2, 135), (3, 1890), (4, 210), (5, 2400), (6, 31), (7, 15), (8, 470),
        (9, 1100), (10, 160), (11, 27), (12, 380), (13, 1450), (14, 19), (15, 52), (16, 230),
        (17, 9999), (18, 9999), (19, 9999), (20, 9999);
    duckdb: |
      SELECT d, count(amount) AS n,
             round(count(amount) / (SELECT count(*) FROM invoices), 3) AS observed,
             round(log10(1 + 1 / d), 3) AS benford
      FROM generate_series(1, 9) AS g(d)
      LEFT JOIN invoices ON left(CAST(amount AS text), 1) = CAST(d AS text)
      GROUP BY d
      ORDER BY d;
    postgres: |
      SELECT d, count(amount) AS n,
             round(count(amount)::numeric / (SELECT count(*) FROM invoices), 3) AS observed,
             round(log(1 + 1.0 / d), 3) AS benford
      FROM generate_series(1, 9) AS g(d)
      LEFT JOIN invoices ON left(CAST(amount AS text), 1) = CAST(d AS text)
      GROUP BY d
      ORDER BY d;
    mongo:
      docs: |
        [1200, 135, 1890, 210, 2400, 31, 15, 470, 1100, 160, 27, 380, 1450, 19, 52, 230,
         9999, 9999, 9999, 9999].map((v, i) => ({ _id: i + 1, amount: v }))
      pipeline: |
        [
          { $group: { _id: null, ds: { $push: { $toInt: { $substrCP: [{ $toString: "$amount" }, 0, 1] } } } } },
          { $project: { _id: 0, row: { $map: { input: { $range: [1, 10] }, as: "d", in: {
              d: "$$d",
              n: { $size: { $filter: { input: "$ds", cond: { $eq: ["$$this", "$$d"] } } } },
              total: { $size: "$ds" } } } } } },
          { $unwind: "$row" },
          { $project: { d: "$row.d", n: "$row.n",
              observed: { $round: [{ $divide: ["$row.n", "$row.total"] }, 3] },
              benford: { $round: [{ $log10: { $add: [1, { $divide: [1, "$row.d"] }] } }, 3] } } }
        ]
    jq:
      entrada: |
        [1200, 135, 1890, 210, 2400, 31, 15, 470, 1100, 160, 27, 380, 1450, 19, 52, 230,
         9999, 9999, 9999, 9999]
      filtro: |
        [.[] | tostring[0:1] | tonumber] as $ds
        | range(1; 10) as $d
        | ([$ds[] | select(. == $d)] | length) as $n
        | {d: $d, n: $n,
           observed: ($n / ($ds | length) * 1000 | round / 1000),
           benford: ((1 + 1 / $d | log10) * 1000 | round / 1000)}
    leitura: >-
      O dígito 9 aparece em 20% das faturas; a Lei de Benford espera 4,6%. Os quatro `9999` são o
      excesso: um valor fictício repetido distorce a distribuição do primeiro dígito. Com só 20
      valores o teste é grosseiro; ele ganha força em colunas grandes.
---
A Lei de Benford afirma que, em números que ocorrem naturalmente, o primeiro dígito *d* segue aproximadamente P(*d*) = log₁₀(1 + 1/*d*). O dígito 1 deve ser o mais frequente, seguido do 2 e assim por diante. O comportamento foi observado em pesos moleculares, tamanhos de prédios e contas de luz, e a lei já serviu para revelar fraudes contábeis e outros números fabricados.[@abedjan2015][@benford1938]

| *d* | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| P(*d*) | 30,1% | 17,6% | 12,5% | 9,7% | 7,9% | 6,7% | 5,8% | 5,1% | 4,6% |

A lei vale para valores que se espalham por várias ordens de grandeza. Valores presos a uma faixa estreita, como idades ou notas de 0 a 10, não a seguem, e o desvio não indica problema nenhum.
