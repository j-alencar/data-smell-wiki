---
smell: Separating
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE populations (id int, people text);
    INSERT INTO populations VALUES (1, '23 432'), (2, '21.321'), (3, '12 340 000'), (4, '1500'), (5, '980');
  duckdb: |
    SELECT pattern(people) AS pattern, count(*) AS n
    FROM populations
    GROUP BY 1
    ORDER BY pattern;
  postgres: |
    SELECT pattern(people) AS pattern, count(*) AS n
    FROM populations
    GROUP BY 1
    ORDER BY pattern;
  mongo:
    docs: |
      [
        { _id: 1, city: { people: "23 432" } }, { _id: 2, city: { people: "21.321" } },
        { _id: 3, city: { people: "12 340 000" } }, { _id: 4, city: { people: "1500" } },
        { _id: 5, city: { people: "980" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$city.people"), n: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"people": "23 432"}, {"people": "21.321"}, {"people": "12 340 000"}, {"people": "1500"}, {"people": "980"}]
    filtro: |
      [.[].people | pattern]
      | group_by(.) | map({pattern: .[0], n: length})[]
  leitura: >-
    Três valores agrupam dígitos com espaço ou ponto. `99.999` é ambíguo: pode ser 21 mil ou 21
    vírgula 321.
---
Espaço, ponto ou sublinhado entre grupos de três dígitos é separador de milhar.
