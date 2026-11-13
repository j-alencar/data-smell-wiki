---
smell: Dummy Value
exemplo:
  tarefa: constancy
  sql: |
    CREATE TABLE accounts (id int, signed_up date);
    INSERT INTO accounts VALUES
      (1, '1970-01-01'), (2, '2021-06-14'), (3, '1970-01-01'),
      (4, '2022-03-02'), (5, '1970-01-01'), (6, '2021-11-20');
  duckdb: |
    SELECT signed_up AS top_value,
           count(*) AS n,
           round(count(*) / (SELECT count(*) FROM accounts), 2) AS constancy
    FROM accounts
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  postgres: |
    SELECT signed_up AS top_value,
           count(*) AS n,
           round(count(*)::numeric / (SELECT count(*) FROM accounts), 2) AS constancy
    FROM accounts
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  mongo:
    docs: |
      [
        { _id: 1, signedUp: new Date("1970-01-01") }, { _id: 2, signedUp: new Date("2021-06-14") },
        { _id: 3, signedUp: new Date("1970-01-01") }, { _id: 4, signedUp: new Date("2022-03-02") },
        { _id: 5, signedUp: new Date("1970-01-01") }, { _id: 6, signedUp: new Date("2021-11-20") }
      ]
    pipeline: |
      [
        { $group: { _id: "$signedUp", n: { $sum: 1 } } },
        { $setWindowFields: { output: { total: { $sum: "$n",
            window: { documents: ["unbounded", "unbounded"] } } } } },
        { $sort: { n: -1 } }, { $limit: 1 },
        { $project: { _id: 0,
            top_value: { $dateToString: { format: "%Y-%m-%d", date: "$_id" } },
            n: 1, constancy: { $round: [{ $divide: ["$n", "$total"] }, 2] } } }
      ]
  jq:
    entrada: |
      [{"signedUp": "1970-01-01"}, {"signedUp": "2021-06-14"}, {"signedUp": "1970-01-01"},
       {"signedUp": "2022-03-02"}, {"signedUp": "1970-01-01"}, {"signedUp": "2021-11-20"}]
    filtro: |
      length as $rows
      | group_by(.signedUp) | max_by(length)
      | {top_value: .[0].signedUp, n: length, constancy: (length / $rows)}
  leitura: >-
    Metade das linhas tem 1970-01-01, o dia zero do tempo Unix. Uma data frequente demais e no
    marco zero de um sistema costuma ser um valor substituto.
---
Em datas, o valor substituto costuma ser um marco: o dia zero de um sistema ou o primeiro dia de um ano.
