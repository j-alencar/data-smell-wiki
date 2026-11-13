---
smell: Meaningless Value
exemplo:
  tarefa: domain-classification
  sql: |
    CREATE TABLE people (id int, name text);
    INSERT INTO people VALUES (1, 'aaa'), (2, 'abcabc'), (3, '123412341234'), (4, 'Maria'), (5, 'Joinville');
  duckdb: |
    SELECT CASE WHEN len([k FOR k IN range(1, length(name))
                          IF length(name) % k = 0
                          AND repeat(name[1:k], length(name) // k) = name]) > 0
                THEN 'repeated sequence' ELSE 'text' END AS domain,
           count(*) AS n,
           string_agg(name, ', ' ORDER BY id) AS values
    FROM people
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT CASE WHEN name ~ '^(.+)\1+$' THEN 'repeated sequence' ELSE 'text' END AS domain,
           count(*) AS n,
           string_agg(name, ', ' ORDER BY id) AS values
    FROM people
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, name: "aaa" }, { _id: 2, name: "abcabc" }, { _id: 3, name: "123412341234" },
        { _id: 4, name: "Maria" }, { _id: 5, name: "Joinville" }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $cond: [{ $regexMatch: { input: "$name", regex: /^(.+)\1+$/ } },
                           "repeated sequence", "text"] },
            n: { $sum: 1 }, values: { $push: "$name" } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"name": "aaa"}, {"name": "abcabc"}, {"name": "123412341234"}, {"name": "Maria"}, {"name": "Joinville"}]
    filtro: |
      [.[].name] | group_by(if test("^(.+)\\1+$") then "repeated sequence" else "text" end)
      | map({domain: (if .[0] | test("^(.+)\\1+$") then "repeated sequence" else "text" end),
             n: length, values: .})[]
  leitura: Três "nomes" são só uma sequência repetida e não pertencem ao domínio de nomes de pessoa.
---
Uma regra de domínio simples: o valor é uma sequência curta repetida? O RE2 do DuckDB não tem retrovisor (`\1`), então a consulta testa cada tamanho de prefixo; PostgreSQL, MongoDB e jq usam a regex direto.
