---
smell: Missing Value Inconsistency
exemplo:
  tarefa: null-values
  sql: |
    CREATE TABLE visits (id int, visited_on text);
    INSERT INTO visits VALUES
      (1, '2021-03-05'), (2, NULL), (3, ''), (4, 'N/A'),
      (5, '0000-00-00'), (6, '2021-03-07'), (7, 'NULL');
  duckdb: |
    SELECT coalesce('"' || visited_on || '"', '(NULL)') AS missing_as, count(*) AS n
    FROM visits
    WHERE TRY_CAST(visited_on AS DATE) IS NULL
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT coalesce('"' || visited_on || '"', '(NULL)') AS missing_as, count(*) AS n
    FROM visits
    WHERE visited_on IS NULL OR NOT pg_input_is_valid(visited_on, 'date')
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, visitedOn: "2021-03-05" }, { _id: 2, visitedOn: null }, { _id: 3, visitedOn: "" },
        { _id: 4, visitedOn: "N/A" }, { _id: 5, visitedOn: "0000-00-00" },
        { _id: 6, visitedOn: "2021-03-07" }, { _id: 7 }
      ]
    pipeline: |
      [
        { $match: { $expr: { $eq: [
            { $convert: { input: "$visitedOn", to: "date", onError: null, onNull: null } }, null] } } },
        { $group: { _id: { $switch: { branches: [
            { case: { $eq: [{ $type: "$visitedOn" }, "missing"] }, then: "(campo ausente)" },
            { case: { $eq: ["$visitedOn", null] }, then: "(null)" } ],
            default: { $concat: ['"', "$visitedOn", '"'] } } }, n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"visitedOn": "2021-03-05"}, {"visitedOn": null}, {"visitedOn": ""}, {"visitedOn": "N/A"},
       {"visitedOn": "0000-00-00"}, {"visitedOn": "2021-03-07"}, {}]
    filtro: |
      [.[] | if has("visitedOn") | not then "(campo ausente)"
             elif .visitedOn == null then "(null)"
             elif (try (.visitedOn | strptime("%Y-%m-%d") | mktime | true) catch false) then empty
             else "\"" + .visitedOn + "\"" end]
      | group_by(.) | map({missing_as: .[0], n: length})[]
  leitura: >-
    Cinco formas de dizer "sem data" na mesma coluna. Em documentos, o campo ausente é mais uma
    forma, distinta de `null`.
---
Liste tudo o que não se converte em data: as formas de "vazio" aparecem juntas.
