---
exemplos:
  - id: base
    titulo: nulos e vazios em telefones
    sql: |
      CREATE TABLE contacts (id int, phone text);
      INSERT INTO contacts VALUES
        (1, '81 3333-4444'), (2, NULL), (3, ''), (4, '81 98888-7777'), (5, NULL), (6, '11 2222-3333');
    duckdb: |
      SELECT count(*) AS n,
             count(*) FILTER (WHERE phone IS NULL) AS nulls,
             count(*) FILTER (WHERE phone = '') AS empty,
             round(100 * count(*) FILTER (WHERE phone IS NULL OR phone = '') / count(*), 1) AS pct_missing
      FROM contacts;
    postgres: |
      SELECT count(*) AS n,
             count(*) FILTER (WHERE phone IS NULL) AS nulls,
             count(*) FILTER (WHERE phone = '') AS empty,
             round(100.0 * count(*) FILTER (WHERE phone IS NULL OR phone = '') / count(*), 1) AS pct_missing
      FROM contacts;
    mongo:
      docs: |
        [
          { _id: 1, phone: "81 3333-4444" }, { _id: 2, phone: null }, { _id: 3, phone: "" },
          { _id: 4, phone: "81 98888-7777" }, { _id: 5 }, { _id: 6, phone: "11 2222-3333" }
        ]
      pipeline: |
        [
          { $group: { _id: null, n: { $sum: 1 },
              nulls: { $sum: { $cond: [{ $eq: [{ $ifNull: ["$phone", null] }, null] }, 1, 0] } },
              empty: { $sum: { $cond: [{ $eq: ["$phone", ""] }, 1, 0] } } } },
          { $project: { _id: 0, n: 1, nulls: 1, empty: 1,
              pct_missing: { $round: [{ $multiply: [100, { $divide: [{ $add: ["$nulls", "$empty"] }, "$n"] }] }, 1] } } }
        ]
    jq:
      entrada: |
        [{"phone": "81 3333-4444"}, {"phone": null}, {"phone": ""},
         {"phone": "81 98888-7777"}, {}, {"phone": "11 2222-3333"}]
      filtro: |
        length as $n
        | {n: $n,
           nulls: (map(select(.phone == null)) | length),
           empty: (map(select(.phone == "")) | length)}
        | .pct_missing = ((.nulls + .empty) / $n * 1000 | round / 10)
    leitura: >-
      Dois nulos e um vazio: metade da coluna não tem telefone. Contar só `NULL` daria 33,3%. No
      MongoDB e no JSON, o documento 5 nem tem o campo; `$ifNull` e `.phone == null` tratam campo
      ausente como nulo.
---
Células vazias, isto é, com valor nulo ou string vazia, indicam o grau de (in)completude da coluna. A contagem exige uma única passada pelos dados (ABEDJAN; GOLAB; NAUMANN, 2015).

Valores ausentes também se disfarçam. Formulários web trazem listas com o primeiro item pré-selecionado, e parte dos usuários não o troca: o CEP vira `99999` ou o estado vira o primeiro da lista. Esses valores não são nulos, mas fazem o mesmo papel. Detectá-los é difícil; uma heurística examina, para cada valor de uma coluna, a distribuição dos demais atributos (ABEDJAN; GOLAB; NAUMANN, 2015). Veja também [Constância](/tarefas/constancy/), que mede o peso do valor mais frequente.
