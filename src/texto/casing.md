---
smell: Casing
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE greetings (id int, msg text);
    INSERT INTO greetings VALUES
      (1, 'GoOD MorNiNg'), (2, 'GOOD MORNING'), (3, 'good morning'), (4, 'Good Morning'), (5, 'Good Evening');
  duckdb: |
    SELECT CASE WHEN msg = upper(msg) THEN 'UPPER'
                WHEN msg = lower(msg) THEN 'lower'
                WHEN regexp_full_match(msg, '[A-Z][a-z]*( [A-Z][a-z]*)*') THEN 'Title'
                ELSE 'Mixed' END AS casing,
           count(*) AS n
    FROM greetings
    GROUP BY 1
    ORDER BY n DESC, casing;
  postgres: |
    SELECT CASE WHEN msg = upper(msg) THEN 'UPPER'
                WHEN msg = lower(msg) THEN 'lower'
                WHEN msg = initcap(msg) THEN 'Title'
                ELSE 'Mixed' END AS casing,
           count(*) AS n
    FROM greetings
    GROUP BY 1
    ORDER BY n DESC, casing;
  mongo:
    docs: |
      [
        { _id: 1, msg: "GoOD MorNiNg" }, { _id: 2, msg: "GOOD MORNING" }, { _id: 3, msg: "good morning" },
        { _id: 4, msg: "Good Morning" }, { _id: 5, msg: "Good Evening" }
      ]
    pipeline: |
      [
        { $group: { _id: { $switch: { branches: [
            { case: { $eq: ["$msg", { $toUpper: "$msg" }] }, then: "UPPER" },
            { case: { $eq: ["$msg", { $toLower: "$msg" }] }, then: "lower" },
            { case: { $regexMatch: { input: "$msg", regex: /^[A-Z][a-z]*( [A-Z][a-z]*)*$/ } }, then: "Title" } ],
            default: "Mixed" } }, n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"msg": "GoOD MorNiNg"}, {"msg": "GOOD MORNING"}, {"msg": "good morning"},
       {"msg": "Good Morning"}, {"msg": "Good Evening"}]
    filtro: |
      [.[].msg
        | if . == ascii_upcase then "UPPER" elif . == ascii_downcase then "lower"
          elif test("^[A-Z][a-z]*( [A-Z][a-z]*)*$") then "Title" else "Mixed" end]
      | group_by(.) | map({casing: .[0], n: length})
      | sort_by([-.n, .casing])[]
  leitura: >-
    `GoOD MorNiNg` é o caso "Mixed": maiúsculas fora de qualquer regra. Só maiúsculas ou só
    minúsculas também contam como uso incomum, conforme o contexto.
---
Reduza cada valor à sua classe de caixa: UPPER, lower, Title ou Mixed. O PostgreSQL tem `initcap`; nos demais, uma regex faz o mesmo.
