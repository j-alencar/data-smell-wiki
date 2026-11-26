---
exemplos:
  - id: base
    titulo: colunas sem nome contra um dicionário de domínios
    sql: |
      CREATE TABLE unknown (id int, a text, b text, c text, d text);
      INSERT INTO unknown VALUES
        (1, 'ana@x.com', '50050-000', 'PE', 'Ana'),
        (2, 'bia@y.org', '01310-100', 'SP', 'Bia'),
        (3, 'caio@z.net', '70040-010', 'DF', 'Caio'),
        (4, 'dani(at)w.com', '50.050-000', 'XX', 'Dani');
    duckdb: |
      WITH v AS (UNPIVOT unknown ON a, b, c, d INTO NAME col VALUE v),
      dom(domain, re) AS (VALUES
        ('email', '[^@ ]+@[^@ ]+\.[a-z]+'),
        ('cep', '\d{5}-\d{3}'),
        ('uf', 'AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO'))
      SELECT col, domain, round(avg(regexp_full_match(v, re)::int), 2) AS share
      FROM v, dom
      GROUP BY col, domain
      HAVING share > 0
      ORDER BY col, share DESC;
    postgres: |
      WITH v AS (SELECT col, v FROM unknown,
                   LATERAL (VALUES ('a', a), ('b', b), ('c', c), ('d', d)) AS u(col, v)),
      dom(domain, re) AS (VALUES
        ('email', '[^@ ]+@[^@ ]+\.[a-z]+'),
        ('cep', '\d{5}-\d{3}'),
        ('uf', 'AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO'))
      SELECT col, domain, round(avg((v ~ ('^(' || re || ')$'))::int), 2) AS share
      FROM v, dom
      GROUP BY col, domain
      HAVING avg((v ~ ('^(' || re || ')$'))::int) > 0
      ORDER BY col, share DESC;
    mongo:
      docs: |
        [
          { _id: 1, a: "ana@x.com", b: "50050-000", c: "PE", d: "Ana" },
          { _id: 2, a: "bia@y.org", b: "01310-100", c: "SP", d: "Bia" },
          { _id: 3, a: "caio@z.net", b: "70040-010", c: "DF", d: "Caio" },
          { _id: 4, a: "dani(at)w.com", b: "50.050-000", c: "XX", d: "Dani" }
        ]
      pipeline: |
        [
          { $project: { _id: 0, kv: { $objectToArray: "$$ROOT" } } }, { $unwind: "$kv" },
          { $match: { "kv.k": { $ne: "_id" } } },
          { $set: { dom: [
              { domain: "email", re: "^[^@ ]+@[^@ ]+\\.[a-z]+$" },
              { domain: "cep", re: "^\\d{5}-\\d{3}$" },
              { domain: "uf", re: "^(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)$" }] } },
          { $unwind: "$dom" },
          { $group: { _id: { col: "$kv.k", domain: "$dom.domain" },
              share: { $avg: { $cond: [{ $regexMatch: { input: "$kv.v", regex: "$dom.re" } }, 1, 0] } } } },
          { $match: { share: { $gt: 0 } } },
          { $project: { _id: 0, col: "$_id.col", domain: "$_id.domain", share: { $round: ["$share", 2] } } },
          { $sort: { col: 1, share: -1 } }
        ]
    jq:
      entrada: |
        [{"a": "ana@x.com", "b": "50050-000", "c": "PE", "d": "Ana"},
         {"a": "bia@y.org", "b": "01310-100", "c": "SP", "d": "Bia"},
         {"a": "caio@z.net", "b": "70040-010", "c": "DF", "d": "Caio"},
         {"a": "dani(at)w.com", "b": "50.050-000", "c": "XX", "d": "Dani"}]
      filtro: |
        {email: "^[^@ ]+@[^@ ]+\\.[a-z]+$", cep: "^\\d{5}-\\d{3}$",
         uf: "^(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)$"} as $dom
        | . as $rows
        | [($rows[0] | keys[]) as $col | $dom | to_entries[] as {key: $domain, value: $re}
           | {col: $col, domain: $domain,
              share: ([$rows[][$col] | if test($re) then 1 else 0 end] | add / length * 100 | round / 100)}
           | select(.share > 0)]
        | sort_by([.col, -.share])[]
    leitura: >-
      `a`, `b` e `c` ganham domínio: e-mail, CEP e UF, cada um com 75% de aderência. O quarto valor
      de cada coluna é o suspeito (`dani(at)w.com`, `50.050-000`, `XX`). A coluna `d` fica sem
      domínio: reconhecer primeiros nomes exige um dicionário de nomes, não uma expressão regular.
---
O domínio semântico descreve o significado dos valores, não só sua sintaxe.[@abedjan2015] Teste cada coluna contra os padrões de um dicionário de domínios. A fração de valores que casam indica a aderência, e os que ficam fora do padrão são candidatos a erro. Uma coluna sem correspondência pode exigir outro tipo de dicionário, como no caso dos nomes.
