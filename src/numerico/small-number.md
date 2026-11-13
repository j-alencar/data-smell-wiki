---
smell: Small Number
refs: [foidl2022a]
exemplo:
  tarefa: histogram
  sql: |
    CREATE TABLE rates (id int, rate double precision);
    INSERT INTO rates VALUES (1, 12), (2, 0.04), (3, 0.02), (4, 0.00024), (5, 0.4), (6, 7);
  duckdb: |
    SELECT CAST(floor(log10(rate)) AS INTEGER) AS magnitude, count(*) AS n
    FROM rates
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT floor(log10(rate))::int AS magnitude, count(*) AS n
    FROM rates
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, rate: 12 }, { _id: 2, rate: 0.04 }, { _id: 3, rate: 0.02 },
        { _id: 4, rate: 0.00024 }, { _id: 5, rate: 0.4 }, { _id: 6, rate: 7 }
      ]
    pipeline: |
      [
        { $group: { _id: { $floor: { $log10: "$rate" } }, n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"rate": 12}, {"rate": 0.04}, {"rate": 0.02}, {"rate": 0.00024}, {"rate": 0.4}, {"rate": 7}]
    filtro: |
      [.[].rate | log10 | floor]
      | group_by(.) | map({magnitude: .[0], n: length})[]
  leitura: >-
    Quatro dos seis valores estão abaixo de 1, um deles na casa de 10⁻⁴. Multiplicados entre si, perdem
    casas decimais ou sofrem underflow (FOIDL; FELDERER; RAMLER, 2022a).
---
Um histograma por ordem de grandeza (`floor(log10(v))`) mostra quantos valores ficam abaixo de 1 e quão abaixo.
