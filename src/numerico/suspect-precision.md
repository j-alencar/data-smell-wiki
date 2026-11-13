---
smell: Suspect Precision
exemplo:
  tarefa: decimals
  sql: |
    CREATE TABLE readings (id int, ph double precision);
    INSERT INTO readings VALUES (1, 5.5), (2, 4.25), (3, 5.5458415569), (4, 3.75);
  duckdb: |
    SELECT length(split_part(CAST(ph AS VARCHAR), '.', 2)) AS decimals, count(*) AS n
    FROM readings
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT length(split_part(ph::text, '.', 2)) AS decimals, count(*) AS n
    FROM readings
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, reading: { ph: 5.5 } }, { _id: 2, reading: { ph: 4.25 } },
        { _id: 3, reading: { ph: 5.5458415569 } }, { _id: 4, reading: { ph: 3.75 } }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $strLenCP: { $ifNull: [
              { $arrayElemAt: [{ $split: [{ $toString: "$reading.ph" }, "."] }, 1] }, ""] } },
            n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"ph": 5.5}, {"ph": 4.25}, {"ph": 5.5458415569}, {"ph": 3.75}]
    filtro: |
      [.[].ph | tostring | (split(".")[1] // "") | length]
      | group_by(.) | map({decimals: .[0], n: length})[]
  leitura: Um valor tem 10 casas decimais; os demais têm 1 ou 2. Um pH com essa precisão é implausível.
---
Conte as casas decimais de cada valor. Uma cauda longa sugere precisão que o instrumento não tem.
