---
smell: Floating-point Number as String
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE products (id int, price text);
    INSERT INTO products VALUES (1, '3.5'), (2, '12.25'), (3, '0.75'), (4, '8.0');
  duckdb: |
    SELECT typeof(price) AS data_type, pattern(price) AS pattern, count(*) AS n
    FROM products
    GROUP BY ALL
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pg_typeof(price)::text AS data_type, pattern(price) AS pattern, count(*) AS n
    FROM products
    GROUP BY 1, 2
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, product: { price: "3.5" } }, { _id: 2, product: { price: "12.25" } },
        { _id: 3, product: { price: "0.75" } }, { _id: 4, product: { price: "8.0" } }
      ]
    pipeline: |
      [
        { $group: { _id: { type: { $type: "$product.price" }, pattern: pattern("$product.price") },
                    n: { $sum: 1 } } },
        { $sort: { n: -1, "_id.pattern": 1 } }
      ]
  jq:
    entrada: |
      [{"price": "3.5"}, {"price": "12.25"}, {"price": "0.75"}, {"price": "8.0"}]
    filtro: |
      [.[].price] | group_by(pattern)
      | map({type: (.[0] | type), pattern: (.[0] | pattern), n: length})
      | sort_by([-.n, .pattern])[]
  leitura: Todo valor segue `9...9.9...9`, mas a coluna é texto.
---
Padrões só com dígitos e ponto decimal num campo de texto indicam um número guardado como string.
