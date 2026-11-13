---
smell: Ambiguous Date/Time Format
refs: [mesibov2023, gbif-parsers]
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE occurrence (id int, event_date text);
    INSERT INTO occurrence VALUES
      (1, '2021-05-03'), (2, '5/3/21'), (3, '12/31/20'),
      (4, '03/05/2021'), (5, '2020-12-31'), (6, '1/2/1996');
  duckdb: |
    SELECT pattern(event_date) AS pattern, count(*) AS n
    FROM occurrence
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(event_date) AS pattern, count(*) AS n
    FROM occurrence
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, occurrence: { eventDate: "2021-05-03" } },
        { _id: 2, occurrence: { eventDate: "5/3/21" } },
        { _id: 3, occurrence: { eventDate: "12/31/20" } },
        { _id: 4, occurrence: { eventDate: "03/05/2021" } },
        { _id: 5, occurrence: { eventDate: "2020-12-31" } },
        { _id: 6, occurrence: { eventDate: "1/2/1996" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$occurrence.eventDate"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [
        {"id": 1, "eventDate": "2021-05-03"}, {"id": 2, "eventDate": "5/3/21"},
        {"id": 3, "eventDate": "12/31/20"}, {"id": 4, "eventDate": "03/05/2021"},
        {"id": 5, "eventDate": "2020-12-31"}, {"id": 6, "eventDate": "1/2/1996"}
      ]
    filtro: |
      [.[].eventDate | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: >-
    Todo padrão diferente de `9999-99-99` é ambíguo. "5/3/21" pode ser maio ou março, e de 1921
    ou 2021 (MESIBOV, 2023). O parser do GBIF devolve "1/2/1996" como ambíguo, com duas
    alternativas (BLISSETT, 2018).
---
Com separador `/` e dois grupos curtos no início, o padrão não diz se é dia/mês ou mês/dia. Ano com dois dígitos acrescenta ambiguidade de século.
