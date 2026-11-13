---
smell: Spacing Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE contacts (id int, phone text);
    INSERT INTO contacts VALUES (1, '+43 664 123'), (2, '+43664 546'), (3, '+43 650 123'), (4, '+43699 111');
  duckdb: |
    SELECT pattern(phone) AS pattern, count(*) AS n
    FROM contacts
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(phone) AS pattern, count(*) AS n
    FROM contacts
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, phone: "+43 664 123" }, { _id: 2, phone: "+43664 546" },
        { _id: 3, phone: "+43 650 123" }, { _id: 4, phone: "+43699 111" }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$phone"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"phone": "+43 664 123"}, {"phone": "+43664 546"}, {"phone": "+43 650 123"}, {"phone": "+43699 111"}]
    filtro: |
      [.[].phone | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: Metade dos telefones separa o código de área com espaço; a outra metade, não.
---
Padrões que só diferem na posição dos espaços indicam espaçamento inconsistente.
