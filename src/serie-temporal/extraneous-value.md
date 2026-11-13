---
smell: Extraneous Value
exemplo:
  tarefa: value-length
  sql: |
    CREATE TABLE logins (id int, logged_on text);
    INSERT INTO logins VALUES
      (1, '2021-03-05'), (2, '2021-03-08'), (3, 'Fri Mar 05 2021'), (4, '2021-03-09 UTC');
  duckdb: |
    SELECT length(logged_on) AS len, count(*) AS n, min(logged_on) AS example
    FROM logins
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT length(logged_on) AS len, count(*) AS n, min(logged_on) AS example
    FROM logins
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, login: { on: "2021-03-05" } }, { _id: 2, login: { on: "2021-03-08" } },
        { _id: 3, login: { on: "Fri Mar 05 2021" } }, { _id: 4, login: { on: "2021-03-09 UTC" } }
      ]
    pipeline: |
      [
        { $group: { _id: { $strLenCP: "$login.on" }, n: { $sum: 1 }, example: { $min: "$login.on" } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"on": "2021-03-05"}, {"on": "2021-03-08"}, {"on": "Fri Mar 05 2021"}, {"on": "2021-03-09 UTC"}]
    filtro: |
      [.[].on] | group_by(length)
      | map({len: (.[0] | length), n: length, example: min})[]
  leitura: >-
    Uma data ISO tem 10 caracteres. Os valores mais longos trazem um dia da semana ou um fuso
    horário a mais.
---
Em datas, a informação a mais costuma ser um dia da semana como prefixo, um fuso horário como sufixo ou qualificadores como "c. 1950". Um comprimento acima do esperado para o formato denuncia isso.
