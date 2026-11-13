---
smell: Syntax Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE contacts (id int, phone text);
    INSERT INTO contacts VALUES (1, '+43650123'), (2, '0043654124'), (3, '+43664123'), (4, '+43699111');
  duckdb: |
    SELECT pattern(phone) AS pattern, count(*) AS n
    FROM contacts
    GROUP BY 1
    ORDER BY n DESC;
  postgres: |
    SELECT pattern(phone) AS pattern, count(*) AS n
    FROM contacts
    GROUP BY 1
    ORDER BY n DESC;
  mongo:
    docs: |
      [
        { _id: 1, phone: "+43650123" }, { _id: 2, phone: "0043654124" },
        { _id: 3, phone: "+43664123" }, { _id: 4, phone: "+43699111" }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$phone"), n: { $sum: 1 } } },
        { $sort: { n: -1 } }
      ]
  jq:
    entrada: |
      [{"phone": "+43650123"}, {"phone": "0043654124"}, {"phone": "+43664123"}, {"phone": "+43699111"}]
    filtro: |
      [.[].phone | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by(-.n)[]
  leitura: O código do país aparece como `+43` e como `0043`. São duas sintaxes para a mesma coisa.
---
Uma sintaxe dominante com uma minoria diferente, para o mesmo tipo de valor, indica inconsistência.
