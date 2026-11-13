---
smell: Missing Value Inconsistency
exemplo:
  tarefa: null-values
  sql: |
    CREATE TABLE readings (id int, temp text);
    INSERT INTO readings VALUES
      (1, '12'), (2, 'NaN'), (3, 'Na'), (4, 'NULL'), (5, '22'), (6, 'inf'), (7, '23'), (8, NULL);
  duckdb: |
    SELECT coalesce(temp, '(NULL)')  AS value,
           count(*)                  AS n,
           TRY_CAST(temp AS DOUBLE)  AS as_double
    FROM readings
    WHERE temp IS NULL OR NOT regexp_full_match(temp, '-?[0-9]+(\.[0-9]+)?')
    GROUP BY 1, 3
    ORDER BY 1;
  postgres: |
    SELECT coalesce(temp, '(NULL)') AS value,
           count(*) AS n,
           CASE WHEN pg_input_is_valid(temp, 'float8') THEN temp::float8 END AS as_double
    FROM readings
    WHERE temp IS NULL OR temp !~ '^-?[0-9]+(\.[0-9]+)?$'
    GROUP BY 1, 3
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, temp: "12" }, { _id: 2, temp: "NaN" }, { _id: 3, temp: "Na" },
        { _id: 4, temp: null }, { _id: 5, temp: "22" }, { _id: 6, temp: "inf" },
        { _id: 7, temp: "23" }, { _id: 8 }
      ]
    pipeline: |
      [
        { $match: { $expr: { $not: { $regexMatch: {
            input: { $ifNull: ["$temp", ""] }, regex: /^-?[0-9]+(\.[0-9]+)?$/ } } } } },
        { $group: {
            _id: { $switch: { branches: [
              { case: { $eq: [{ $type: "$temp" }, "missing"] }, then: "(campo ausente)" },
              { case: { $eq: ["$temp", null] }, then: "(null)" } ], default: "$temp" } },
            n: { $sum: 1 },
            asDouble: { $first: { $convert: { input: "$temp", to: "double", onError: "erro", onNull: null } } } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"temp": "12"}, {"temp": "NaN"}, {"temp": "Na"}, {"temp": null}, {"temp": "22"},
       {"temp": "inf"}, {"temp": "23"}, {}]
    filtro: |
      [.[] | if has("temp") | not then {value: "(campo ausente)", as_number: null}
             elif .temp == null then {value: "(null)", as_number: null}
             elif (.temp | test("^-?[0-9]+(\\.[0-9]+)?$")) then empty
             else {value: .temp, as_number: (.temp | try tonumber catch "erro")} end]
      | group_by(.value) | map(.[0] + {n: length})[]
  leitura: >-
    Cinco formas de "sem leitura" em cada motor. Cuidado: DuckDB, PostgreSQL e MongoDB convertem
    `"NaN"` e `"inf"` em número de ponto flutuante, então um filtro "converte em número?" deixa
    esses dois passarem. O jq converte `"NaN"` em `null` e `"inf"` no maior double.
---
Procure tudo que não é um número escrito do jeito esperado, incluindo os nulos de verdade.
