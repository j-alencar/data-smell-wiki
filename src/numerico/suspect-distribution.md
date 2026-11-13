---
smell: Suspect Distribution
exemplo:
  tarefa: quartiles
  sql: |
    CREATE TABLE sales (id int, amount double precision);
    INSERT INTO sales VALUES
      (1, 1), (2, 3), (3, 4), (4, 5), (5, 3), (6, 4),
      (7, 3), (8, 500), (9, 15000), (10, 780000), (11, 800000), (12, 800000);
  duckdb: |
    SELECT min(amount) AS min,
           quantile_cont(amount, 0.25) AS q1,
           quantile_cont(amount, 0.5)  AS median,
           quantile_cont(amount, 0.75) AS q3,
           max(amount) AS max
    FROM sales;
  postgres: |
    SELECT min(amount) AS min,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY amount) AS q1,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY amount) AS median,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY amount) AS q3,
           max(amount) AS max
    FROM sales;
  mongo:
    docs: |
      [1, 3, 4, 5, 3, 4, 3, 500, 15000, 780000, 800000, 800000]
        .map((v, i) => ({ _id: i + 1, sale: { amount: v } }))
    pipeline: |
      [
        { $group: { _id: null,
            min: { $min: "$sale.amount" },
            quartiles: { $percentile: { input: "$sale.amount", p: [0.25, 0.5, 0.75], method: "approximate" } },
            max: { $max: "$sale.amount" } } },
        { $project: { _id: 0 } }
      ]
  jq:
    entrada: |
      [1, 3, 4, 5, 3, 4, 3, 500, 15000, 780000, 800000, 800000]
    filtro: |
      sort as $s | ($s | length) as $n
      | def q(p): ($n - 1) * p | (floor) as $i | (. - $i) as $f
                  | $s[$i] + $f * (($s[$i + 1] // $s[$i]) - $s[$i]);
      {min: $s[0], q1: q(0.25), median: q(0.5), q3: q(0.75), max: $s[-1]}
  leitura: >-
    A mediana fica em 4,5, mas o terceiro quartil salta para os milhares: metade dos valores é
    minúscula e o resto é enorme. DuckDB, PostgreSQL e o jq acima interpolam (Q3 = 206250); o
    `$percentile` aproximado do MongoDB devolve um valor existente (Q3 = 15000). Os números mudam,
    a leitura não.
---
Quartis resumem a forma da distribuição. Uma distância grande entre a mediana e o terceiro quartil denuncia grupos de escala diferente.
