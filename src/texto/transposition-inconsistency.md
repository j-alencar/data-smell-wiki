---
smell: Transposition Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE menu (id int, price text);
    INSERT INTO menu VALUES (1, '€10.5'), (2, '11.0€'), (3, '€9.9'), (4, '€12.0');
  duckdb: |
    SELECT pattern(price) AS pattern, count(*) AS n
    FROM menu
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(price) AS pattern, count(*) AS n
    FROM menu
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, item: { price: "€10.5" } }, { _id: 2, item: { price: "11.0€" } },
        { _id: 3, item: { price: "€9.9" } }, { _id: 4, item: { price: "€12.0" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$item.price"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"price": "€10.5"}, {"price": "11.0€"}, {"price": "€9.9"}, {"price": "€12.0"}]
    filtro: |
      [.[].price | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: O símbolo `€` vem antes do número em três valores e depois em um (`99.9€`).
---
Mesmos elementos em ordem diferente aparecem como padrões espelhados.
