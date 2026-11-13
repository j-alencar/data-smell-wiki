---
smell: Intermingled Data Type
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE parts (id int, code text);
    INSERT INTO parts VALUES (1, '7034'), (2, '7O34'), (3, '5120'), (4, '8812');
  duckdb: |
    SELECT CASE WHEN regexp_full_match(code, '[0-9]+') THEN 'numeric'
                WHEN regexp_full_match(code, '[A-Za-z]+') THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n,
           min(code) AS example
    FROM parts
    GROUP BY 1
    ORDER BY n DESC;
  postgres: |
    SELECT CASE WHEN code ~ '^[0-9]+$' THEN 'numeric'
                WHEN code ~ '^[A-Za-z]+$' THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n,
           min(code) AS example
    FROM parts
    GROUP BY 1
    ORDER BY n DESC;
  mongo:
    docs: |
      [
        { _id: 1, part: { code: "7034" } }, { _id: 2, part: { code: "7O34" } },
        { _id: 3, part: { code: "5120" } }, { _id: 4, part: { code: "8812" } }
      ]
    pipeline: |
      [
        { $group: { _id: { $switch: { branches: [
            { case: { $regexMatch: { input: "$part.code", regex: /^[0-9]+$/ } }, then: "numeric" },
            { case: { $regexMatch: { input: "$part.code", regex: /^[A-Za-z]+$/ } }, then: "alphabetic" } ],
            default: "alphanumeric" } }, n: { $sum: 1 }, example: { $min: "$part.code" } } },
        { $sort: { n: -1 } }
      ]
  jq:
    entrada: |
      [{"code": "7034"}, {"code": "7O34"}, {"code": "5120"}, {"code": "8812"}]
    filtro: |
      [.[].code | {code: .,
        basic_type: (if test("^[0-9]+$") then "numeric"
                     elif test("^[A-Za-z]+$") then "alphabetic" else "alphanumeric" end)}]
      | group_by(.basic_type)
      | map({basic_type: .[0].basic_type, n: length, example: (map(.code) | min)})
      | sort_by(-.n)[]
  leitura: >-
    `7O34` traz a letra O no lugar do zero: um caractere alfabético num campo que deveria ser só
    numérico.
---
Num código numérico, uma letra parecida com um dígito (O e 0, l e 1) muda o tipo básico do valor.
