"""PROTOTYPE — single source of truth for both site variants.

Smell -> task mapping copied from tree.png (TCC framework, Figura 2).
Worlds copied from the author's prose sketch.
"""

RB = "https://github.com/mkerschbaumer/rb-data-smell-detection/blob/cb12887e2184352d7ca299c8f764c1a1fd25a636/data_smell_detection/datasmelldetection/core/datasmells.py"
RB_CITE = f"Foidl & Felderer (2021), via docstrings in [rb-data-smell-detection]({RB})"
FOIDL_CITE = "Foidl, Felderer & Ramler (2022), *Data Smells*, CAIN'22, §4.2"
ABEDJAN = "Abedjan, Golab & Naumann (2015), *Profiling relational data: a survey*"

CATS = {
    "B": ("Believability", "#C2185B"),
    "UE": ("Understandability — Encoding", "#1565C0"),
    "US": ("Understandability — Syntactic", "#4527A0"),
    "C": ("Consistency", "#00695C"),
}

# task slug: (name, Abedjan category, scope, description)
TASKS = {
    "value-length": ("value length", "Cardinalities", "Single column",
        "Measurements of value lengths (minimum, maximum, median, and average)", "Table 1"),
    "null-values": ("null values", "Cardinalities", "Single column",
        "Number or percentage of null values", "Table 1"),
    "histogram": ("histogram", "Value distributions", "Single column",
        "Frequency histograms (equi-width, equi-depth, etc.)", "Table 1"),
    "constancy": ("constancy", "Value distributions", "Single column",
        "Frequency of most frequent value divided by number of rows", "Table 1"),
    "quartiles": ("quartiles", "Value distributions", "Single column",
        "Three points that divide the (numeric) values into four equal groups", "Table 1"),
    "first-digit": ("first digit", "Value distributions", "Single column",
        "Distribution of first digit in numeric values; to check Benford's law", "Table 1"),
    "basic-type": ("basic type", "Patterns, data types, and domains", "Single column",
        "Generic data type, such as numeric, alphabetic, alphanumeric, date, time", "Table 1"),
    "data-type": ("data type", "Patterns, data types, and domains", "Single column",
        "Concrete DBMS-specific data type, such as varchar, timestamp, etc.", "Table 1"),
    "decimals": ("decimals", "Patterns, data types, and domains", "Single column",
        "Maximum number of decimals in numeric values", "Table 1"),
    "patterns": ("patterns", "Patterns, data types, and domains", "Single column",
        "Histogram of value patterns (Aa9...)", "Table 1"),
    "domain-classification": ("domain classification", "Patterns, data types, and domains", "Single column",
        "Classification of semantic domain, such as credit card, first name, city, phenotype", "Table 1"),
    "clustering": ("clustering", "Clusters & outliers", "Multiple columns",
        "Segment the records into homogeneous groups using a clustering algorithm; furthermore, records that do not fit into any cluster may be flagged as outliers", "§4.2"),
    "summaries-sketches": ("summaries & sketches (MinHash, Jaccard similarity)", "Summaries & sketches", "Multiple columns",
        "Create summaries or sketches; e.g. estimate the Jaccard similarity of columns using their MinHash signatures", "§4.3"),
    "correlations": ("correlations", "Correlations & association rules", "Multiple columns",
        "Correlation analysis reveals related numeric columns; association rules denote relationships or patterns between attribute values among columns", "§4.1"),
    "sequential-dependencies": ("sequential dependencies", "Dependencies", "Dependencies",
        "Dependencies on the ordering of values (listed among dependency tasks, Fig. 1/§5)", "§5"),
}

# name: (cat, definition, definition source, [task slugs])
SMELLS = {
    "Suspect Date Value": ("B", "Occurs when a data value represents a date far in the past or future.", RB_CITE, ["patterns", "histogram", "quartiles"]),
    "Meaningless Value": ("B", "Arises when a data value has no common meaning or contains suspect repeating sequences of characters.", RB_CITE, ["constancy", "domain-classification"]),
    "Dummy Value": ("B", "A kind of substitute value (sentinel value) is used due to several reasons (e.g. missing values, unknown values, computation errors, surpass 'not NULL' constraints etc.).", RB_CITE, ["constancy", "first-digit", "patterns"]),
    "Suspect Precision": ("B", None, None, ["decimals", "histogram"]),
    "Suspect Distribution": ("B", "The data values have a suspect distribution.", RB_CITE, ["histogram", "quartiles", "first-digit"]),
    "Suspect Date/Time Interval": ("B", "Occurs when there is a very long/short date/time interval between data instances.", RB_CITE, ["histogram", "sequential-dependencies"]),
    "Date as Date/Time": ("UE", "Occurs when a date is encoded as a datetime data type.", RB_CITE, ["basic-type", "data-type", "patterns"]),
    "Date as String": ("UE", "Occurs when a date is encoded as a string.", RB_CITE, ["basic-type", "patterns"]),
    "Floating-point Number as String": ("UE", "Occurs when a floating-point number is encoded as a string.", RB_CITE, ["basic-type", "patterns"]),
    "Integer as Floating-point Number": ("UE", "Occurs when an integer is encoded as a floating-point number.", RB_CITE, ["data-type", "decimals"]),
    "Integer as String": ("UE", "Occurs when an integer is encoded as a string, usually indicated by double quotation marks (e.g., \"5\"). While some operations can be performed with this data value (e.g., concatenations), others will result in a fault (e.g., additions).", FOIDL_CITE, ["basic-type", "patterns"]),
    "Date/Time as String": ("UE", "Occurs when a date and a timestamp are encoded as a string.", RB_CITE, ["basic-type", "patterns"]),
    "Time as String": ("UE", "Occurs when a timestamp is encoded as a string.", RB_CITE, ["basic-type", "patterns"]),
    "Small Number": ("US", "Occurs when data values represent numbers below 1. If several such values are multiplied in subsequent operations, the calculation result can be very small and has many decimal places.", FOIDL_CITE, ["quartiles", "histogram", "value-length"]),
    "Contracting": ("US", "Occurs when data values represent shortened version of words or phrases.", RB_CITE, ["patterns"]),
    "Spacing": ("US", "Arises when data values contain an uncommon pattern of spaces (Trailing Space, Leading Spaces, Multiple Spaces, Missing Spaces).", RB_CITE, ["patterns"]),
    "Separating": ("US", "Arises when data values contain thousands separators (space, underbar, dot etc.) for grouping digits.", RB_CITE, ["patterns"]),
    "Long Data Value": ("US", "Arises when data values are too long to understand.", RB_CITE, ["value-length", "patterns"]),
    "Intermingled Data Type": ("US", "Data values contain numeric and alphabetic characters.", RB_CITE, ["basic-type", "patterns"]),
    "Ambiguous Value": ("US", "Arises when data values represent abbreviations, homonyms, acronyms or an ambiguous context.", RB_CITE, ["domain-classification", "clustering"]),
    "Ambiguous Date/Time Format": ("US", "Occurs when a date is represented in short format or a timestamp is represented in 12 hour format.", RB_CITE, ["patterns"]),
    "Special Character": ("US", "Occurs when data values contain special characters (non-alphanumeric) like Commas, Dots, Hyphens, Apostrophes, Tab Char, Punctuation, Parentheses, Dashes, accented Letters, etc.", RB_CITE, ["patterns"]),
    "Casing": ("US", "Occurs when data values represent an unusual use of upper and lower case (Mixed Case, Upper Only, Lower Only).", RB_CITE, ["patterns"]),
    "Extraneous Value": ("US", "Occurs when data values provide additional, likely unnecessary information.", RB_CITE, ["value-length", "patterns"]),
    "Synonym": ("US", "Occurs when data values have the same semantic meaning but are syntactically different (e.g. Aliases, Nick names, Pseudonyms).", RB_CITE, ["clustering", "summaries-sketches"]),
    "Abbreviation Inconsistency": ("C", "Arises when abbreviations, acronyms or contractions are not used consistently.", FOIDL_CITE, ["patterns", "histogram"]),
    "Casing Inconsistency": ("C", "Upper and lower case is not used consistently.", RB_CITE, ["patterns"]),
    "Syntax Inconsistency": ("C", "The general syntax (decimal places, telephone area codes, extraneous information etc.) of data values is not used consistently.", RB_CITE, ["patterns"]),
    "Date/Time Format Inconsistency": ("C", "Occurs when date or time formats are not used consistently.", RB_CITE, ["patterns"]),
    "Missing Value Inconsistency": ("C", "Constants are not used consistently to represent missing data values.", RB_CITE, ["null-values", "constancy"]),
    "Precision Inconsistency": ("C", None, None, ["decimals", "histogram"]),
    "Separating Inconsistency": ("C", "Occurs when thousands separator are not used consistently.", RB_CITE, ["patterns"]),
    "Transposition Inconsistency": ("C", "Arises when ordering of words or special characters is not used consistently.", RB_CITE, ["patterns", "correlations"]),
    "Special Character Inconsistency": ("C", "Occurs when special characters are not used consistently.", RB_CITE, ["patterns"]),
    "Spacing Inconsistency": ("C", "Occurs when spacing is not used consistently.", RB_CITE, ["patterns"]),
    "Unit Inconsistency": ("C", "Arises when units of measurement are not (implicitly) used consistently.", RB_CITE, ["patterns", "correlations"]),
}

ARCHETYPAL = ["Dummy Value", "Missing Value Inconsistency", "Unit Inconsistency", "Extraneous Value", "Intermingled Data Type"]
MIGRATES = {"Unit Inconsistency", "Extraneous Value", "Intermingled Data Type"}  # -> text, from time-series/numeric

WORLDS = {
    "time-series": ("Time-series", "Is it seemingly meant for time-series data?", [
        "Date as Date/Time", "Date as String", "Date/Time as String", "Time as String",
        "Suspect Date Value", "Suspect Date/Time Interval", "Ambiguous Date/Time Format",
        "Date/Time Format Inconsistency"]),
    "numeric": ("Numeric", "Is it seemingly meant for numerical data?", [
        "Floating-point Number as String", "Integer as String", "Suspect Precision",
        "Suspect Distribution", "Small Number", "Precision Inconsistency"]),
    "text": ("Text", "Is it seemingly meant for text data?", [
        "Meaningless Value", "Contracting", "Spacing", "Separating", "Long Data Value",
        "Special Character", "Casing", "Casing Inconsistency", "Syntax Inconsistency",
        "Abbreviation Inconsistency", "Separating Inconsistency", "Transposition Inconsistency",
        "Special Character Inconsistency", "Spacing Inconsistency", "Synonym"]),
}

UNPLACED = [s for s in SMELLS if s not in ARCHETYPAL and not any(s in w[2] for w in WORLDS.values())]


def slug(s):
    return s.lower().replace("/", "-").replace(" ", "-")


NON_RELATIONAL = """If applied to non-relational data, such as a Document Store, the values inside types such as Array or Object (that are not of these same types) would recursively receive these categorizations. Furthermore, the same would apply to any collection of data, such as collections of scalars in a Geospatial system. Boolean types would end up being attributed to either the Numeric or Text world, depending on the supported representations, which can cause Synonym, Intermingled Data Type and Integer as String smells. The same is true for binary data, as its representation as a blob in blob storages does not have the semantics necessary for suspicion, unless represented in the Numeric or Text worlds. Of course, the profiling techniques dependant on Relationships cannot apply to these storage formats directly."""

# ---- helpers shown on base task pages ----
HELPERS = {
    "patterns": {
        "sql": """CREATE MACRO pattern(v) AS
  regexp_replace(regexp_replace(regexp_replace(v,
    '[A-Z]', 'A', 'g'), '[a-z]', 'a', 'g'), '[0-9]', '9', 'g');""",
        "mongo": """// expression builder: maps each character to A / a / 9
const pattern = (s) => ({ $reduce: {
  input: { $range: [0, { $strLenCP: s }] }, initialValue: "",
  in: { $let: { vars: { c: { $substrCP: [s, "$$this", 1] } },
    in: { $concat: ["$$value", { $switch: { branches: [
      { case: { $regexMatch: { input: "$$c", regex: /[A-Z]/ } }, then: "A" },
      { case: { $regexMatch: { input: "$$c", regex: /[a-z]/ } }, then: "a" },
      { case: { $regexMatch: { input: "$$c", regex: /[0-9]/ } }, then: "9" } ],
      default: "$$c" } }] } } } } });""",
        "jq": """def pattern: gsub("[A-Z]"; "A") | gsub("[a-z]"; "a") | gsub("[0-9]"; "9");""",
    },
}

# ---- tailored, fully worked pages ----
# Each example: task, note, sql{setup, query, cols, rows}, mongo{docs, pipeline, out}, jq{input, filter, out}, sources
EXAMPLES = {
("time-series", "Ambiguous Date/Time Format"): dict(
    task="patterns",
    note="In a date field, a pattern with `/` separators and two short leading groups cannot tell day/month from month/day. A two-digit year adds century ambiguity: \"5/3/21\" could be 1921.",
    sql=dict(
        setup="""CREATE TABLE occurrence AS SELECT * FROM (VALUES
  (1, '2021-05-03'), (2, '5/3/21'), (3, '12/31/20'),
  (4, '03/05/2021'), (5, '2020-12-31'), (6, '1/2/1996')
) t(id, event_date);""",
        query="""SELECT pattern(event_date) AS pattern, count(*) AS n
FROM occurrence
GROUP BY 1
ORDER BY n DESC, pattern;"""),
    mongo=dict(
        docs="""[
  { _id: 1, occurrence: { eventDate: "2021-05-03" } },
  { _id: 2, occurrence: { eventDate: "5/3/21" } },
  { _id: 3, occurrence: { eventDate: "12/31/20" } },
  { _id: 4, occurrence: { eventDate: "03/05/2021" } },
  { _id: 5, occurrence: { eventDate: "2020-12-31" } },
  { _id: 6, occurrence: { eventDate: "1/2/1996" } }
]""",
        pipeline="""[
  { $group: { _id: pattern("$occurrence.eventDate"), n: { $sum: 1 } } },
  { $sort: { n: -1, _id: 1 } }
]"""),
    jq=dict(
        input="""[
  {"id": 1, "eventDate": "2021-05-03"},
  {"id": 2, "eventDate": "5/3/21"},
  {"id": 3, "eventDate": "12/31/20"},
  {"id": 4, "eventDate": "03/05/2021"},
  {"id": 5, "eventDate": "2020-12-31"},
  {"id": 6, "eventDate": "1/2/1996"}
]""",
        filter="""[.[].eventDate | pattern]
| group_by(.) | map({pattern: .[0], n: length})
| sort_by([-.n, .pattern])[]"""),
    reading="Every pattern except `9999-99-99` is ambiguous. GBIF's parser returns \"1/2/1996\" as ambiguous with two alternatives.",
    sources=[
        "Mesibov, R. *Please share your dates correctly*. GBIF forum, 2023. https://discourse.gbif.org/t/please-share-your-dates-correctly/3824",
        "gbif/parsers commit [8631f5ad](https://github.com/gbif/parsers/commit/8631f5ad70ab764974a8bcced0d495202f1d77af): \"Return ambiguous dates to caller\".",
    ]),
("time-series", "Date as Date/Time"): dict(
    task="patterns",
    note="Profile the time part on its own. If every row has the same time, the column is a date that got encoded as a datetime.",
    sql=dict(
        setup="""CREATE TABLE orders AS SELECT * FROM (VALUES
  (1, TIMESTAMP '2021-01-01 00:00:00'), (2, TIMESTAMP '2021-01-02 00:00:00'),
  (3, TIMESTAMP '2021-01-05 00:00:00'), (4, TIMESTAMP '2021-02-11 00:00:00')
) t(id, order_date);""",
        query="""SELECT pattern(CAST(order_date AS VARCHAR)) AS pattern,
       strftime(order_date, '%H:%M:%S')     AS time_part,
       count(*)                             AS n
FROM orders
GROUP BY ALL;"""),
    mongo=dict(
        docs="""[
  { _id: 1, order: { date: new Date("2021-01-01T00:00:00Z") } },
  { _id: 2, order: { date: new Date("2021-01-02T00:00:00Z") } },
  { _id: 3, order: { date: new Date("2021-01-05T00:00:00Z") } },
  { _id: 4, order: { date: new Date("2021-02-11T00:00:00Z") } }
]""",
        pipeline="""[
  { $group: {
      _id: { $dateToString: { format: "%H:%M:%S", date: "$order.date" } },
      n: { $sum: 1 } } }
]"""),
    jq=dict(
        input="""{"ts": "2021-01-01T00:00:00Z", "event": "order"}
{"ts": "2021-01-02T00:00:00Z", "event": "order"}
{"ts": "2021-01-05T00:00:00Z", "event": "order"}
{"ts": "2021-02-11T00:00:00Z", "event": "order"}""",
        slurp=True,
        filter="""[.[].ts | split("T")[1]]
| group_by(.) | map({time_part: .[0], n: length})[]"""),
    reading="A single `00:00:00` time part across all rows means the column carries no time information.",
    sources=[
        "Foidl et al. (2022) §5.1.2: `pandas.to_datetime` on \"2021-01-01\" yields \"2021-01-01 00:00:00\".",
    ]),
("time-series", "Unit Inconsistency"): dict(
    task="patterns",
    note="In timestamps, the unit is the epoch resolution. Seconds and milliseconds since 1970 look alike but differ by three digits (10 vs 13 for current dates).",
    sql=dict(
        setup="""CREATE TABLE events AS SELECT * FROM (VALUES
  (1, 1609459200), (2, 1609459260000), (3, 1609459320), (4, 1609459380)
) t(id, created_at);""",
        query="""SELECT pattern(CAST(created_at AS VARCHAR)) AS pattern, count(*) AS n
FROM events
GROUP BY 1
ORDER BY n DESC;"""),
    mongo=dict(
        docs="""[
  { _id: 1, meta: { createdAt: NumberLong("1609459200") } },
  { _id: 2, meta: { createdAt: NumberLong("1609459260000") } },
  { _id: 3, meta: { createdAt: NumberLong("1609459320") } },
  { _id: 4, meta: { createdAt: NumberLong("1609459380") } }
]""",
        pipeline="""[
  { $group: { _id: pattern({ $toString: "$meta.createdAt" }), n: { $sum: 1 } } },
  { $sort: { n: -1 } }
]"""),
    jq=dict(
        input="""[{"createdAt": 1609459200}, {"createdAt": 1609459260000},
 {"createdAt": 1609459320}, {"createdAt": 1609459380}]""",
        filter="""[.[].createdAt | tostring | pattern]
| group_by(.) | map({pattern: .[0], n: length})
| sort_by(-.n)[]"""),
    reading="One 13-digit value among 10-digit ones: probably milliseconds among seconds.",
    sources=["Framework author's note (TCC working session); not from a cited source."]),
("time-series", "Dummy Value"): dict(
    task="constancy",
    note="In a date field, a dummy value is usually a placeholder date such as 1 January of a year standing in for \"sometime in that year\".",
    sql=dict(
        setup="""CREATE TABLE specimens AS SELECT * FROM (VALUES
  (1, DATE '1950-01-01'), (2, DATE '1950-01-01'), (3, DATE '1950-06-14'),
  (4, DATE '1950-01-01'), (5, DATE '1951-03-02'), (6, DATE '1949-11-20')
) t(id, collected_on);""",
        query="""SELECT collected_on AS top_value,
       count(*) AS n,
       round(count(*) / (SELECT count(*) FROM specimens), 2) AS constancy
FROM specimens
GROUP BY 1
ORDER BY n DESC
LIMIT 1;"""),
    mongo=dict(
        docs="""[
  { _id: 1, collectedOn: new Date("1950-01-01") }, { _id: 2, collectedOn: new Date("1950-01-01") },
  { _id: 3, collectedOn: new Date("1950-06-14") }, { _id: 4, collectedOn: new Date("1950-01-01") },
  { _id: 5, collectedOn: new Date("1951-03-02") }, { _id: 6, collectedOn: new Date("1949-11-20") }
]""",
        pipeline="""[
  { $group: { _id: "$collectedOn", n: { $sum: 1 } } },
  { $setWindowFields: { output: { total: { $sum: "$n",
      window: { documents: ["unbounded", "unbounded"] } } } } },
  { $sort: { n: -1 } }, { $limit: 1 },
  { $project: { _id: 0,
      top_value: { $dateToString: { format: "%Y-%m-%d", date: "$_id" } },
      n: 1, constancy: { $round: [{ $divide: ["$n", "$total"] }, 2] } } }
]"""),
    jq=dict(
        input="""[{"collectedOn": "1950-01-01"}, {"collectedOn": "1950-01-01"},
 {"collectedOn": "1950-06-14"}, {"collectedOn": "1950-01-01"},
 {"collectedOn": "1951-03-02"}, {"collectedOn": "1949-11-20"}]""",
        filter="""length as $rows
| group_by(.collectedOn) | max_by(length)
| {top_value: .[0].collectedOn, n: length, constancy: (length / $rows)}"""),
    reading="Half the rows share one date, and it falls on 1 January: likely a placeholder, not a collection date.",
    sources=["Mesibov (2023) advises against \"1950-01-01\" as a placeholder for \"sometime in 1950\". https://discourse.gbif.org/t/please-share-your-dates-correctly/3824"]),
("numeric", "Unit Inconsistency"): dict(
    task="patterns",
    note="In a numeric field with no unit written, a scale change only shows as a shift in magnitude. If someone then writes the unit into the value, the field migrates to Text.",
    sql=dict(
        setup="""CREATE TABLE prices AS SELECT * FROM (VALUES
  (DATE '2021-01-04', 62.15), (DATE '2021-01-05', 62.37),
  (DATE '2021-01-06', 6215.0), (DATE '2021-01-07', 61.93)
) t(day, close);""",
        query="""SELECT pattern(CAST(close AS VARCHAR)) AS pattern, count(*) AS n
FROM prices
GROUP BY 1
ORDER BY n DESC;"""),
    mongo=dict(
        docs="""[
  { _id: 1, quote: { day: "2021-01-04", close: 62.15 } },
  { _id: 2, quote: { day: "2021-01-05", close: 62.37 } },
  { _id: 3, quote: { day: "2021-01-06", close: 6215.0 } },
  { _id: 4, quote: { day: "2021-01-07", close: 61.93 } }
]""",
        pipeline="""[
  { $group: { _id: pattern({ $toString: "$quote.close" }), n: { $sum: 1 } } },
  { $sort: { n: -1 } }
]"""),
    jq=dict(
        input="""{"day": "2021-01-04", "close": 62.15}
{"day": "2021-01-05", "close": 62.37}
{"day": "2021-01-06", "close": 6215.0}
{"day": "2021-01-07", "close": 61.93}""",
        slurp=True,
        filter="""[.[].close | tostring | pattern]
| group_by(.) | map({pattern: .[0], n: length})
| sort_by(-.n)[]"""),
    reading="One value has two more integer digits: a 100× jump, the shape of pence (GBp) mixed with pounds (GBP). The outlier's pattern depends on the engine's numeric type: `9999.99` in DuckDB (DECIMAL literal), `9999` in MongoDB and `9999.9` in jq (double). Compare patterns within one engine only.",
    sources=[
        "ranaroussi/yfinance [#552](https://github.com/ranaroussi/yfinance/issues/552): prices \"1/100 of actual\".",
        "ranaroussi/yfinance [PR #1110](https://github.com/ranaroussi/yfinance/pull/1110): \"Yahoo is mixing up currency units £ and pence\".",
        "Values are illustrative.",
    ]),
("numeric", "Integer as String"): dict(
    task="basic-type",
    note="Compare the declared type with what the values actually parse as. In documents, look at every nesting level: the smell can sit inside arrays.",
    sql=dict(
        setup="""CREATE TABLE stock AS SELECT * FROM (VALUES
  ('A1', '5'), ('A2', '12'), ('A3', '0'), ('A4', '7')
) t(sku, qty);""",
        query="""SELECT typeof(qty)                   AS data_type,
       count(*)                      AS n,
       count(TRY_CAST(qty AS INTEGER)) AS castable_to_integer
FROM stock
GROUP BY 1;"""),
    mongo=dict(
        docs="""[
  { _id: 1, items: [ { sku: "A1", qty: "5" }, { sku: "A2", qty: "12" } ] },
  { _id: 2, items: [ { sku: "A3", qty: "0" }, { sku: "A4", qty: "7" } ] }
]""",
        pipeline="""[
  { $unwind: "$items" },
  { $group: {
      _id: { $type: "$items.qty" },
      n: { $sum: 1 },
      castableToInt: { $sum: { $cond: [
        { $ne: [{ $convert: { input: "$items.qty", to: "int", onError: null } }, null] },
        1, 0] } } } }
]"""),
    jq=dict(
        input="""[
  {"id": 1, "items": [{"sku": "A1", "qty": "5"}, {"sku": "A2", "qty": "12"}]},
  {"id": 2, "items": [{"sku": "A3", "qty": "0"}, {"sku": "A4", "qty": "7"}]}
]""",
        filter="""[.. | objects | select(has("qty")) | .qty]
| {types: (map(type) | unique), n: length,
   castable_to_integer: (map(select(test("^-?[0-9]+$"))) | length)}"""),
    reading="Every value is a string, and every one parses as an integer.",
    sources=["Foidl et al. (2022) §4.2.2."]),
("numeric", "Dummy Value"): dict(
    task="constancy",
    note="In a numeric field, look for one repeated value outside the plausible range, often made of repeated 9s.",
    sql=dict(
        setup="""CREATE TABLE people AS SELECT * FROM (VALUES
  (1, 34), (2, 999), (3, 27), (4, 999), (5, 41), (6, 999)
) t(id, age);""",
        query="""SELECT age AS top_value,
       count(*) AS n,
       round(count(*) / (SELECT count(*) FROM people), 2) AS constancy
FROM people
GROUP BY 1
ORDER BY n DESC
LIMIT 1;"""),
    mongo=dict(
        docs="""[
  { _id: 1, person: { age: 34 } }, { _id: 2, person: { age: 999 } },
  { _id: 3, person: { age: 27 } }, { _id: 4, person: { age: 999 } },
  { _id: 5, person: { age: 41 } }, { _id: 6, person: { age: 999 } }
]""",
        pipeline="""[
  { $group: { _id: "$person.age", n: { $sum: 1 } } },
  { $setWindowFields: { output: { total: { $sum: "$n",
      window: { documents: ["unbounded", "unbounded"] } } } } },
  { $sort: { n: -1 } }, { $limit: 1 },
  { $project: { n: 1, constancy: { $round: [{ $divide: ["$n", "$total"] }, 2] } } }
]"""),
    jq=dict(
        input="""[{"age": 34}, {"age": 999}, {"age": 27},
 {"age": 999}, {"age": 41}, {"age": 999}]""",
        filter="""length as $rows
| group_by(.age) | max_by(length)
| {top_value: .[0].age, n: length, constancy: (length / $rows)}"""),
    reading="999 is the most frequent age and is not a plausible one.",
    sources=["Foidl et al. (2022) §4.2.1: \"999\" for a person's age \"possibly indicates a missing entry\"."]),
("text", "Unit Inconsistency"): dict(
    task="patterns",
    note="In a text field, the unit is written in the value, so it shows up in the pattern's alphabetic tail. Casing variants of the same unit split the histogram further.",
    sql=dict(
        setup="""CREATE TABLE ways AS SELECT * FROM (VALUES
  (1, '50'), (2, '30 mph'), (3, '60 MPH'), (4, '10 knots'), (5, '80')
) t(id, maxspeed);""",
        query="""SELECT pattern(maxspeed) AS pattern, count(*) AS n
FROM ways
GROUP BY 1
ORDER BY n DESC, pattern;"""),
    mongo=dict(
        docs="""[
  { _id: "way/1", tags: { highway: "primary", maxspeed: "50" } },
  { _id: "way/2", tags: { highway: "primary", maxspeed: "30 mph" } },
  { _id: "way/3", tags: { highway: "primary", maxspeed: "60 MPH" } },
  { _id: "way/4", tags: { waterway: "canal", maxspeed: "10 knots" } },
  { _id: "way/5", tags: { highway: "motorway", maxspeed: "80" } }
]""",
        pipeline="""[
  { $group: { _id: pattern("$tags.maxspeed"), n: { $sum: 1 } } },
  { $sort: { n: -1, _id: 1 } }
]"""),
    jq=dict(
        input="""{"type": "FeatureCollection", "features": [
  {"type": "Feature", "properties": {"maxspeed": "50"}, "geometry": null},
  {"type": "Feature", "properties": {"maxspeed": "30 mph"}, "geometry": null},
  {"type": "Feature", "properties": {"maxspeed": "60 MPH"}, "geometry": null},
  {"type": "Feature", "properties": {"maxspeed": "10 knots"}, "geometry": null},
  {"type": "Feature", "properties": {"maxspeed": "80"}, "geometry": null}
]}""",
        filter="""[.features[].properties.maxspeed | pattern]
| group_by(.) | map({pattern: .[0], n: length})
| sort_by([-.n, .pattern])[]"""),
    reading="Bare numbers (implicit km/h) sit next to three unit suffixes. Going by its code, OSRM only converts lowercase \"mph\", so \"60 MPH\" would be read as 60 km/h.",
    sources=[
        "OpenStreetMap wiki, [Key:maxspeed](https://wiki.openstreetmap.org/wiki/Key:maxspeed): km/h by default; mph and knots after a space.",
        "OSRM [`profiles/lib/measure.lua`](https://github.com/Project-OSRM/osrm-backend/blob/f2147ead8d9c6a2c724120113d9c56ab85963262/profiles/lib/measure.lua): this was worked out by reading the code, not observed in data.",
        "Values are illustrative.",
    ]),
("text", "Casing Inconsistency"): dict(
    task="patterns",
    note="Collapse each value to its casing class before counting. Raw `Aa9` patterns depend on length, which hides casing.",
    sql=dict(
        setup="""CREATE TABLE customers AS SELECT * FROM (VALUES
  (1, 'Joinville'), (2, 'JOINVILLE'), (3, 'joinville'), (4, 'Curitiba'), (5, 'Blumenau')
) t(id, city);""",
        query="""SELECT CASE WHEN city = upper(city) THEN 'UPPER'
            WHEN city = lower(city) THEN 'lower'
            ELSE 'Mixed' END AS casing,
       count(*) AS n
FROM customers
GROUP BY 1
ORDER BY n DESC, casing;"""),
    mongo=dict(
        docs="""[
  { _id: 1, address: { city: "Joinville" } }, { _id: 2, address: { city: "JOINVILLE" } },
  { _id: 3, address: { city: "joinville" } }, { _id: 4, address: { city: "Curitiba" } },
  { _id: 5, address: { city: "Blumenau" } }
]""",
        pipeline="""[
  { $group: { _id: { $switch: { branches: [
      { case: { $eq: ["$address.city", { $toUpper: "$address.city" }] }, then: "UPPER" },
      { case: { $eq: ["$address.city", { $toLower: "$address.city" }] }, then: "lower" } ],
      default: "Mixed" } }, n: { $sum: 1 } } },
  { $sort: { n: -1, _id: 1 } }
]"""),
    jq=dict(
        input="""[
  {"id": 1, "addresses": [{"city": "Joinville"}, {"city": "JOINVILLE"}]},
  {"id": 2, "addresses": [{"city": "joinville"}]},
  {"id": 3, "addresses": [{"city": "Curitiba"}, {"city": "Blumenau"}]}
]""",
        filter="""[.[].addresses[].city
  | if . == ascii_upcase then "UPPER"
    elif . == ascii_downcase then "lower" else "Mixed" end]
| group_by(.) | map({casing: .[0], n: length})
| sort_by([-.n, .casing])[]"""),
    reading="Most values are Mixed case; the UPPER and lower minorities are the same city written differently.",
    sources=["Values are illustrative."]),
}

NOTES = {
    ("time-series", "Extraneous Value"): "In time columns: a weekday prefix, a time-zone suffix, or qualifiers like \"c. 1950\" (framework author's note).",
    ("time-series", "Date as Date/Time"): None,
}
