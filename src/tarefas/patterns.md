---
exemplos:
  - id: base
    titulo: placas de veículos
    sql: |
      CREATE TABLE vehicles (id int, plate text);
      INSERT INTO vehicles VALUES
        (1, 'ABC-1234'), (2, 'BRA2E19'), (3, 'KLM-9081'), (4, 'RIO2A18'), (5, 'PQR-4455'), (6, 'AB-12345');
    duckdb: |
      SELECT pattern(plate) AS pattern, count(*) AS n, min(plate) AS example
      FROM vehicles
      GROUP BY 1
      ORDER BY n DESC, pattern;
    postgres: |
      SELECT pattern(plate) AS pattern, count(*) AS n, min(plate) AS example
      FROM vehicles
      GROUP BY 1
      ORDER BY n DESC, pattern;
    mongo:
      docs: |
        ["ABC-1234", "BRA2E19", "KLM-9081", "RIO2A18", "PQR-4455", "AB-12345"]
          .map((v, i) => ({ _id: i + 1, plate: v }))
      pipeline: |
        [
          { $group: { _id: pattern("$plate"), n: { $sum: 1 }, example: { $min: "$plate" } } },
          { $sort: { n: -1, _id: 1 } },
          { $project: { _id: 0, pattern: "$_id", n: "$n", example: "$example" } }
        ]
    jq:
      entrada: |
        ["ABC-1234", "BRA2E19", "KLM-9081", "RIO2A18", "PQR-4455", "AB-12345"]
      filtro: |
        map({pattern: pattern, plate: .}) | group_by(.pattern)
        | map({pattern: .[0].pattern, n: length, example: (map(.plate) | min)})
        | sort_by([-.n, .pattern])[]
    leitura: >-
      Dois padrões frequentes: o antigo `AAA-9999` e o Mercosul `AAA9A99`. `AB-12345` não segue
      nenhum dos dois e é o candidato a erro. Note o equilíbrio entre generalidade e especificidade:
      `.*` aceitaria tudo; `ABC-1234` só aceitaria a si mesmo.
---
A função `pattern` troca maiúsculas por `A`, minúsculas por `a` e dígitos por `9`; os demais caracteres ficam iguais. Conte os padrões e examine os valores que fogem dos mais frequentes.
