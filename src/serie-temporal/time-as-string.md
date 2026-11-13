---
smell: Time as String
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE shifts (id int, starts text);
    INSERT INTO shifts VALUES (1, '11:50:40'), (2, '07:00:00'), (3, '23:15:00'), (4, '14:30:00');
  duckdb: |
    SELECT typeof(starts) AS data_type,
           count(*) AS n,
           count(TRY_CAST(starts AS TIME)) AS castable_to_time
    FROM shifts
    GROUP BY 1;
  postgres: |
    SELECT pg_typeof(starts)::text AS data_type,
           count(*) AS n,
           count(*) FILTER (WHERE pg_input_is_valid(starts, 'time')) AS castable_to_time
    FROM shifts
    GROUP BY 1;
  mongo:
    docs: |
      [
        { _id: 1, shift: { starts: "11:50:40" } }, { _id: 2, shift: { starts: "07:00:00" } },
        { _id: 3, shift: { starts: "23:15:00" } }, { _id: 4, shift: { starts: "14:30:00" } }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $type: "$shift.starts" },
            n: { $sum: 1 },
            timeLike: { $sum: { $cond: [
              { $regexMatch: { input: "$shift.starts", regex: /^[0-2][0-9]:[0-5][0-9](:[0-5][0-9])?$/ } },
              1, 0] } } } }
      ]
  jq:
    entrada: |
      [{"starts": "11:50:40"}, {"starts": "07:00:00"}, {"starts": "23:15:00"}, {"starts": "14:30:00"}]
    filtro: |
      [.[].starts]
      | {types: (map(type) | unique), n: length,
         time_like: (map(select(test("^[0-2][0-9]:[0-5][0-9](:[0-5][0-9])?$"))) | length)}
  leitura: >-
    Todos os valores são strings com cara de horário. O BSON não tem um tipo só de hora, então o
    MongoDB e o jq checam o formato por expressão regular.
---
Compare o tipo declarado com aquilo em que os valores se convertem.
