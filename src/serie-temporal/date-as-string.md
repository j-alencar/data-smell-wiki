---
smell: Date as String
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE events (id int, event_date text);
    INSERT INTO events VALUES
      (1, '2020-12-30'), (2, '2020-12-31'), (3, '2021-01-04'), (4, '2021-01-05');
  duckdb: |
    SELECT typeof(event_date)                  AS data_type,
           count(*)                            AS n,
           count(TRY_CAST(event_date AS DATE)) AS castable_to_date
    FROM events
    GROUP BY 1;
  postgres: |
    SELECT pg_typeof(event_date)::text AS data_type,
           count(*) AS n,
           count(*) FILTER (WHERE pg_input_is_valid(event_date, 'date')) AS castable_to_date
    FROM events
    GROUP BY 1;
  mongo:
    docs: |
      [
        { _id: 1, event: { date: "2020-12-30" } }, { _id: 2, event: { date: "2020-12-31" } },
        { _id: 3, event: { date: "2021-01-04" } }, { _id: 4, event: { date: "2021-01-05" } }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $type: "$event.date" },
            n: { $sum: 1 },
            castableToDate: { $sum: { $cond: [
              { $ne: [{ $convert: { input: "$event.date", to: "date", onError: null } }, null] },
              1, 0] } } } }
      ]
  jq:
    entrada: |
      [{"date": "2020-12-30"}, {"date": "2020-12-31"},
       {"date": "2021-01-04"}, {"date": "2021-01-05"}]
    filtro: |
      [.[].date]
      | {types: (map(type) | unique), n: length,
         castable_to_date: (map(select(try (strptime("%Y-%m-%d") | true) catch false)) | length)}
  leitura: Todos os valores são strings, e todos se convertem em data.
---
Compare o tipo declarado com aquilo em que os valores de fato se convertem.
