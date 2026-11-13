---
smell: Unit Inconsistency
refs: [osm-maxspeed, osrm-measure]
exemplo:
  tarefa: patterns
  sql: |
    CREATE TABLE ways (id int, maxspeed text);
    INSERT INTO ways VALUES
      (1, '50'), (2, '30 mph'), (3, '60 MPH'), (4, '10 knots'), (5, '80');
  duckdb: |
    SELECT pattern(maxspeed) AS pattern, count(*) AS n
    FROM ways
    GROUP BY 1
    ORDER BY n DESC, pattern;
  postgres: |
    SELECT pattern(maxspeed) AS pattern, count(*) AS n
    FROM ways
    GROUP BY 1
    ORDER BY n DESC, pattern;
  mongo:
    docs: |
      [
        { _id: "way/1", tags: { highway: "primary", maxspeed: "50" } },
        { _id: "way/2", tags: { highway: "primary", maxspeed: "30 mph" } },
        { _id: "way/3", tags: { highway: "primary", maxspeed: "60 MPH" } },
        { _id: "way/4", tags: { waterway: "canal", maxspeed: "10 knots" } },
        { _id: "way/5", tags: { highway: "motorway", maxspeed: "80" } }
      ]
    pipeline: |
      [
        { $group: { _id: pattern("$tags.maxspeed"), n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"maxspeed": "50"}, "geometry": null},
        {"type": "Feature", "properties": {"maxspeed": "30 mph"}, "geometry": null},
        {"type": "Feature", "properties": {"maxspeed": "60 MPH"}, "geometry": null},
        {"type": "Feature", "properties": {"maxspeed": "10 knots"}, "geometry": null},
        {"type": "Feature", "properties": {"maxspeed": "80"}, "geometry": null}
      ]}
    filtro: |
      [.features[].properties.maxspeed | pattern]
      | group_by(.) | map({pattern: .[0], n: length})
      | sort_by([-.n, .pattern])[]
  leitura: >-
    Números sem unidade (km/h implícito) convivem com três sufixos de unidade. Pelo código do OSRM,
    só "mph" em minúsculas é convertido; "60 MPH" seria lido como 60 km/h (OPENSTREETMAP WIKI, 2026; PROJECT-OSRM, [20--]).
---
Em texto, a unidade vem escrita no valor e aparece na cauda alfabética do padrão. Variações de caixa da mesma unidade dividem o histograma.
