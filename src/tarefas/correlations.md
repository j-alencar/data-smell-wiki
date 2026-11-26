---
exemplos:
  - id: pearson
    titulo: correlação de Pearson entre idade e salário
    sql: |
      CREATE TABLE employees (id int, age int, salary int);
      INSERT INTO employees VALUES
        (1, 23, 2800), (2, 27, 3400), (3, 31, 4100), (4, 35, 4500),
        (5, 42, 6200), (6, 48, 6900), (7, 55, 8100), (8, 61, 7600);
    duckdb: |
      SELECT round(corr(age, salary), 3) AS r
      FROM employees;
    postgres: |
      SELECT round(corr(age, salary)::numeric, 3) AS r
      FROM employees;
    mongo:
      docs: |
        [[23, 2800], [27, 3400], [31, 4100], [35, 4500], [42, 6200], [48, 6900], [55, 8100], [61, 7600]]
          .map(([a, s], i) => ({ _id: i + 1, age: a, salary: s }))
      pipeline: |
        [
          { $group: { _id: null, n: { $sum: 1 }, sx: { $sum: "$age" }, sy: { $sum: "$salary" },
              sxy: { $sum: { $multiply: ["$age", "$salary"] } },
              sxx: { $sum: { $multiply: ["$age", "$age"] } }, syy: { $sum: { $multiply: ["$salary", "$salary"] } } } },
          { $project: { _id: 0, r: { $round: [{ $divide: [
              { $subtract: [{ $multiply: ["$n", "$sxy"] }, { $multiply: ["$sx", "$sy"] }] },
              { $sqrt: { $multiply: [
                  { $subtract: [{ $multiply: ["$n", "$sxx"] }, { $multiply: ["$sx", "$sx"] }] },
                  { $subtract: [{ $multiply: ["$n", "$syy"] }, { $multiply: ["$sy", "$sy"] }] }] } }] }, 3] } } }
        ]
    jq:
      entrada: |
        [{"age": 23, "salary": 2800}, {"age": 27, "salary": 3400}, {"age": 31, "salary": 4100},
         {"age": 35, "salary": 4500}, {"age": 42, "salary": 6200}, {"age": 48, "salary": 6900},
         {"age": 55, "salary": 8100}, {"age": 61, "salary": 7600}]
      filtro: |
        length as $n | (map(.age) | add) as $sx | (map(.salary) | add) as $sy
        | (map(.age * .salary) | add) as $sxy
        | (map(.age * .age) | add) as $sxx | (map(.salary * .salary) | add) as $syy
        | {r: (($n * $sxy - $sx * $sy) / ((($n * $sxx - $sx * $sx) * ($n * $syy - $sy * $sy)) | sqrt)
               * 1000 | round / 1000)}
    leitura: >-
      r = 0,974: idade e salário sobem juntos. Em perfilamento, o
      interesse está tanto nas correlações fortes que se esperam quanto nas que somem quando
      deveriam existir.
  - id: regras
    titulo: regras de associação entre colunas
    sql: |
      CREATE TABLE employees (id int, department text, position text, allowance int);
      INSERT INTO employees VALUES
        (1, 'finance', 'assistant manager', 1000), (2, 'finance', 'assistant manager', 1000),
        (3, 'finance', 'assistant manager', 1000), (4, 'finance', 'assistant manager', 1000),
        (5, 'finance', 'analyst', 500), (6, 'finance', 'analyst', 500),
        (7, 'sales', 'assistant manager', 800), (8, 'sales', 'assistant manager', 800),
        (9, 'sales', 'analyst', 500), (10, 'sales', 'analyst', 500);
    duckdb: |
      WITH items AS (
        SELECT 'department=' || department AS lhs, allowance FROM employees
        UNION ALL SELECT 'position=' || position, allowance FROM employees
        UNION ALL SELECT 'department=' || department || ', position=' || position, allowance FROM employees),
      rules AS (
        SELECT lhs, 'allowance=' || allowance AS rhs, count(*) AS n_rule,
               sum(count(*)) OVER (PARTITION BY lhs) AS n_lhs
        FROM items
        GROUP BY lhs, allowance)
      SELECT lhs, rhs,
             round(n_rule / (SELECT count(*) FROM employees), 2) AS support,
             round(n_rule / n_lhs, 2) AS confidence
      FROM rules
      WHERE n_rule / (SELECT count(*) FROM employees) >= 0.3 AND n_rule / n_lhs >= 0.8
      ORDER BY support DESC, lhs;
    postgres: |
      WITH items AS (
        SELECT 'department=' || department AS lhs, allowance FROM employees
        UNION ALL SELECT 'position=' || position, allowance FROM employees
        UNION ALL SELECT 'department=' || department || ', position=' || position, allowance FROM employees),
      rules AS (
        SELECT lhs, 'allowance=' || allowance AS rhs, count(*)::numeric AS n_rule,
               sum(count(*)) OVER (PARTITION BY lhs) AS n_lhs
        FROM items
        GROUP BY lhs, allowance)
      SELECT lhs, rhs,
             round(n_rule / (SELECT count(*) FROM employees), 2) AS support,
             round(n_rule / n_lhs, 2) AS confidence
      FROM rules
      WHERE n_rule / (SELECT count(*) FROM employees) >= 0.3 AND n_rule / n_lhs >= 0.8
      ORDER BY support DESC, lhs;
    mongo:
      docs: |
        [
          ...Array(4).fill(["finance", "assistant manager", 1000]), ...Array(2).fill(["finance", "analyst", 500]),
          ...Array(2).fill(["sales", "assistant manager", 800]), ...Array(2).fill(["sales", "analyst", 500])
        ].map(([d, p, a], i) => ({ _id: i + 1, department: d, position: p, allowance: a }))
      pipeline: |
        [
          { $setWindowFields: { output: { total: { $count: {}, window: { documents: ["unbounded", "unbounded"] } } } } },
          { $project: { total: 1, rhs: { $concat: ["allowance=", { $toString: "$allowance" }] }, lhs: [
              { $concat: ["department=", "$department"] }, { $concat: ["position=", "$position"] },
              { $concat: ["department=", "$department", ", position=", "$position"] }] } },
          { $unwind: "$lhs" },
          { $group: { _id: { lhs: "$lhs", rhs: "$rhs" }, n_rule: { $sum: 1 }, total: { $first: "$total" } } },
          { $setWindowFields: { partitionBy: "$_id.lhs", output: {
              n_lhs: { $sum: "$n_rule", window: { documents: ["unbounded", "unbounded"] } } } } },
          { $project: { _id: 0, lhs: "$_id.lhs", rhs: "$_id.rhs",
              support: { $round: [{ $divide: ["$n_rule", "$total"] }, 2] },
              confidence: { $round: [{ $divide: ["$n_rule", "$n_lhs"] }, 2] } } },
          { $match: { support: { $gte: 0.3 }, confidence: { $gte: 0.8 } } },
          { $sort: { support: -1, lhs: 1 } }
        ]
    jq:
      entrada: |
        [{"department": "finance", "position": "assistant manager", "allowance": 1000},
         {"department": "finance", "position": "assistant manager", "allowance": 1000},
         {"department": "finance", "position": "assistant manager", "allowance": 1000},
         {"department": "finance", "position": "assistant manager", "allowance": 1000},
         {"department": "finance", "position": "analyst", "allowance": 500},
         {"department": "finance", "position": "analyst", "allowance": 500},
         {"department": "sales", "position": "assistant manager", "allowance": 800},
         {"department": "sales", "position": "assistant manager", "allowance": 800},
         {"department": "sales", "position": "analyst", "allowance": 500},
         {"department": "sales", "position": "analyst", "allowance": 500}]
      filtro: |
        length as $total
        | [.[] | "allowance=\(.allowance)" as $rhs
           | ("department=\(.department)", "position=\(.position)",
              "department=\(.department), position=\(.position)") | {lhs: ., rhs: $rhs}]
        | group_by(.lhs)
        | map(length as $n_lhs | group_by(.rhs)[]
              | {lhs: .[0].lhs, rhs: .[0].rhs,
                 support: (length / $total * 100 | round / 100),
                 confidence: (length / $n_lhs * 100 | round / 100)})
        | map(select(.support >= 0.3 and .confidence >= 0.8))
        | sort_by([-.support, .lhs])[]
    leitura: >-
      Duas regras passam nos limiares (suporte ≥ 0,3; confiança ≥ 0,8). Todo assistant manager de
      finance recebe 1000. `department=finance` sozinho não basta (confiança 0,67), porque analysts
      de finance recebem 500.
  - id: aplicado
    smell: Unit Inconsistency
    mundo: numerico
    sql: |
      CREATE TABLE people (id int, height double precision, weight int);
      INSERT INTO people VALUES
        (1, 1.60, 55), (2, 1.68, 62), (3, 1.75, 70), (4, 1.84, 82),
        (5, 158, 54), (6, 170, 63), (7, 176, 75), (8, 190, 88);
    duckdb: |
      SELECT grp, count(*) AS n, round(corr(height, weight), 3) AS r
      FROM (SELECT 'all' AS grp, * FROM people
            UNION ALL
            SELECT CASE WHEN height < 10 THEN 'height < 10' ELSE 'height >= 10' END, * FROM people)
      GROUP BY grp
      ORDER BY grp;
    postgres: |
      SELECT grp, count(*) AS n, round(corr(height, weight)::numeric, 3) AS r
      FROM (SELECT 'all' AS grp, * FROM people
            UNION ALL
            SELECT CASE WHEN height < 10 THEN 'height < 10' ELSE 'height >= 10' END, * FROM people) t
      GROUP BY grp
      ORDER BY grp;
    mongo:
      docs: |
        [[1.60, 55], [1.68, 62], [1.75, 70], [1.84, 82], [158, 54], [170, 63], [176, 75], [190, 88]]
          .map(([h, w], i) => ({ _id: i + 1, height: h, weight: w }))
      pipeline: |
        [
          { $set: { grp: ["all", { $cond: [{ $lt: ["$height", 10] }, "height < 10", "height >= 10"] }] } },
          { $unwind: "$grp" },
          { $group: { _id: "$grp", n: { $sum: 1 }, sx: { $sum: "$height" }, sy: { $sum: "$weight" },
              sxy: { $sum: { $multiply: ["$height", "$weight"] } },
              sxx: { $sum: { $multiply: ["$height", "$height"] } }, syy: { $sum: { $multiply: ["$weight", "$weight"] } } } },
          { $project: { _id: 0, grp: "$_id", n: "$n", r: { $round: [{ $divide: [
              { $subtract: [{ $multiply: ["$n", "$sxy"] }, { $multiply: ["$sx", "$sy"] }] },
              { $sqrt: { $multiply: [
                  { $subtract: [{ $multiply: ["$n", "$sxx"] }, { $multiply: ["$sx", "$sx"] }] },
                  { $subtract: [{ $multiply: ["$n", "$syy"] }, { $multiply: ["$sy", "$sy"] }] }] } }] }, 3] } } },
          { $sort: { grp: 1 } }
        ]
    jq:
      entrada: |
        [{"height": 1.60, "weight": 55}, {"height": 1.68, "weight": 62}, {"height": 1.75, "weight": 70},
         {"height": 1.84, "weight": 82}, {"height": 158, "weight": 54}, {"height": 170, "weight": 63},
         {"height": 176, "weight": 75}, {"height": 190, "weight": 88}]
      filtro: |
        def r: length as $n | (map(.height) | add) as $sx | (map(.weight) | add) as $sy
          | (map(.height * .weight) | add) as $sxy
          | (map(.height * .height) | add) as $sxx | (map(.weight * .weight) | add) as $syy
          | ($n * $sxy - $sx * $sy) / ((($n * $sxx - $sx * $sx) * ($n * $syy - $sy * $sy)) | sqrt)
          | . * 1000 | round / 1000;
        [.[] | (.grp = "all"), (.grp = if .height < 10 then "height < 10" else "height >= 10" end)]
        | group_by(.grp) | map({grp: .[0].grp, n: length, r: r})[]
    leitura: >-
      Altura e peso deveriam andar juntos, mas a correlação da coluna inteira é fraca. Separadas
      pela ordem de grandeza, as duas metades voltam a correlacionar quase perfeitamente: metade das
      alturas está em metros e metade em centímetros. Uma correlação esperada que desaparece é
      sinal de unidades misturadas.
---
A correlação revela colunas numéricas relacionadas, como idade e salário; calcule-a para todos os pares.[@abedjan2015] Perto de 1, as colunas crescem juntas. Uma correlação esperada que desaparece pode revelar dados suspeitos, como unidades misturadas.

Regras de associação ligam valores de colunas diferentes, como {department=finance, position=assistant manager} → {allowance=1000}.[@abedjan2015] O **suporte** é a fração de linhas que satisfazem antecedente e consequente; a **confiança** é a fração das linhas com o antecedente que também satisfazem o consequente. Minere as regras em dois passos:[@abedjan2015]

1. Encontre os conjuntos de itens frequentes, cujo suporte passa de um limiar, com algoritmos como Apriori, Eclat ou FP-Growth.
2. Para cada conjunto frequente *a*, gere as regras *l* → *a* − *l* cuja confiança passa de um limiar.

Nos exemplos, os limiares são suporte ≥ 0,3 e confiança ≥ 0,8.
