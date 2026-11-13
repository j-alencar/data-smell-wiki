// Directory data shared by the three world folders.
export const smellPage = (mundoId, mundoNome) => ({
  layout: "smell.njk",
  tags: ["smell"],
  mundoId,
  eleventyComputed: {
    title: (d) => d.smell,
    crumbs: (d) => `<a href="/arvore/">Árvore de smells</a> › ${mundoNome} › ${d.smell}`,
    // {arq, migra, ...} for this smell in this world, from nav.js
    item: (d) => d.nav.find((m) => m.id === mundoId).unicos.find((s) => s.nome === d.smell),
  },
});
