---
smell: Date as Date/Time
refs: [foidl2022a]
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE orders (id int, order_date timestamp);
    INSERT INTO orders VALUES
      (1, '2020-12-30 00:00:00'), (2, '2021-01-02 00:00:00'),
      (3, '2021-01-05 00:00:00'), (4, '2021-02-11 00:00:00');
  duckdb: |
    SELECT pattern(CAST(order_date AS VARCHAR)) AS pattern,
           strftime(order_date, '%H:%M:%S')     AS time_part,
           count(*)                             AS n
    FROM orders
    GROUP BY ALL;
  postgres: |
    SELECT pattern(order_date::text)          AS pattern,
           to_char(order_date, 'HH24:MI:SS')  AS time_part,
           count(*)                           AS n
    FROM orders
    GROUP BY 1, 2;
  mongo:
    docs: |
      [
        { _id: 1, order: { date: new Date("2020-12-30T00:00:00Z") } },
        { _id: 2, order: { date: new Date("2021-01-02T00:00:00Z") } },
        { _id: 3, order: { date: new Date("2021-01-05T00:00:00Z") } },
        { _id: 4, order: { date: new Date("2021-02-11T00:00:00Z") } }
      ]
    pipeline: |
      [
        { $group: {
            _id: { $dateToString: { format: "%H:%M:%S", date: "$order.date" } },
            n: { $sum: 1 } } }
      ]
  jq:
    slurp: true
    entrada: |
      {"ts": "2020-12-30T00:00:00Z", "event": "order"}
      {"ts": "2021-01-02T00:00:00Z", "event": "order"}
      {"ts": "2021-01-05T00:00:00Z", "event": "order"}
      {"ts": "2021-02-11T00:00:00Z", "event": "order"}
    filtro: |
      [.[].ts | split("T")[1]]
      | group_by(.) | map({time_part: .[0], n: length})[]
  leitura: >-
    Todas as linhas têm o mesmo horário, `00:00:00`: a coluna é uma data guardada como datetime.
    Converter "2021-01-01" com `pandas.to_datetime` sem declarar o formato produz exatamente isso
    (FOIDL; FELDERER; RAMLER, 2022a).
---
Perfile só a parte do horário. Se ela for constante, o campo não carrega hora.
