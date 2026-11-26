---
exemplos:
  - id: base
    titulo: comprimento de primeiros nomes
    sql: |
      CREATE TABLE customers (id int, first_name text);
      INSERT INTO customers VALUES
        (1, 'Ana'), (2, 'Bruno'), (3, 'J'), (4, 'Maria'), (5, 'Guilherme');
    duckdb: |
      SELECT min(length(first_name)) AS min,
             max(length(first_name)) AS max,
             median(length(first_name)) AS median,
             round(avg(length(first_name)), 2) AS avg
      FROM customers;
    postgres: |
      SELECT min(length(first_name)) AS min,
             max(length(first_name)) AS max,
             percentile_cont(0.5) WITHIN GROUP (ORDER BY length(first_name)) AS median,
             round(avg(length(first_name)), 2) AS avg
      FROM customers;
    mongo:
      docs: |
        [
          { _id: 1, first_name: "Ana" }, { _id: 2, first_name: "Bruno" }, { _id: 3, first_name: "J" },
          { _id: 4, first_name: "Maria" }, { _id: 5, first_name: "Guilherme" }
        ]
      pipeline: |
        [
          { $project: { len: { $strLenCP: "$first_name" } } },
          { $group: { _id: null, min: { $min: "$len" }, max: { $max: "$len" },
              median: { $median: { input: "$len", method: "approximate" } }, avg: { $avg: "$len" } } },
          { $project: { _id: 0, min: 1, max: 1, median: 1, avg: { $round: ["$avg", 2] } } }
        ]
    jq:
      entrada: |
        [{"first_name": "Ana"}, {"first_name": "Bruno"}, {"first_name": "J"},
         {"first_name": "Maria"}, {"first_name": "Guilherme"}]
      filtro: |
        [.[].first_name | length] | sort as $l | ($l | length) as $n
        | {min: $l[0], max: $l[-1],
           median: (if $n % 2 == 1 then $l[$n / 2 | floor] else ($l[$n / 2 - 1] + $l[$n / 2]) / 2 end),
           avg: (add / $n * 100 | round / 100)}
    leitura: >-
      O mínimo 1 vem de `J`: um primeiro nome de um caractere só é o outlier que esta tarefa
      costuma revelar. Uma coluna de datas no mesmo formato teria mínimo, máximo e média iguais.
---
O comprimento dos valores ajuda a reconstruir o esquema, por exemplo para fixar limites justos de tipos como `varchar(n)`. Também revela outliers, como primeiros nomes de um caractere, e problemas de formatação: datas num mesmo formato têm o mesmo comprimento mínimo, máximo e médio. O cálculo exige uma única passada pelos dados.[@abedjan2015]
