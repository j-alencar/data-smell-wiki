CREATE FUNCTION pattern(v text) RETURNS text IMMUTABLE LANGUAGE sql AS $$
  SELECT regexp_replace(regexp_replace(regexp_replace(v,
    '[A-Z]', 'A', 'g'), '[a-z]', 'a', 'g'), '[0-9]', '9', 'g')
$$;
