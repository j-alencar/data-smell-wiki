---
smell: Dummy Value
refs: [foidl2022a]
exemplo:
  tarefa: constancy
  sql: |
    CREATE TABLE people (id int, age int);
    INSERT INTO people VALUES (1, 34), (2, 999), (3, 27), (4, 999), (5, 41), (6, 999);
  duckdb: |
    SELECT age AS top_value,
           count(*) AS n,
           round(count(*) / (SELECT count(*) FROM people), 2) AS constancy
    FROM people
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  postgres: |
    SELECT age AS top_value,
           count(*) AS n,
           round(count(*)::numeric / (SELECT count(*) FROM people), 2) AS constancy
    FROM people
    GROUP BY 1
    ORDER BY n DESC
    LIMIT 1;
  mongo:
    docs: |
      [
        { _id: 1, person: { age: 34 } }, { _id: 2, person: { age: 999 } },
        { _id: 3, person: { age: 27 } }, { _id: 4, person: { age: 999 } },
        { _id: 5, person: { age: 41 } }, { _id: 6, person: { age: 999 } }
      ]
    pipeline: |
      [
        { $group: { _id: "$person.age", n: { $sum: 1 } } },
        { $setWindowFields: { output: { total: { $sum: "$n",
            window: { documents: ["unbounded", "unbounded"] } } } } },
        { $sort: { n: -1 } }, { $limit: 1 },
        { $project: { _id: 0, top_value: "$_id", n: 1,
            constancy: { $round: [{ $divide: ["$n", "$total"] }, 2] } } }
      ]
  jq:
    entrada: |
      [{"age": 34}, {"age": 999}, {"age": 27}, {"age": 999}, {"age": 41}, {"age": 999}]
    filtro: |
      length as $rows
      | group_by(.age) | max_by(length)
      | {top_value: .[0].age, n: length, constancy: (length / $rows)}
  leitura: >-
    999 é a idade mais frequente e não é plausível. Como idade, o valor provavelmente marca uma
    entrada ausente (FOIDL; FELDERER; RAMLER, 2022a).
---
Em números, procure um valor repetido fora da faixa plausível, muitas vezes feito de noves ou de limites de tipo (65535).
