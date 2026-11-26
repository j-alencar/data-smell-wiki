---
exemplos:
  - id: base
    titulo: candidata a chave
    sql: |
      CREATE TABLE customers (id int, email text, city text);
      INSERT INTO customers VALUES
        (1, 'ana@x.com', 'Recife'), (2, 'bia@x.com', 'Natal'), (3, 'caio@x.com', 'Recife'),
        (4, 'dani@x.com', 'Natal');
    duckdb: |
      SELECT col, count(DISTINCT v) AS distinct_values, count(*) AS n,
             count(DISTINCT v) / count(*) AS uniqueness
      FROM (UNPIVOT customers ON email, city INTO NAME col VALUE v)
      GROUP BY col
      ORDER BY uniqueness DESC;
    postgres: |
      SELECT col, count(DISTINCT v) AS distinct_values, count(*) AS n,
             round(count(DISTINCT v)::numeric / count(*), 2) AS uniqueness
      FROM customers, LATERAL (VALUES ('email', email), ('city', city)) AS u(col, v)
      GROUP BY col
      ORDER BY uniqueness DESC;
    mongo:
      docs: |
        [
          { _id: 1, email: "ana@x.com", city: "Recife" }, { _id: 2, email: "bia@x.com", city: "Natal" },
          { _id: 3, email: "caio@x.com", city: "Recife" }, { _id: 4, email: "dani@x.com", city: "Natal" }
        ]
      pipeline: |
        [
          { $project: { kv: { $objectToArray: { email: "$email", city: "$city" } } } },
          { $unwind: "$kv" },
          { $group: { _id: "$kv.k", vals: { $addToSet: "$kv.v" }, n: { $sum: 1 } } },
          { $project: { _id: 0, col: "$_id", distinct_values: { $size: "$vals" }, n: "$n",
              uniqueness: { $divide: [{ $size: "$vals" }, "$n"] } } },
          { $sort: { uniqueness: -1 } }
        ]
    jq:
      entrada: |
        [{"email": "ana@x.com", "city": "Recife"}, {"email": "bia@x.com", "city": "Natal"},
         {"email": "caio@x.com", "city": "Recife"}, {"email": "dani@x.com", "city": "Natal"}]
      filtro: |
        . as $rows
        | ["email", "city"] | map(. as $c | [$rows[][$c]]
            | {col: $c, distinct_values: (unique | length), n: length})
        | map(.uniqueness = .distinct_values / .n) | sort_by(-.uniqueness)[]
    leitura: >-
      `email` tem unicidade 1: todo valor é único, logo é candidata a chave. `city` fica em 0,5. A
      unicidade 1 numa amostra não garante a chave; só a restrição no esquema garante.
---
A unicidade deriva do número de [valores distintos](/tarefas/distinct-values/): é esse número dividido pelo número de linhas. Coluna com todos os valores únicos é candidata a chave.[@abedjan2015]
