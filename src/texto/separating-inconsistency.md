---
smell: Separating Inconsistency
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE salaries (id int, amount text);
    INSERT INTO salaries VALUES (1, '23 100'), (2, '23.500'), (3, '25_000'), (4, '27 000');
  duckdb: |
    SELECT pattern(amount) AS pattern, count(*) AS n
    FROM salaries
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(amount) AS pattern, count(*) AS n
    FROM salaries
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: 1, salary: { amount: "23 100" } }, { _id: 2, salary: { amount: "23.500" } },
        { _id: 3, salary: { amount: "25_000" } }, { _id: 4, salary: { amount: "27 000" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$salary.amount"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"amount": "23 100"}, {"amount": "23.500"}, {"amount": "25_000"}, {"amount": "27 000"}]
    filtro: |
      [.[].amount | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: Três separadores de milhar diferentes (espaço, ponto, sublinhado) na mesma coluna.
---
Os padrões só diferem no caractere entre os grupos de dígitos.
