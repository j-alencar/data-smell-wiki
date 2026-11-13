---
smell: Intermingled Data Type
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE deliveries (id int, due text);
    INSERT INTO deliveries VALUES
      (1, '2021-03-05'), (2, '2021-03-06'), (3, 'Q1 2021'), (4, '2021-03-08'), (5, 'week 12');
  duckdb: |
    SELECT CASE WHEN TRY_CAST(due AS DATE) IS NOT NULL THEN 'date'
                WHEN regexp_full_match(due, '[0-9]+') THEN 'numeric'
                WHEN regexp_full_match(due, '[A-Za-z ]+') THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n
    FROM deliveries
    GROUP BY 1
    ORDER BY n DESC, basic_type;
  postgres: |
    SELECT CASE WHEN pg_input_is_valid(due, 'date') THEN 'date'
                WHEN due ~ '^[0-9]+$' THEN 'numeric'
                WHEN due ~ '^[A-Za-z ]+$' THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n
    FROM deliveries
    GROUP BY 1
    ORDER BY n DESC, basic_type;
  mongo:
    docs: |
      [
        { _id: 1, due: "2021-03-05" }, { _id: 2, due: "2021-03-06" }, { _id: 3, due: "Q1 2021" },
        { _id: 4, due: "2021-03-08" }, { _id: 5, due: "week 12" }
      ]
    pipeline: |
      [
        { $group: { _id: { $switch: { branches: [
            { case: { $ne: [{ $convert: { input: "$due", to: "date", onError: null } }, null] }, then: "date" },
            { case: { $regexMatch: { input: "$due", regex: /^[0-9]+$/ } }, then: "numeric" },
            { case: { $regexMatch: { input: "$due", regex: /^[A-Za-z ]+$/ } }, then: "alphabetic" } ],
            default: "alphanumeric" } }, n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"due": "2021-03-05"}, {"due": "2021-03-06"}, {"due": "Q1 2021"},
       {"due": "2021-03-08"}, {"due": "week 12"}]
    filtro: |
      [.[].due
        | if (try (strptime("%Y-%m-%d") | true) catch false) then "date"
          elif test("^[0-9]+$") then "numeric"
          elif test("^[A-Za-z ]+$") then "alphabetic" else "alphanumeric" end]
      | group_by(.) | map({basic_type: .[0], n: length})
      | sort_by([-.n, .basic_type])[]
  leitura: >-
    Dois valores não são datas: misturam letras e números para descrever um período ("Q1 2021",
    "week 12").
---
Em datas, a mistura costuma vir de períodos escritos por extenso no lugar de uma data.
