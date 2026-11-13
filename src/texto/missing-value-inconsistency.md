---
smell: Missing Value Inconsistency
exemplo:
  tarefa: null-values
  sql: |
    CREATE TABLE customers (id int, city text);
    INSERT INTO customers VALUES
      (1, 'Joinville'), (2, NULL), (3, ''), (4, 'N/A'), (5, '-'), (6, 'Curitiba'), (7, 'null');
  duckdb: |
    SELECT coalesce('"' || city || '"', '(NULL)') AS missing_as, count(*) AS n
    FROM customers
    WHERE city IS NULL OR trim(city) IN ('', '-', 'N/A', 'null')
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT coalesce('"' || city || '"', '(NULL)') AS missing_as, count(*) AS n
    FROM customers
    WHERE city IS NULL OR btrim(city) IN ('', '-', 'N/A', 'null')
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, city: "Joinville" }, { _id: 2, city: null }, { _id: 3, city: "" },
        { _id: 4, city: "N/A" }, { _id: 5, city: "-" }, { _id: 6, city: "Curitiba" }, { _id: 7 }
      ]
    pipeline: |
      [
        { $match: { $or: [{ city: { $exists: false } }, { city: null },
                          { city: { $in: ["", "-", "N/A", "null"] } }] } },
        { $group: { _id: { $switch: { branches: [
            { case: { $eq: [{ $type: "$city" }, "missing"] }, then: "(campo ausente)" },
            { case: { $eq: ["$city", null] }, then: "(null)" } ],
            default: { $concat: ['"', "$city", '"'] } } }, n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"city": "Joinville"}, {"city": null}, {"city": ""}, {"city": "N/A"},
       {"city": "-"}, {"city": "Curitiba"}, {}]
    filtro: |
      [.[] | if has("city") | not then "(campo ausente)"
             elif .city == null then "(null)"
             elif (.city | IN("", "-", "N/A", "null")) then "\"" + .city + "\""
             else empty end]
      | group_by(.) | map({missing_as: .[0], n: length})[]
  leitura: >-
    Cinco formas de "sem cidade". A lista de marcadores é uma suposição; ajuste-a ao que aparece
    nos dados, por exemplo olhando os valores mais curtos ou mais frequentes.
---
Em texto, o "vazio" pode ser `NULL`, string vazia ou uma palavra-marcador. Conte cada forma.
