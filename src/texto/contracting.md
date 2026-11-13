---
smell: Contracting
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE replies (id int, reply text);
    INSERT INTO replies VALUES (1, 'don''t'), (2, 'I''d'), (3, 'do not'), (4, 'I would'), (5, 'can''t');
  duckdb: |
    SELECT pattern(reply) AS pattern, count(*) AS n
    FROM replies
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(reply) AS pattern, count(*) AS n
    FROM replies
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, reply: "don't" }, { _id: 2, reply: "I'd" }, { _id: 3, reply: "do not" },
        { _id: 4, reply: "I would" }, { _id: 5, reply: "can't" }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$reply"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"reply": "don't"}, {"reply": "I'd"}, {"reply": "do not"}, {"reply": "I would"}, {"reply": "can't"}]
    filtro: |
      [.[].reply | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: Os padrões com apóstrofo entre letras (`aaa'a`, `A'a`) são contrações.
---
Um apóstrofo entre letras no padrão marca uma forma contraída.
