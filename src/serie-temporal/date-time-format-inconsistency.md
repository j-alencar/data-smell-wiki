---
smell: Date/Time Format Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE payments (id int, paid_on text);
    INSERT INTO payments VALUES
      (1, '2020-01-30'), (2, '30-01-2020'), (3, '20-01-30'), (4, '2020-02-14'), (5, '2020-03-02');
  duckdb: |
    SELECT pattern(paid_on) AS pattern, count(*) AS n
    FROM payments
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(paid_on) AS pattern, count(*) AS n
    FROM payments
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, payment: { paidOn: "2020-01-30" } }, { _id: 2, payment: { paidOn: "30-01-2020" } },
        { _id: 3, payment: { paidOn: "20-01-30" } }, { _id: 4, payment: { paidOn: "2020-02-14" } },
        { _id: 5, payment: { paidOn: "2020-03-02" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$payment.paidOn"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"paidOn": "2020-01-30"}, {"paidOn": "30-01-2020"}, {"paidOn": "20-01-30"},
       {"paidOn": "2020-02-14"}, {"paidOn": "2020-03-02"}]
    filtro: |
      [.[].paidOn | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: Três formatos de data na mesma coluna. O padrão minoritário `99-99-99` também é ambíguo.
---
Mais de um padrão de data na mesma coluna indica formatos misturados.
