---
smell: Spacing
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE people (id int, name text);
    INSERT INTO people VALUES (1, 'JohnSmith '), (2, 'John  Smith'), (3, '  John  Smith'), (4, 'John Smith');
  duckdb: |
    SELECT count(*) FILTER (WHERE name <> trim(name))                AS leading_or_trailing,
           count(*) FILTER (WHERE name LIKE '%  %')                  AS multiple,
           count(*) FILTER (WHERE regexp_matches(name, '[a-z][A-Z]')) AS missing,
           count(*) AS n
    FROM people;
  postgres: |
    SELECT count(*) FILTER (WHERE name <> btrim(name))     AS leading_or_trailing,
           count(*) FILTER (WHERE name LIKE '%  %')        AS multiple,
           count(*) FILTER (WHERE name ~ '[a-z][A-Z]')     AS missing,
           count(*) AS n
    FROM people;
  mongo:
    docs: |
      [
        { _id: 1, name: "JohnSmith " }, { _id: 2, name: "John  Smith" },
        { _id: 3, name: "  John  Smith" }, { _id: 4, name: "John Smith" }
      ]
    pipeline: |
      [
        { $group: { _id: null,
            leading_or_trailing: { $sum: { $cond: [{ $ne: ["$name", { $trim: { input: "$name" } }] }, 1, 0] } },
            multiple: { $sum: { $cond: [{ $regexMatch: { input: "$name", regex: /  / } }, 1, 0] } },
            missing: { $sum: { $cond: [{ $regexMatch: { input: "$name", regex: /[a-z][A-Z]/ } }, 1, 0] } },
            n: { $sum: 1 } } },
        { $project: { _id: 0 } }
      ]
  jq:
    entrada: |
      [{"name": "JohnSmith "}, {"name": "John  Smith"}, {"name": "  John  Smith"}, {"name": "John Smith"}]
    filtro: |
      [.[].name]
      | {leading_or_trailing: map(select(test("^ | $"))) | length,
         multiple: (map(select(test("  "))) | length),
         missing: (map(select(test("[a-z][A-Z]"))) | length),
         n: length}
  leitura: >-
    Três dos quatro nomes têm espaço sobrando ou faltando. Só `John Smith` está limpo.
---
Conte os três desvios de espaçamento: nas pontas, repetido e ausente entre palavras.
