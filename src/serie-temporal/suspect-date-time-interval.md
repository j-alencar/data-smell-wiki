---
smell: Suspect Date/Time Interval
exemplo:
  tarefa: histogram
  sql: |
    CREATE TABLE backups (id int, ran_on date);
    INSERT INTO backups VALUES
      (1, '2019-01-01'), (2, '2019-01-02'), (3, '2019-10-01'), (4, '2019-10-02'), (5, '2019-10-03');
  duckdb: |
    SELECT gap_days, count(*) AS n
    FROM (SELECT ran_on - lag(ran_on) OVER (ORDER BY ran_on) AS gap_days FROM backups)
    WHERE gap_days IS NOT NULL
    GROUP BY 1
    ORDER BY 1;
  postgres: |
    SELECT gap_days, count(*) AS n
    FROM (SELECT ran_on - lag(ran_on) OVER (ORDER BY ran_on) AS gap_days FROM backups) g
    WHERE gap_days IS NOT NULL
    GROUP BY 1
    ORDER BY 1;
  mongo:
    docs: |
      [
        { _id: 1, ranOn: new Date("2019-01-01") }, { _id: 2, ranOn: new Date("2019-01-02") },
        { _id: 3, ranOn: new Date("2019-10-01") }, { _id: 4, ranOn: new Date("2019-10-02") },
        { _id: 5, ranOn: new Date("2019-10-03") }
      ]
    pipeline: |
      [
        { $setWindowFields: { sortBy: { ranOn: 1 },
            output: { prev: { $shift: { output: "$ranOn", by: -1 } } } } },
        { $match: { prev: { $ne: null } } },
        { $group: { _id: { $dateDiff: { startDate: "$prev", endDate: "$ranOn", unit: "day" } },
                    n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"ranOn": "2019-01-01"}, {"ranOn": "2019-01-02"}, {"ranOn": "2019-10-01"},
       {"ranOn": "2019-10-02"}, {"ranOn": "2019-10-03"}]
    filtro: |
      [.[].ranOn | strptime("%Y-%m-%d") | mktime] | sort
      | [range(1; length) as $i | (.[$i] - .[$i - 1]) / 86400]
      | group_by(.) | map({gap_days: .[0], n: length})[]
  leitura: Os backups são diários, mas há um salto de 272 dias entre o segundo e o terceiro.
---
Perfile o intervalo entre valores consecutivos, não as datas em si. A ordem importa, por isso a tarefa também se liga a [sequential dependencies](/tarefas/sequential-dependencies/).
