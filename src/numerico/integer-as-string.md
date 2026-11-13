---
smell: Integer as String
refs: [foidl2022a]
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE stock (sku text, qty text);
    INSERT INTO stock VALUES ('A1', '5'), ('A2', '12'), ('A3', '0'), ('A4', '7');
  duckdb: |
    SELECT typeof(qty)                     AS data_type,
           count(*)                        AS n,
           count(TRY_CAST(qty AS INTEGER)) AS castable_to_integer
    FROM stock
    GROUP BY 1;
  postgres: |
    SELECT pg_typeof(qty)::text AS data_type,
           count(*) AS n,
           count(*) FILTER (WHERE pg_input_is_valid(qty, 'integer')) AS castable_to_integer
    FROM stock
    GROUP BY 1;
  mongo:
    docs: |
      [
        { _id: 1, items: [ { sku: "A1", qty: "5" }, { sku: "A2", qty: "12" } ] },
        { _id: 2, items: [ { sku: "A3", qty: "0" }, { sku: "A4", qty: "7" } ] }
      ]
    pipeline: |
      [
        { $unwind: "$items" },
        { $group: {
            _id: { $type: "$items.qty" },
            n: { $sum: 1 },
            castableToInt: { $sum: { $cond: [
              { $ne: [{ $convert: { input: "$items.qty", to: "int", onError: null } }, null] },
              1, 0] } } } }
      ]
  jq:
    entrada: |
      [
        {"id": 1, "items": [{"sku": "A1", "qty": "5"}, {"sku": "A2", "qty": "12"}]},
        {"id": 2, "items": [{"sku": "A3", "qty": "0"}, {"sku": "A4", "qty": "7"}]}
      ]
    filtro: |
      [.. | objects | select(has("qty")) | .qty]
      | {types: (map(type) | unique), n: length,
         castable_to_integer: (map(select(test("^-?[0-9]+$"))) | length)}
  leitura: >-
    Todos os valores são strings, e todos se convertem em inteiro. Somar `"5"` falha onde concatenar
    funciona (FOIDL; FELDERER; RAMLER, 2022a).
---
Em documentos, procure em todos os níveis: o campo pode estar dentro de arrays.
