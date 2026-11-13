// Derived navigation: per world, the smells with slug, type and archetypal flag.
import fs from "node:fs";
import yaml from "js-yaml";

const load = (f) => yaml.load(fs.readFileSync(new URL(f, import.meta.url), "utf8"));
const smells = load("./smells.yaml");
const mundos = load("./mundos.yaml");

const slug = (s) => s.toLowerCase().replaceAll("/", "-").replaceAll(" ", "-");

export default function () {
  const item = (m, nome, arq) => ({
    nome,
    url: `/${m.id}/${slug(nome)}/`,
    tipo: smells[nome].tipo,
    arq,
    migra: arq && m.id !== "texto" && mundos.migram.includes(nome),
  });
  return mundos.lista.map((m) => {
    const especificos = m.especificos.map((n) => item(m, n, false));
    const arquetipicos = mundos.arquetipicos.map((n) => item(m, n, true));
    // Unique pages in the world, archetypal flag wins (sidebar).
    const unicos = [
      ...m.especificos.filter((n) => !mundos.arquetipicos.includes(n)).map((n) => item(m, n, false)),
      ...arquetipicos,
    ];
    return { ...m, especificos, arquetipicos, unicos };
  });
}
