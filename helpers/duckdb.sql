CREATE MACRO pattern(v) AS
  regexp_replace(regexp_replace(regexp_replace(v,
    '[A-Z]', 'A', 'g'), '[a-z]', 'a', 'g'), '[0-9]', '9', 'g');
