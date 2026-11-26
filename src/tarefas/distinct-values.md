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
      Seis pedidos, três cidades. Com 3 distintos em 6 linhas, `city` não identifica pedidos. A razão entre os dois números é a [Unicidade](/tarefas/uniqueness/).
---
Comparado ao número de linhas, o número de valores distintos aponta candidatas a chave ou mostra quantos valores diferentes há, como quantas cidades aparecem numa tabela de endereços.[@abedjan2015]

Em colunas grandes, o sketch *k Minimum Values* (KMV), descrito em [Resumos e sketches](/tarefas/summaries-sketches/#kmv), estima esse número.[@cormode2011]

`count(DISTINCT ...)` ignora `NULL` no SQL, mas o `$addToSet` do MongoDB guarda `null` como um valor.
