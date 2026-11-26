---
exemplos:
  - id: base
    titulo: cidades distintas
    sql: |
      CREATE TABLE orders (id int, city text);
      INSERT INTO orders VALUES
        (1, 'Recife'), (2, 'Natal'), (3, 'Recife'), (4, 'Olinda'), (5, 'Natal'), (6, 'Recife');
    duckdb: |
      SELECT count(*) AS n, count(DISTINCT city) AS distinct_values
      FROM orders;
    postgres: |
      SELECT count(*) AS n, count(DISTINCT city) AS distinct_values
      FROM orders;
    mongo:
      docs: |
        [
          { _id: 1, city: "Recife" }, { _id: 2, city: "Natal" }, { _id: 3, city: "Recife" },
          { _id: 4, city: "Olinda" }, { _id: 5, city: "Natal" }, { _id: 6, city: "Recife" }
        ]
      pipeline: |
        [
          { $group: { _id: null, n: { $sum: 1 }, cities: { $addToSet: "$city" } } },
          { $project: { _id: 0, n: 1, distinct_values: { $size: "$cities" } } }
        ]
    jq:
      entrada: |
        [{"city": "Recife"}, {"city": "Natal"}, {"city": "Recife"},
         {"city": "Olinda"}, {"city": "Natal"}, {"city": "Recife"}]
      filtro: |
        {n: length, distinct_values: (map(.city) | unique | length)}
    leitura: >-
      Seis pedidos, três cidades. Com 3 distintos em 6 linhas, `city` não identifica pedidos;
      a razão entre os dois números é a [Unicidade](/tarefas/uniqueness/).
---
O número de valores distintos permite ao otimizador de consultas estimar a seletividade de seleções e junções: quanto mais valores distintos, mais seletiva a operação. Para quem analisa, comparado ao número de linhas, ele aponta candidatas a chave ou mostra quantos valores diferentes há, como quantas cidades aparecem numa tabela de endereços.[@abedjan2015]

O cálculo exato exige ordenar ou fazer hashing de todos os valores. Na ordenação, uma passada conta cada grupo de valores iguais uma vez; no hashing, contam-se os buckets não vazios, descontadas as colisões. Quando o custo importa, estimadores trabalham sobre amostras ou leem tudo com pouca memória.[@abedjan2015] Um deles é o sketch *k Minimum Values* (KMV), que guarda só os *k* menores valores de hash;[@cormode2011] veja [Resumos e sketches](/tarefas/summaries-sketches/#kmv).

`count(DISTINCT ...)` ignora `NULL` no SQL; o `$addToSet` do MongoDB guarda `null` como um valor.
