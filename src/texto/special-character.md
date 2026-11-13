---
smell: Special Character
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE notes (id int, note text);
    INSERT INTO notes VALUES
      (1, 'Hello, how are you - today'), (2, 'New.York.'), (3, 'John''s house'), (4, 'Main Street');
  duckdb: |
    SELECT regexp_replace(note, '[A-Za-z0-9 ]', '', 'g') AS specials, count(*) AS n
    FROM notes
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT regexp_replace(note, '[A-Za-z0-9 ]', '', 'g') AS specials, count(*) AS n
    FROM notes
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, note: "Hello, how are you - today" }, { _id: 2, note: "New.York." },
        { _id: 3, note: "John's house" }, { _id: 4, note: "Main Street" }
      ]
    pipeline: |
      [
        { $set: { specials: { $reduce: {
            input: { $regexFindAll: { input: "$note", regex: /[^A-Za-z0-9 ]/ } },
            initialValue: "", in: { $concat: ["$$value", "$$this.match"] } } } } },
        { $group: { _id: "$specials", n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"note": "Hello, how are you - today"}, {"note": "New.York."},
       {"note": "John's house"}, {"note": "Main Street"}]
    filtro: |
      [.[].note | gsub("[A-Za-z0-9 ]"; "")]
      | group_by(.) | map({specials: .[0], n: length})[]
  leitura: Três dos quatro valores têm caracteres especiais; os pontos de `New.York.` não pertencem a um nome de cidade.
---
Apague letras, dígitos e espaços: o que sobra são os caracteres especiais de cada valor.
