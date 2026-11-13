---
smell: Ambiguous Value
exemplo:
  tarefa: domain-classification
  sql: |
    CREATE TABLE addresses (id int, line text);
    INSERT INTO addresses VALUES (1, '12 Ocean Dr'), (2, 'Dr Smith'), (3, '5 Main St'), (4, 'St Paul');
    CREATE TABLE domains (term text, domain text);
    INSERT INTO domains VALUES
      ('Dr', 'street type'), ('Dr', 'title'), ('St', 'street type'), ('St', 'saint'), ('Main', 'street name');
  duckdb: |
    SELECT d.term,
           string_agg(DISTINCT d.domain, ', ' ORDER BY d.domain) AS domains,
           count(DISTINCT a.id) AS values_with_term
    FROM addresses a
    CROSS JOIN unnest(string_split(a.line, ' ')) AS t(tok)
    JOIN domains d ON d.term = t.tok
    GROUP BY d.term
    HAVING count(DISTINCT d.domain) > 1
    ORDER BY d.term;
  postgres: |
    SELECT d.term,
           string_agg(DISTINCT d.domain, ', ' ORDER BY d.domain) AS domains,
           count(DISTINCT a.id) AS values_with_term
    FROM addresses a
    CROSS JOIN LATERAL unnest(string_to_array(a.line, ' ')) AS t(tok)
    JOIN domains d ON d.term = t.tok
    GROUP BY d.term
    HAVING count(DISTINCT d.domain) > 1
    ORDER BY d.term;
  mongo:
    docs: |
      [
        { _id: 1, line: "12 Ocean Dr" }, { _id: 2, line: "Dr Smith" },
        { _id: 3, line: "5 Main St" }, { _id: 4, line: "St Paul" }
      ]
    pipeline: |
      [
        { $project: { tok: { $split: ["$line", " "] } } }, { $unwind: "$tok" },
        { $set: { domains: { $filter: { input: [
            { term: "Dr", domain: "street type" }, { term: "Dr", domain: "title" },
            { term: "St", domain: "street type" }, { term: "St", domain: "saint" },
            { term: "Main", domain: "street name" }],
          cond: { $eq: ["$$this.term", "$tok"] } } } } },
        { $match: { "domains.1": { $exists: true } } },
        { $group: { _id: "$tok", domains: { $first: "$domains.domain" }, values_with_term: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]
  jq:
    entrada: |
      [{"line": "12 Ocean Dr"}, {"line": "Dr Smith"}, {"line": "5 Main St"}, {"line": "St Paul"}]
    filtro: |
      {"Dr": ["street type", "title"], "St": ["saint", "street type"], "Main": ["street name"]} as $dict
      | [.[].line | split(" ")[] | select(($dict[.] // []) | length > 1)]
      | group_by(.) | map({term: .[0], domains: $dict[.[0]], values_with_term: length})[]
  leitura: >-
    "Dr" e "St" pertencem a dois domínios cada; "Dr" pode ser rua (drive) ou título (doctor). Os
    quatro valores precisam de contexto para serem lidos.
---
Classifique cada token contra um dicionário de domínios. Um token com mais de um domínio é ambíguo. O dicionário é parte da entrada: na prática, vem do conhecimento do negócio.
