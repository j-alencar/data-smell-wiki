---
exemplos:
  - id: base
    titulo: "pollnum →[9,11] t: coletas a cada 9 a 11 segundos"
    sql: |
      CREATE TABLE polls (pollnum int, t int);
      INSERT INTO polls VALUES
        (1, 0), (2, 10), (3, 20), (4, 30), (5, 50), (6, 60), (7, 70), (8, 79), (9, 85), (10, 95);
    duckdb: |
      SELECT pollnum, t, gap, CASE WHEN gap BETWEEN 9 AND 11 THEN 'ok' ELSE 'violates' END AS sd
      FROM (SELECT pollnum, t, t - lag(t) OVER (ORDER BY pollnum) AS gap FROM polls)
      WHERE gap IS NOT NULL
      ORDER BY pollnum;
    postgres: |
      SELECT pollnum, t, gap, CASE WHEN gap BETWEEN 9 AND 11 THEN 'ok' ELSE 'violates' END AS sd
      FROM (SELECT pollnum, t, t - lag(t) OVER (ORDER BY pollnum) AS gap FROM polls) p
      WHERE gap IS NOT NULL
      ORDER BY pollnum;
    mongo:
      docs: |
        [0, 10, 20, 30, 50, 60, 70, 79, 85, 95].map((t, i) => ({ _id: i + 1, pollnum: i + 1, t }))
      pipeline: |
        [
          { $setWindowFields: { sortBy: { pollnum: 1 }, output: { prev: { $shift: { output: "$t", by: -1 } } } } },
          { $match: { prev: { $ne: null } } },
          { $set: { gap: { $subtract: ["$t", "$prev"] } } },
          { $project: { _id: 0, pollnum: 1, t: 1, gap: 1,
              sd: { $cond: [{ $and: [{ $gte: ["$gap", 9] }, { $lte: ["$gap", 11] }] }, "ok", "violates"] } } },
          { $sort: { pollnum: 1 } }
        ]
    jq:
      entrada: |
        [{"pollnum": 1, "t": 0}, {"pollnum": 2, "t": 10}, {"pollnum": 3, "t": 20}, {"pollnum": 4, "t": 30},
         {"pollnum": 5, "t": 50}, {"pollnum": 6, "t": 60}, {"pollnum": 7, "t": 70}, {"pollnum": 8, "t": 79},
         {"pollnum": 9, "t": 85}, {"pollnum": 10, "t": 95}]
      filtro: |
        sort_by(.pollnum) | [., .[1:]] | transpose[:-1][]
        | (.[1].t - .[0].t) as $gap
        | {pollnum: .[1].pollnum, t: .[1].t, gap: $gap,
           sd: (if $gap >= 9 and $gap <= 11 then "ok" else "violates" end)}
    leitura: >-
      Sete das nove lacunas ficam em [9, 11]. A lacuna de 20 s entre as coletas 4 e 5 indica uma
      coleta perdida; a de 6 s entre 8 e 9, uma coleta extra ou adiantada.
  - id: aplicado
    smell: Suspect Date/Time Interval
    mundo: serie-temporal
    sql: |
      CREATE TABLE backups (id int, ran_on date);
      INSERT INTO backups VALUES
        (1, '2019-01-01'), (2, '2019-01-02'), (3, '2019-10-01'), (4, '2019-10-02'), (5, '2019-10-03');
    duckdb: |
      SELECT prev_id, id, prev_day, ran_on, gap_days
      FROM (SELECT id, ran_on,
                   lag(id) OVER (ORDER BY id) AS prev_id,
                   lag(ran_on) OVER (ORDER BY id) AS prev_day,
                   ran_on - lag(ran_on) OVER (ORDER BY id) AS gap_days
            FROM backups)
      WHERE gap_days NOT BETWEEN 1 AND 1
      ORDER BY id;
    postgres: |
      SELECT prev_id, id, prev_day, ran_on, gap_days
      FROM (SELECT id, ran_on,
                   lag(id) OVER (ORDER BY id) AS prev_id,
                   lag(ran_on) OVER (ORDER BY id) AS prev_day,
                   ran_on - lag(ran_on) OVER (ORDER BY id) AS gap_days
            FROM backups) b
      WHERE gap_days NOT BETWEEN 1 AND 1
      ORDER BY id;
    mongo:
      docs: |
        [
          { _id: 1, ranOn: new Date("2019-01-01") }, { _id: 2, ranOn: new Date("2019-01-02") },
          { _id: 3, ranOn: new Date("2019-10-01") }, { _id: 4, ranOn: new Date("2019-10-02") },
          { _id: 5, ranOn: new Date("2019-10-03") }
        ]
      pipeline: |
        [
          { $setWindowFields: { sortBy: { _id: 1 }, output: {
              prevId: { $shift: { output: "$_id", by: -1 } }, prevDay: { $shift: { output: "$ranOn", by: -1 } } } } },
          { $match: { prevDay: { $ne: null } } },
          { $set: { gapDays: { $dateDiff: { startDate: "$prevDay", endDate: "$ranOn", unit: "day" } } } },
          { $match: { $expr: { $or: [{ $lt: ["$gapDays", 1] }, { $gt: ["$gapDays", 1] }] } } },
          { $project: { _id: 0, prevId: "$prevId", id: "$_id",
              prevDay: { $dateToString: { date: "$prevDay", format: "%Y-%m-%d" } },
              ranOn: { $dateToString: { date: "$ranOn", format: "%Y-%m-%d" } }, gapDays: "$gapDays" } }
        ]
    jq:
      entrada: |
        [{"id": 1, "ran_on": "2019-01-01"}, {"id": 2, "ran_on": "2019-01-02"},
         {"id": 3, "ran_on": "2019-10-01"}, {"id": 4, "ran_on": "2019-10-02"},
         {"id": 5, "ran_on": "2019-10-03"}]
      filtro: |
        def day: strptime("%Y-%m-%d") | mktime / 86400;
        sort_by(.id) | [., .[1:]] | transpose[:-1][]
        | {prev_id: .[0].id, id: .[1].id, prev_day: .[0].ran_on, ran_on: .[1].ran_on,
           gap_days: ((.[1].ran_on | day) - (.[0].ran_on | day))}
        | select(.gap_days < 1 or .gap_days > 1)
    leitura: >-
      O backup é diário, então a SD esperada é `id →[1,1] ran_on`: entre execuções consecutivas, um
      dia. Só o par 2 → 3 viola, com 272 dias. Diferente do histograma de lacunas, a SD aponta
      exatamente onde a sequência quebra.
---
Uma dependência de ordem diz que a relação ordenada por *A* também fica ordenada por *B*.[@ginsburg1983] As dependências sequenciais (SDs) generalizam a ideia: dada uma SD, o algoritmo de Golab et al. encontra as faixas de *X* em que ela vale aproximadamente.[@golab2009][@abedjan2015]

Uma SD *X* →[*a*,*b*] *Y* exige que, após ordenar as linhas por *X*, a diferença de *Y* entre linhas consecutivas fique entre *a* e *b*.[@golab2009] No exemplo, `pollnum →[9,11] t` admite de 9 a 11 segundos entre coletas. Lacunas maiores podem indicar coletas perdidas; menores, coletas extras ou adiantadas.
