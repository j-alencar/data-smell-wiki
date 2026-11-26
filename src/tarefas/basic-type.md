---
exemplos:
  - id: base
    titulo: classificação por caracteres e intervalos
    sql: |
      CREATE TABLE raw (id int, v text);
      INSERT INTO raw VALUES
        (1, '42'), (2, '3.14'), (3, 'abc'), (4, 'R2D2'),
        (5, '2024-05-01'), (6, '2024-13-45'), (7, '13:45'), (8, '25:99');
    duckdb: |
      SELECT CASE
               WHEN regexp_full_match(v, '\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])') THEN 'date'
               WHEN regexp_full_match(v, '([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?') THEN 'time'
               WHEN regexp_full_match(v, '-?\d+(\.\d+)?') THEN 'numeric'
               WHEN regexp_full_match(v, '[A-Za-z]+') THEN 'alphabetic'
               WHEN regexp_full_match(v, '[A-Za-z0-9]+') THEN 'alphanumeric'
               ELSE 'other' END AS basic_type,
             count(*) AS n,
             string_agg(v, ', ' ORDER BY id) AS vals
      FROM raw
      GROUP BY 1
      ORDER BY min(id);
    postgres: |
      SELECT CASE
               WHEN v ~ '^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$' THEN 'date'
               WHEN v ~ '^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$' THEN 'time'
               WHEN v ~ '^-?\d+(\.\d+)?$' THEN 'numeric'
               WHEN v ~ '^[A-Za-z]+$' THEN 'alphabetic'
               WHEN v ~ '^[A-Za-z0-9]+$' THEN 'alphanumeric'
               ELSE 'other' END AS basic_type,
             count(*) AS n,
             string_agg(v, ', ' ORDER BY id) AS vals
      FROM raw
      GROUP BY 1
      ORDER BY min(id);
    mongo:
      docs: |
        ["42", "3.14", "abc", "R2D2", "2024-05-01", "2024-13-45", "13:45", "25:99"]
          .map((v, i) => ({ _id: i + 1, v }))
      pipeline: |
        [
          { $set: { basic_type: { $switch: { branches: [
              { case: { $regexMatch: { input: "$v", regex: /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/ } }, then: "date" },
              { case: { $regexMatch: { input: "$v", regex: /^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/ } }, then: "time" },
              { case: { $regexMatch: { input: "$v", regex: /^-?\d+(\.\d+)?$/ } }, then: "numeric" },
              { case: { $regexMatch: { input: "$v", regex: /^[A-Za-z]+$/ } }, then: "alphabetic" },
              { case: { $regexMatch: { input: "$v", regex: /^[A-Za-z0-9]+$/ } }, then: "alphanumeric" } ],
              default: "other" } } } },
          { $sort: { _id: 1 } },
          { $group: { _id: "$basic_type", first: { $min: "$_id" }, n: { $sum: 1 }, vals: { $push: "$v" } } },
          { $sort: { first: 1 } },
          { $project: { _id: 0, basic_type: "$_id", n: "$n", vals: "$vals" } }
        ]
    jq:
      entrada: |
        ["42", "3.14", "abc", "R2D2", "2024-05-01", "2024-13-45", "13:45", "25:99"]
      filtro: |
        def basic_type:
          if test("^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$") then "date"
          elif test("^([01]\\d|2[0-3]):[0-5]\\d(:[0-5]\\d)?$") then "time"
          elif test("^-?\\d+(\\.\\d+)?$") then "numeric"
          elif test("^[A-Za-z]+$") then "alphabetic"
          elif test("^[A-Za-z0-9]+$") then "alphanumeric"
          else "other" end;
        [to_entries[] | {i: .key, v: .value, basic_type: (.value | basic_type)}]
        | group_by(.basic_type) | sort_by(.[0].i)
        | map({basic_type: .[0].basic_type, n: length, vals: map(.v)})[]
    leitura: >-
      `2024-13-45` e `25:99` têm a forma de data e hora, mas os números saem dos intervalos válidos
      (mês 13, minuto 99) e caem em `other`. Numa coluna real, o tipo básico é o da maioria; os
      demais valores são os suspeitos.
---
Classificar uma coluna como numérica, alfabética, alfanumérica, data ou hora é simples. A presença ou ausência de caracteres numéricos e não numéricos separa os três primeiros tipos. Datas e horas se reconhecem por números dentro de certos intervalos, separados em padrões regulares por símbolos especiais (ABEDJAN; GOLAB; NAUMANN, 2015).

O tipo básico antecede o [tipo de dado](/tarefas/data-type/) concreto. Para tipos decimais, extraia também dígitos e casas: veja [Casas decimais](/tarefas/decimals/).

Os exemplos testam as classes da mais específica para a mais geral: `42` também casaria com `alphanumeric`, mas para em `numeric`.
