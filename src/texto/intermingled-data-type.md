---
smell: Intermingled Data Type
exemplo:
  tarefa: basic-type
  sql: |
    CREATE TABLE rooms (id int, room text);
    INSERT INTO rooms VALUES (1, 'Room 12'), (2, '90 Days'), (3, 'Lobby'), (4, 'Kitchen'), (5, '12');
  duckdb: |
    SELECT CASE WHEN regexp_full_match(room, '[0-9]+') THEN 'numeric'
                WHEN regexp_full_match(room, '[A-Za-z ]+') THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n
    FROM rooms
    GROUP BY 1
    ORDER BY n DESC, basic_type;
  postgres: |
    SELECT CASE WHEN room ~ '^[0-9]+$' THEN 'numeric'
                WHEN room ~ '^[A-Za-z ]+$' THEN 'alphabetic'
                ELSE 'alphanumeric' END AS basic_type,
           count(*) AS n
    FROM rooms
    GROUP BY 1
    ORDER BY n DESC, basic_type;
  mongo:
    docs: |
      [
        { _id: 1, room: "Room 12" }, { _id: 2, room: "90 Days" }, { _id: 3, room: "Lobby" },
        { _id: 4, room: "Kitchen" }, { _id: 5, room: "12" }
      ]
    pipeline: |
      [
        { $group: { _id: { $switch: { branches: [
            { case: { $regexMatch: { input: "$room", regex: /^[0-9]+$/ } }, then: "numeric" },
            { case: { $regexMatch: { input: "$room", regex: /^[A-Za-z ]+$/ } }, then: "alphabetic" } ],
            default: "alphanumeric" } }, n: { $sum: 1 } } },
        { $sort: { n: -1, _id: 1 } }
      ]
  jq:
    entrada: |
      [{"room": "Room 12"}, {"room": "90 Days"}, {"room": "Lobby"}, {"room": "Kitchen"}, {"room": "12"}]
    filtro: |
      [.[].room | if test("^[0-9]+$") then "numeric"
                  elif test("^[A-Za-z ]+$") then "alphabetic" else "alphanumeric" end]
      | group_by(.) | map({basic_type: .[0], n: length})
      | sort_by([-.n, .basic_type])[]
  leitura: Três tipos básicos numa coluna de nomes de sala; `12` e `Room 12` talvez sejam a mesma sala.
---
Classifique cada valor como numérico, alfabético ou alfanumérico. Uma coluna de texto saudável costuma ter um tipo dominante.
