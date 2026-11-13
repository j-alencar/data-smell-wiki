---
smell: Long Data Value
exemplo:
  tarefa: value-length
  sql: |
    CREATE TABLE alarms (id int, label text);
    INSERT INTO alarms VALUES
      (1, 'alarm'), (2, 'pressure high'), (3, 'Pneumonoultramicroscopicsilicovolcanoconiosis'),
      (4, '12Am12-12-20highpressalarmset0'), (5, 'door open');
  duckdb: |
    SELECT min(length(label)) AS min, max(length(label)) AS max,
           median(length(label)) AS median, round(avg(length(label)), 1) AS avg
    FROM alarms;
  postgres: |
    SELECT min(length(label)) AS min, max(length(label)) AS max,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY length(label)) AS median,
           round(avg(length(label)), 1) AS avg
    FROM alarms;
  mongo:
    docs: |
      [
        { _id: 1, label: "alarm" }, { _id: 2, label: "pressure high" },
        { _id: 3, label: "Pneumonoultramicroscopicsilicovolcanoconiosis" },
        { _id: 4, label: "12Am12-12-20highpressalarmset0" }, { _id: 5, label: "door open" }
      ]
    pipeline: |
      [
        { $set: { len: { $strLenCP: "$label" } } },
        { $group: { _id: null, min: { $min: "$len" }, max: { $max: "$len" },
            median: { $median: { input: "$len", method: "approximate" } }, avg: { $avg: "$len" } } },
        { $project: { _id: 0, min: 1, max: 1, median: 1, avg: { $round: ["$avg", 1] } } }
      ]
  jq:
    entrada: |
      [{"label": "alarm"}, {"label": "pressure high"},
       {"label": "Pneumonoultramicroscopicsilicovolcanoconiosis"},
       {"label": "12Am12-12-20highpressalarmset0"}, {"label": "door open"}]
    filtro: |
      [.[].label | length] | sort
      | {min: .[0], max: .[-1], median: .[length / 2 | floor],
         avg: ((add / length) * 10 | round / 10)}
  leitura: >-
    A mediana é 13 caracteres, mas o máximo é 45: dois rótulos são longos demais para leitura.
---
Compare o máximo com a mediana. Uma distância grande isola os valores longos demais.
