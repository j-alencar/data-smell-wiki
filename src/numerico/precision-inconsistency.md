---
smell: Precision Inconsistency
exemplo:
  tarefa: decimals
  sql: |
    CREATE TABLE weights (id int, kg double precision);
    INSERT INTO weights VALUES (1, 5.5485), (2, 7.45), (3, 8.21), (4, 8.5), (5, 9.887);
  duckdb: |
    SELECT length(split_part(CAST(kg AS VARCHAR), '.', 2)) AS decimals, count(*) AS n
    FROM weights
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT length(split_part(kg::text, '.', 2)) AS decimals, count(*) AS n
    FROM weights
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, kg: 5.5485 }, { _id: 2, kg: 7.45 }, { _id: 3, kg: 8.21 },
        { _id: 4, kg: 8.5 }, { _id: 5, kg: 9.887 }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $strLenCP: { $ifNull: [
              { $arrayElemAt: [{ $split: [{ $toString: "$kg" }, "."] }, 1] }, ""] } },
            n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"kg": 5.5485}, {"kg": 7.45}, {"kg": 8.21}, {"kg": 8.5}, {"kg": 9.887}]
    filtro: |
      [.[].kg | tostring | (split(".")[1] // "") | length]
      | group_by(.) | map({decimals: .[0], n: length})[]
  leitura: Quatro precisões diferentes em cinco valores; nenhuma domina.
---
Um histograma de casas decimais mostra se a coluna segue uma precisão.
