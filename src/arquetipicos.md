---
layout: base.njk
title: Smells arquetípicos
---
Cinco smells não pertencem a um mundo de campo específico: **Dummy Value**, **Missing Value Inconsistency**, **Unit Inconsistency**, **Extraneous Value** e **Intermingled Data Type**. São os **smells arquetípicos**, marcados com <span class="alfa">α</span>.

## Por que importam

São uma possibilidade que se infiltra em quase todo tipo de dado. Datas, números e textos podem receber um valor substituto, várias formas de "vazio", unidades misturadas, informação a mais ou letras no meio de números. Por isso, valem uma verificação em qualquer campo, venha ele de que mundo vier.

## Uma história: a coluna `peso`

Uma cooperativa registra a pesagem de sacas numa coluna `peso`, numérica, em quilos.

1. **Começo.** `60.2`, `59.8`, `61.0`. Um campo do mundo numérico.
2. **[Dummy Value](/numerico/dummy-value/).** A balança quebra numa manhã e alguém digita `999` para não deixar o campo vazio. Para o banco, é um número válido.
3. **[Unit Inconsistency](/numerico/unit-inconsistency/).** Um novo posto envia o peso em gramas: `60400`. A coluna continua numérica, e a média do mês dispara.
4. **[Intermingled Data Type](/numerico/intermingled-data-type/).** Para tirar a dúvida, a equipe passa a escrever a unidade: `60400 g`, `60.2 kg`. O banco exige texto, e a coluna muda de tipo.
5. **[Extraneous Value](/texto/extraneous-value/).** Logo aparecem `aprox. 60 kg` e `60 kg (estimado)`.
6. **[Missing Value Inconsistency](/texto/missing-value-inconsistency/).** Pesagens que faltam viram `-`, `N/A` e `sem pesagem`.
7. **Já no mundo Texto.** A coluna agora também está sujeita aos smells de texto: `60 KG` contra `60 kg` ([Casing Inconsistency](/texto/casing-inconsistency/)), `60kg` contra `60 kg` ([Spacing Inconsistency](/texto/spacing-inconsistency/)).

<h2 id="text-smell-creep">Text Smell Creep</h2>

Três arquetípicos — Unit Inconsistency, Extraneous Value e Intermingled Data Type — costumam ser "resolvidos" escrevendo mais coisa no valor: a unidade, uma observação, uma letra. Fora do mundo Texto, isso obriga o campo a virar texto, como nos passos 4 a 7 acima.

Essa migração é o **Text Smell Creep**: o campo deixa o mundo de origem e passa a acumular os smells do mundo Texto, além dos que já tinha. Na [árvore](/arvore/), esses smells trazem o aviso "→ pode migrar para Texto".
