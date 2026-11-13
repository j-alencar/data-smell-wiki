---
smell: Extraneous Value
exemplo:
  tarefa: value-length
  sql: |
    CREATE TABLE orders (id int, qty text);
    INSERT INTO orders VALUES (1, '12'), (2, '15'), (3, 'approx. 20'), (4, '18 (estimated)'), (5, '9');
  duckdb: |
    SELECT length(qty) AS len, count(*) AS n, min(qty) AS example
    FROM orders
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT length(qty) AS len, count(*) AS n, min(qty) AS example
    FROM orders
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, qty: "12" }, { _id: 2, qty: "15" }, { _id: 3, qty: "approx. 20" },
        { _id: 4, qty: "18 (estimated)" }, { _id: 5, qty: "9" }
      ]
    pipeline: |
      [
        { $group: { _id: { $strLenCP: "$qty" }, n: { $sum: 1 }, example: { $min: "$qty" } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"qty": "12"}, {"qty": "15"}, {"qty": "approx. 20"}, {"qty": "18 (estimated)"}, {"qty": "9"}]
    filtro: |
      [.[].qty] | group_by(length)
      | map({len: (.[0] | length), n: length, example: min})[]
  leitura: >-
    Quantidades têm 1 ou 2 caracteres; dois valores carregam um qualificador. Para guardá-los, a
    coluna já virou texto.
---
Um número com observação ("aprox.", "estimado") só cabe num campo de texto: o qualificador empurra o campo para fora do mundo numérico.
