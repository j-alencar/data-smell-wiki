// One page per profiling task: metadata in _data/tarefas.yaml, examples in frontmatter.
export default {
  layout: "tarefa.njk",
  tags: ["tarefa"],
  eleventyComputed: {
    tarefa: (d) => d.page.fileSlug,
    title: (d) => d.tarefas[d.page.fileSlug].nome,
    crumbs: (d) =>
      `<a href="/arvore/">Árvore de smells</a> › <a href="/tarefas/">Tarefas de perfilamento</a> › ${d.tarefas[d.page.fileSlug].nome}`,
  },
};
