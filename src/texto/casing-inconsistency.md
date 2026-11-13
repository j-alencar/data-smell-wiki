---
smell: Casing Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE customers (id int, city text);
    INSERT INTO customers VALUES
      (1, 'Joinville'), (2, 'JOINVILLE'), (3, 'joinville'), (4, 'Curitiba'), (5, 'Blumenau');
  duckdb: |
    SELECT CASE WHEN city = upper(city) THEN 'UPPER'
                WHEN city = lower(city) THEN 'lower'
                ELSE 'Mixed' END AS casing,
           count(*) AS n
    FROM customers
    GROUP BY 1
    ORDER BY n DESC, casing;
  postgres: |
    SELECT CASE WHEN city = upper(city) THEN 'UPPER'
                WHEN city = lower(city) THEN 'lower'
                ELSE 'Mixed' END AS casing,
           count(*) AS n
    FROM customers
    GROUP BY 1
    ORDER BY n DESC, casing;
  mongo:
    docs: |
      [
        { _id: 1, address: { city: "Joinville" } }, { _id: 2, address: { city: "JOINVILLE" } },
        { _id: 3, address: { city: "joinville" } }, { _id: 4, address: { city: "Curitiba" } },
        { _id: 5, address: { city: "Blumenau" } }
      ]
    pipeline: |
      [
        { $group: { _id: { $switch: { branches: [
            { case: { $eq: ["$address.city", { $toUpper: "$address.city" }] }, then: "UPPER" },
            { case: { $eq: ["$address.city", { $toLower: "$address.city" }] }, then: "lower" } ],
            default: "Mixed" } }, n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [
        {"id": 1, "addresses": [{"city": "Joinville"}, {"city": "JOINVILLE"}]},
        {"id": 2, "addresses": [{"city": "joinville"}]},
        {"id": 3, "addresses": [{"city": "Curitiba"}, {"city": "Blumenau"}]}
      ]
    filtro: |
      [.[].addresses[].city
        | if . == ascii_upcase then "UPPER"
          elif . == ascii_downcase then "lower" else "Mixed" end]
      | group_by(.) | map({casing: .[0], n: length})
      | sort_by([-.n, .casing])[]
  leitura: A maioria segue uma caixa; as minorias UPPER e lower são a mesma cidade escrita de outro jeito.
---
Reduza cada valor à classe de caixa antes de contar. Padrões `Aa9` crus dependem do comprimento e escondem a caixa.
