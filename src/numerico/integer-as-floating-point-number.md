---
smell: Integer as Floating-point Number
exemplo:
  tarefa: data-type
  sql: |
    CREATE TABLE stock (id int, qty double precision);
    INSERT INTO stock VALUES (1, 3.0), (2, 12.0), (3, 7.0), (4, 5.0);
  duckdb: |
    SELECT typeof(qty) AS data_type,
           count(*) AS n,
           count(*) FILTER (WHERE qty = floor(qty)) AS integral
    FROM stock
    GROUP BY 1;
  postgres: |
    SELECT pg_typeof(qty)::text AS data_type,
           count(*) AS n,
           count(*) FILTER (WHERE qty = floor(qty)) AS integral
    FROM stock
    GROUP BY 1;
  mongo:
    docs: |
      [
        { _id: 1, item: { qty: Double(3) } }, { _id: 2, item: { qty: Double(12) } },
        { _id: 3, item: { qty: Double(7) } }, { _id: 4, item: { qty: Double(5) } }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $type: "$item.qty" },
            n: { $sum: 1 },
            integral: { $sum: { $cond: [{ $eq: ["$item.qty", { $trunc: "$item.qty" }] }, 1, 0] } } } }
      ]
  jq:
    na: >-
      JSON tem um único tipo `number`; o jq lê `3.0` e `3` como o mesmo valor, então não há tipo de
      ponto flutuante para detectar.
  leitura: >-
    A coluna é de ponto flutuante, mas todo valor é inteiro. O MongoDB também mostra o problema,
    porque o BSON distingue `double` de `int`.
---
Compare o tipo declarado com as casas decimais que os valores realmente usam.
