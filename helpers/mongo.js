// Monta uma expressão de agregação que mapeia cada caractere para A / a / 9.
const pattern = (s) => ({ $reduce: {
  input: { $range: [0, { $strLenCP: s }] }, initialValue: "",
  in: { $let: { vars: { c: { $substrCP: [s, "$$this", 1] } },
    in: { $concat: ["$$value", { $switch: { branches: [
      { case: { $regexMatch: { input: "$$c", regex: /[A-Z]/ } }, then: "A" },
      { case: { $regexMatch: { input: "$$c", regex: /[a-z]/ } }, then: "a" },
      { case: { $regexMatch: { input: "$$c", regex: /[0-9]/ } }, then: "9" } ],
      default: "$$c" } }] } } } } });
