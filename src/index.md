---
layout: base.njk
title: O que é isto?
---
Este é um guia de navegação para um framework que propõe **perfilar data smells** durante o desenvolvimento de pipelines de dados. Ele serve de referência para aplicar essa ideia no dia a dia: dado um campo suspeito, quais smells procurar e como procurá-los.

**Data smells** são indícios, baseados nos valores dos dados, de problemas latentes de qualidade. São causados por más práticas e podem gerar falhas no futuro, sem depender de um contexto específico (FOIDL; FELDERER; RAMLER, 2022a). O catálogo dos autores reúne 36 smells em três tipos: Credibilidade, Compreensibilidade e Consistência (FOIDL; FELDERER; RAMLER, 2022b).

**Perfilamento de dados** é o conjunto de métodos que examinam um conjunto de dados e produzem metadados sobre ele, como contagens, distribuições e padrões de valores (ABEDJAN; GOLAB; NAUMANN, 2015).

O framework liga cada smell às tarefas de perfilamento capazes de revelá-lo. Aqui, essa ligação parte do ponto de vista de quem desenvolve: você chega com um campo, não com um smell.

## Como usar

1. Na [Árvore de smells](/arvore/), escolha o mundo do campo: série temporal, numérico ou texto.
2. Escolha um smell. Filtre por tipo, se ajudar.
3. Na página do smell, veja as tarefas de perfilamento e um exemplo com entrada e saída em DuckDB, PostgreSQL, MongoDB e jq.
4. Siga para a página da tarefa e veja a quais outros smells ela se aplica.

Smells marcados com <span class="alfa">α</span> são [arquetípicos](/arquetipicos/): podem surgir em qualquer mundo. Para bancos de documentos e outros formatos, veja [Dados não relacionais](/nao-relacional/).

## Referências

- {{ referencias.abedjan2015.abnt | mdInline | safe }}
- {{ referencias.foidl2022a.abnt | mdInline | safe }}
- {{ referencias.foidl2022b.abnt | mdInline | safe }}
