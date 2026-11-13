---
smell: Date/Time as String
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE readings (id int, read_at text);
    INSERT INTO readings VALUES
      (1, '2020-12-30 11:50:40'), (2, '2020-12-30 11:51:10'), (3, '2020-12-30 11:52:05');
  duckdb: |
    SELECT typeof(read_at) AS data_type, pattern(read_at) AS pattern, count(*) AS n
    FROM readings
    GROUP BY ALL;
  postgres: |
    SELECT pg_typeof(read_at)::text AS data_type, pattern(read_at) AS pattern, count(*) AS n
    FROM readings
    GROUP BY 1, 2;
  mongo:
    docs: |
      [
        { _id: 1, reading: { at: "2020-12-30 11:50:40" } },
        { _id: 2, reading: { at: "2020-12-30 11:51:10" } },
        { _id: 3, reading: { at: "2020-12-30 11:52:05" } }
      ]
    pipeline: |
      [
        { $group: { _id: { type: { $type: "$reading.at" }, pattern: pattern("$reading.at") },
                    n: { $sum: 1 } } }
      ]
  jq:
    entrada: |
      [{"at": "2020-12-30 11:50:40"}, {"at": "2020-12-30 11:51:10"}, {"at": "2020-12-30 11:52:05"}]
    filtro: |
      [.[].at] | group_by(pattern)
      | map({type: (.[0] | type), pattern: (.[0] | pattern), n: length})[]
  leitura: Um único padrão de timestamp, guardado como texto.
---
Um padrão de data e hora estável num campo de texto pede um tipo timestamp.
