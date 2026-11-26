---
exemplos:
  - id: base
    titulo: quartis de tempos de resposta
    sql: |
      CREATE TABLE requests (id int, ms int);
      INSERT INTO requests VALUES
        (1, 12), (2, 15), (3, 18), (4, 22), (5, 25), (6, 31), (7, 45), (8, 60), (9, 480);
    duckdb: |
      SELECT quantile_cont(ms, 0.25) AS q1,
             quantile_cont(ms, 0.5)  AS q2,
             quantile_cont(ms, 0.75) AS q3,
             quantile_cont(ms, 0.75) - quantile_cont(ms, 0.25) AS iqr
      FROM requests;
    postgres: |
      SELECT percentile_cont(0.25) WITHIN GROUP (ORDER BY ms) AS q1,
             percentile_cont(0.5)  WITHIN GROUP (ORDER BY ms) AS q2,
             percentile_cont(0.75) WITHIN GROUP (ORDER BY ms) AS q3,
             percentile_cont(0.75) WITHIN GROUP (ORDER BY ms)
               - percentile_cont(0.25) WITHIN GROUP (ORDER BY ms) AS iqr
      FROM requests;
    mongo:
      docs: |
        [12, 15, 18, 22, 25, 31, 45, 60, 480].map((v, i) => ({ _id: i + 1, ms: v }))
      pipeline: |
        [
          { $group: { _id: null, q: { $percentile: { input: "$ms", p: [0.25, 0.5, 0.75], method: "approximate" } } } },
          { $project: { _id: 0, q1: { $arrayElemAt: ["$q", 0] }, q2: { $arrayElemAt: ["$q", 1] },
              q3: { $arrayElemAt: ["$q", 2] },
              iqr: { $subtract: [{ $arrayElemAt: ["$q", 2] }, { $arrayElemAt: ["$q", 0] }] } } }
        ]
    jq:
      entrada: |
        [12, 15, 18, 22, 25, 31, 45, 60, 480]
      filtro: |
        sort as $s | ($s | length) as $n
        | def q(p): ($n - 1) * p | floor as $i | (. - $i) as $f
                    | $s[$i] + $f * (($s[$i + 1] // $s[$i]) - $s[$i]);
        {q1: q(0.25), q2: q(0.5), q3: q(0.75), iqr: (q(0.75) - q(0.25))}
    leitura: >-
      Metade dos tempos fica entre 18 e 45 ms (IQR = 27). O valor 480 não move nenhum quartil: os
      quartis resistem a extremos, ao contrário da média. Com 9 valores, as posições dos quartis caem
      em valores existentes, e o `$percentile` aproximado do MongoDB coincide com a interpolação.
---
Os quartis são um caso especial comum do [histograma](/tarefas/histogram/) equi-depth: dividem os dados em quatro grupos com o mesmo número de valores. Como o histograma equi-depth, exigem ordenar os valores.[@abedjan2015]

A distância entre o primeiro e o terceiro quartil, o intervalo interquartil (IQR), mede a dispersão sem se deixar levar por extremos. As cercas de Tukey usam o IQR para marcar outliers; veja [Agrupamento (clustering)](/tarefas/clustering/#outliers).
