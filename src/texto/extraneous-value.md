---
smell: Extraneous Value
exemplo:
  tarefa: value-length
  sql: |
    CREATE TABLE justices (id int, name text);
    INSERT INTO justices VALUES
      (1, 'John Roberts Jr.'), (2, 'CJ. John Roberts Jr.'), (3, 'Sonia Sotomayor'),
      (4, 'Elena Kagan'), (5, 'Justice Elena Kagan');
  duckdb: |
    SELECT len(string_split(name, ' ')) AS words, count(*) AS n, min(name) AS example
    FROM justices
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT cardinality(string_to_array(name, ' ')) AS words, count(*) AS n, min(name) AS example
    FROM justices
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, name: "John Roberts Jr." }, { _id: 2, name: "CJ. John Roberts Jr." },
        { _id: 3, name: "Sonia Sotomayor" }, { _id: 4, name: "Elena Kagan" },
        { _id: 5, name: "Justice Elena Kagan" }
      ]
    pipeline: |
      [
        { $group: { _id: { $size: { $split: ["$name", " "] } }, n: { $sum: 1 }, example: { $min: "$name" } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"name": "John Roberts Jr."}, {"name": "CJ. John Roberts Jr."}, {"name": "Sonia Sotomayor"},
       {"name": "Elena Kagan"}, {"name": "Justice Elena Kagan"}]
    filtro: |
      [.[].name] | group_by(split(" ") | length)
      | map({words: (.[0] | split(" ") | length), n: length, example: min})[]
  leitura: >-
    As mesmas pessoas aparecem com e sem título ("CJ.", "Justice"): o comprimento a mais é o
    título.
---
Aqui o comprimento é medido em palavras. Nomes de pessoas com uma palavra a mais que o comum costumam carregar um título ou sufixo.
