---
smell: Unit Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE events (id int, created_at bigint);
    INSERT INTO events VALUES
      (1, 1609459200), (2, 1609459260000), (3, 1609459320), (4, 1609459380);
  duckdb: |
    SELECT pattern(CAST(created_at AS VARCHAR)) AS pattern, count(*) AS n
    FROM events
    GROUP BY 1
    ORDER BY n DESC;
  postgres: |
    SELECT pattern(created_at::text) AS pattern, count(*) AS n
    FROM events
    GROUP BY 1
    ORDER BY n DESC;
  mongo:
    docs: |
      [
        { _id: 1, meta: { createdAt: NumberLong("1609459200") } },
        { _id: 2, meta: { createdAt: NumberLong("1609459260000") } },
        { _id: 3, meta: { createdAt: NumberLong("1609459320") } },
        { _id: 4, meta: { createdAt: NumberLong("1609459380") } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern({ $toString: "$meta.createdAt" }), n: { $sum: 1 } } },
        { $sort: { n: -1 } }
      ]
  jq:
    entrada: |
      [{"createdAt": 1609459200}, {"createdAt": 1609459260000},
       {"createdAt": 1609459320}, {"createdAt": 1609459380}]
    filtro: |
      [.[].createdAt | tostring | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by(-.n)[]
  leitura: >-
    Um valor de 13 dígitos entre valores de 10: provavelmente milissegundos no meio de segundos.
---
Em timestamps, a unidade é a resolução da época. Segundos e milissegundos desde 1970 se parecem, mas diferem em três dígitos (10 contra 13, para datas atuais).
