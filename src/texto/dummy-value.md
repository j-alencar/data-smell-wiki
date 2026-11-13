---
smell: Dummy Value
exemplo:
  tarefa: constancy
  sql: |
    CREATE TABLE signups (id int, name text);
    INSERT INTO signups VALUES
      (1, 'unknown'), (2, 'Ana'), (3, 'unknown'), (4, 'Bruno'), (5, 'unknown'), (6, 'Carla');
  duckdb: |
    SELECT name AS top_value,
           count(*) AS n,
           round(count(*) / (SELECT count(*) FROM signups), 2) AS constancy
    FROM signups
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  postgres: |
    SELECT name AS top_value,
           count(*) AS n,
           round(count(*)::numeric / (SELECT count(*) FROM signups), 2) AS constancy
    FROM signups
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  mongo:
    docs: |
      [
        { _id: 1, name: "unknown" }, { _id: 2, name: "Ana" }, { _id: 3, name: "unknown" },
        { _id: 4, name: "Bruno" }, { _id: 5, name: "unknown" }, { _id: 6, name: "Carla" }
      ]
    pipeline: |
      [
        { $group: { _id: "$name", n: { $sum: 1 } } },
        { $setWindowFields: { output: { total: { $sum: "$n",
            window: { documents: ["unbounded", "unbounded"] } } } } },
        { $sort: { n: -1 } }, { $limit: 1 },
        { $project: { _id: 0, top_value: "$_id", n: 1,
            constancy: { $round: [{ $divide: ["$n", "$total"] }, 2] } } }
      ]
  jq:
    entrada: |
      [{"name": "unknown"}, {"name": "Ana"}, {"name": "unknown"},
       {"name": "Bruno"}, {"name": "unknown"}, {"name": "Carla"}]
    filtro: |
      length as $rows
      | group_by(.name) | max_by(length)
      | {top_value: .[0].name, n: length, constancy: (length / $rows)}
  leitura: Metade dos cadastros tem o nome `unknown`, um valor posto ali para preencher o campo obrigatório.
---
Em texto, o substituto costuma ser uma palavra genérica ("unknown", "xxx", "teste") repetida muito acima dos valores reais.
