---
exemplos:
  - id: base
    titulo: valor padrão de formulário
    sql: |
      CREATE TABLE signups (id int, state text);
      INSERT INTO signups VALUES
        (1, 'AC'), (2, 'PE'), (3, 'AC'), (4, 'SP'), (5, 'AC'),
        (6, 'PE'), (7, 'AC'), (8, 'BA'), (9, 'SP'), (10, 'AC');
    duckdb: |
      SELECT state AS top_value, count(*) AS n,
             count(*) / sum(count(*)) OVER () AS constancy
      FROM signups
      GROUP BY state
      ORDER BY n DESC
      LIMIT 1;
    postgres: |
      SELECT state AS top_value, count(*) AS n,
             round(count(*) / sum(count(*)) OVER (), 2) AS constancy
      FROM signups
      GROUP BY state
      ORDER BY n DESC
      LIMIT 1;
    mongo:
      docs: |
        ["AC", "PE", "AC", "SP", "AC", "PE", "AC", "BA", "SP", "AC"]
          .map((v, i) => ({ _id: i + 1, state: v }))
      pipeline: |
        [
          { $group: { _id: "$state", n: { $sum: 1 } } },
          { $setWindowFields: { output: { total: { $sum: "$n", window: { documents: ["unbounded", "unbounded"] } } } } },
          { $sort: { n: -1 } }, { $limit: 1 },
          { $project: { _id: 0, top_value: "$_id", n: "$n", constancy: { $divide: ["$n", "$total"] } } }
        ]
    jq:
      entrada: |
        ["AC", "PE", "AC", "SP", "AC", "PE", "AC", "BA", "SP", "AC"]
      filtro: |
        length as $rows | group_by(.) | max_by(length)
        | {top_value: .[0], n: length, constancy: (length / $rows)}
    leitura: >-
      Metade dos cadastros diz `AC`, a primeira UF em ordem alfabética, a que um formulário mostraria
      pré-selecionada. Constância alta num campo que deveria variar sugere um valor padrão
      disfarçado, não um fato.
---
A constância é a frequência do valor mais frequente, possivelmente um valor padrão predefinido, dividida pelo número total de valores. Ela representa a proporção de algum valor constante em relação à coluna inteira (ABEDJAN; GOLAB; NAUMANN, 2015). O valor mais frequente sai de uma passada com hashing ou de uma ordenação (ABEDJAN; GOLAB; NAUMANN, 2015).

O exemplo segue o caso dos formulários web descrito pelos autores: o primeiro item de uma lista vem pré-selecionado e parte dos usuários não o troca, como o estado `Alabama`, primeiro em ordem alfabética nos EUA (ABEDJAN; GOLAB; NAUMANN, 2015). Aqui, a lista é a de UFs brasileiras.
