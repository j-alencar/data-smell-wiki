---
exemplos:
  - id: base
    titulo: dígitos e casas para escolher o DECIMAL
    sql: |
      CREATE TABLE readings (id int, v text);
      INSERT INTO readings VALUES (1, '12.5'), (2, '3.14159'), (3, '100'), (4, '0.25'), (5, '7.125');
    duckdb: |
      SELECT max(length(regexp_replace(v, '[^0-9]', '', 'g'))) AS size,
             max(length(split_part(v, '.', 1))) AS int_digits,
             max(length(split_part(v, '.', 2))) AS decimals,
             format('DECIMAL({}, {})', max(length(split_part(v, '.', 1))) + max(length(split_part(v, '.', 2))),
                    max(length(split_part(v, '.', 2)))) AS fits
      FROM readings;
    postgres: |
      SELECT max(length(regexp_replace(v, '[^0-9]', '', 'g'))) AS size,
             max(length(split_part(v, '.', 1))) AS int_digits,
             max(length(split_part(v, '.', 2))) AS decimals,
             format('DECIMAL(%s, %s)', max(length(split_part(v, '.', 1))) + max(length(split_part(v, '.', 2))),
                    max(length(split_part(v, '.', 2)))) AS fits
      FROM readings;
    mongo:
      docs: |
        ["12.5", "3.14159", "100", "0.25", "7.125"].map((v, i) => ({ _id: i + 1, v }))
      pipeline: |
        [
          { $set: { p: { $split: ["$v", "."] } } },
          { $set: { i: { $strLenCP: { $arrayElemAt: ["$p", 0] } },
                    d: { $strLenCP: { $ifNull: [{ $arrayElemAt: ["$p", 1] }, ""] } } } },
          { $group: { _id: null, size: { $max: { $add: ["$i", "$d"] } },
              int_digits: { $max: "$i" }, decimals: { $max: "$d" } } },
          { $project: { _id: 0, size: 1, int_digits: 1, decimals: 1,
              fits: { $concat: ["DECIMAL(", { $toString: { $add: ["$int_digits", "$decimals"] } }, ", ",
                                { $toString: "$decimals" }, ")"] } } }
        ]
    jq:
      entrada: |
        ["12.5", "3.14159", "100", "0.25", "7.125"]
      filtro: |
        map(split(".") | {i: (.[0] | length), d: (.[1] // "" | length)})
        | {size: (map(.i + .d) | max), int_digits: (map(.i) | max), decimals: (map(.d) | max)}
        | .fits = "DECIMAL(\(.int_digits + .decimals), \(.decimals))"
    leitura: >-
      O maior número de dígitos é 6 (`3.14159`) e o de casas é 5. Mas `100` pede 3 dígitos inteiros,
      então a coluna só cabe sem perda em `DECIMAL(8, 5)`. Os valores chegam como texto de propósito:
      num `double`, a representação decimal depende do motor.
---
Para os tipos decimal, float e double, extraia o número máximo de dígitos e de casas decimais. Os dois números dão os metadados *size* e *decimals* da coluna (ABEDJAN; GOLAB; NAUMANN, 2015) e definem a precisão e a escala de um tipo `DECIMAL(p, s)`.

Casas decimais demais ou em número variável são, elas mesmas, data smells: veja os smells ligados a esta tarefa abaixo.
