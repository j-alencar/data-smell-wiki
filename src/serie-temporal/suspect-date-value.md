---
smell: Suspect Date Value
exemplo:
  tarefa: histogram
  sql: |
    CREATE TABLE inspections (id int, inspected_on date);
    INSERT INTO inspections VALUES
      (1, '1899-03-22'), (2, '2019-05-02'), (3, '2020-01-14'),
      (4, '2020-07-30'), (5, '2021-03-11'), (6, '2099-03-02');
  duckdb: |
    SELECT (year(inspected_on) // 10) * 10 AS decade, count(*) AS n
    FROM inspections
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT (extract(year FROM inspected_on)::int / 10) * 10 AS decade, count(*) AS n
    FROM inspections
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, inspectedOn: new Date("1899-03-22") }, { _id: 2, inspectedOn: new Date("2019-05-02") },
        { _id: 3, inspectedOn: new Date("2020-01-14") }, { _id: 4, inspectedOn: new Date("2020-07-30") },
        { _id: 5, inspectedOn: new Date("2021-03-11") }, { _id: 6, inspectedOn: new Date("2099-03-02") }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $multiply: [{ $floor: { $divide: [{ $year: "$inspectedOn" }, 10] } }, 10] },
            n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"inspectedOn": "1899-03-22"}, {"inspectedOn": "2019-05-02"}, {"inspectedOn": "2020-01-14"},
       {"inspectedOn": "2020-07-30"}, {"inspectedOn": "2021-03-11"}, {"inspectedOn": "2099-03-02"}]
    filtro: |
      [.[].inspectedOn[0:4] | tonumber / 10 | floor * 10]
      | group_by(.) | map({decade: .[0], n: length})[]
  leitura: As décadas de 1890 e 2090 estão longe do restante; são datas implausíveis para uma inspeção.
---
Agrupe as datas em faixas largas (décadas) para que os extremos fiquem isolados.
