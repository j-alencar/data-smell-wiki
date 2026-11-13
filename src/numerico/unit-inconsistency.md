---
smell: Unit Inconsistency
refs: [yfinance-552, yfinance-1110]
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE prices (day date, close double precision);
    INSERT INTO prices VALUES
      ('2021-01-04', 62.15), ('2021-01-05', 62.37), ('2021-01-06', 6215.0), ('2021-01-07', 61.93);
  duckdb: |
    SELECT pattern(CAST(close AS VARCHAR)) AS pattern, count(*) AS n
    FROM prices
    GROUP BY 1
    ORDER BY n DESC;
  postgres: |
    SELECT pattern(close::text) AS pattern, count(*) AS n
    FROM prices
    GROUP BY 1
    ORDER BY n DESC;
  mongo:
    docs: |
      [
        { _id: 1, quote: { day: "2021-01-04", close: 62.15 } },
        { _id: 2, quote: { day: "2021-01-05", close: 62.37 } },
        { _id: 3, quote: { day: "2021-01-06", close: 6215.0 } },
        { _id: 4, quote: { day: "2021-01-07", close: 61.93 } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern({ $toString: "$quote.close" }), n: { $sum: 1 } } },
        { $sort: { n: -1 } }
      ]
  jq:
    slurp: true
    entrada: |
      {"day": "2021-01-04", "close": 62.15}
      {"day": "2021-01-05", "close": 62.37}
      {"day": "2021-01-06", "close": 6215.0}
      {"day": "2021-01-07", "close": 61.93}
    filtro: |
      [.[].close | tostring | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by(-.n)[]
  leitura: >-
    Um valor tem dois dígitos inteiros a mais: um salto de 100×, a forma de pence (GBp) misturado
    com libras (GBP), como no yfinance (YFINANCE, 2021; 2022). O padrão do valor discrepante muda
    conforme o motor escreve `6215.0`: com ou sem a casa decimal.
---
Num campo numérico sem unidade escrita, a troca de escala só aparece como salto de magnitude. Se alguém escrever a unidade no valor, o campo migra para Texto.
