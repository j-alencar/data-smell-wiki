---
smell: Abbreviation Inconsistency
exemplo:
  tarefa: histogram
  sql: |
    CREATE TABLE staff (id int, name text);
    INSERT INTO staff VALUES
      (1, 'Dr. Hofer'), (2, 'Doctor Huber'), (3, 'Dr. Maier'), (4, 'Prof. Gruber'), (5, 'Doctor Wolf');
  duckdb: |
    SELECT split_part(name, ' ', 1) AS title, count(*) AS n
    FROM staff
    GROUP BY 1
    ORDER BY n DESC, title;
  postgres: |
    SELECT split_part(name, ' ', 1) AS title, count(*) AS n
    FROM staff
    GROUP BY 1
    ORDER BY n DESC, title;
  mongo:
    docs: |
      [
        { _id: 1, name: "Dr. Hofer" }, { _id: 2, name: "Doctor Huber" }, { _id: 3, name: "Dr. Maier" },
        { _id: 4, name: "Prof. Gruber" }, { _id: 5, name: "Doctor Wolf" }
      ]
    pipeline: |
      [
        { $group: { _id: { $arrayElemAt: [{ $split: ["$name", " "] }, 0] }, n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"name": "Dr. Hofer"}, {"name": "Doctor Huber"}, {"name": "Dr. Maier"},
       {"name": "Prof. Gruber"}, {"name": "Doctor Wolf"}]
    filtro: |
      [.[].name | split(" ")[0]]
      | group_by(.) | map({title: .[0], n: length})
      | sort_by([-.n, .title])[]
  leitura: "`Dr.` e `Doctor` dividem o mesmo título quase meio a meio."
---
Um histograma do primeiro token separa títulos abreviados dos escritos por extenso.
