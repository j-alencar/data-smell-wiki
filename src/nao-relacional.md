---
layout: base.njk
title: Dados não relacionais
---
Os mundos de campo também valem fora de tabelas.

## Valores aninhados

Em um banco de documentos, cada valor escalar dentro de um Array ou Object recebe a mesma classificação, recursivamente:

```json
{"pedido": 7, "itens": [{"qtd": "5", "entrega": "5/3/21"}]}
```

`itens[].qtd` pertence ao mundo Numérico e já traz [Integer as String](/numerico/integer-as-string/). `itens[].entrega` pertence ao mundo Série temporal e traz [Ambiguous Date/Time Format](/serie-temporal/ambiguous-date-time-format/).

O mesmo vale para qualquer coleção de valores, como as coordenadas de um sistema geoespacial: em `[-48.85, -26.30]`, cada número é um valor do mundo Numérico.

## Booleanos e binários

Um booleano cai no mundo Numérico ou Texto, conforme a representação suportada: `true`, `1`, `"true"`, `"S"`. Misturar representações traz [Synonym](/texto/synonym/), [Intermingled Data Type](/texto/intermingled-data-type/) e [Integer as String](/numerico/integer-as-string/).

Dados binários guardados como blob não têm a semântica necessária para levantar suspeita, a menos que sejam representados no mundo Numérico ou Texto, como um hexadecimal em um campo de texto.

## Tarefas de perfilamento

As tarefas de Abedjan, Golab e Naumann (2015) foram escritas pensando em dados relacionais; os autores observam que a maioria dos métodos de perfilamento se aplica apenas a dados relacionais ou foi desenvolvida para eles (§7.2). Ainda assim, muitas tarefas só olham para uma sequência de valores e funcionam igual em documentos. Por exemplo:

- `patterns`, `histogram` e `value length` sobre `itens[].qtd`, depois de achatar o array (`$unwind` no MongoDB, `.[]` no jq);
- `null values`, contando tanto `null` quanto o campo ausente;
- `basic type`, com `$type` no MongoDB ou `type` no jq.

Outras são exclusivas de sistemas relacionais. `data type` descreve o tipo que o SGBD declara para a coluna (varchar, timestamp); um documento JSON não declara tipo por campo. As tarefas de dependência (chaves únicas, dependências funcionais e de inclusão) partem de relações entre colunas e tabelas. Existem adaptações para XML, como chaves aproximadas (ABEDJAN; GOLAB; NAUMANN, 2015, §7.2), mas elas não são tratadas aqui.

<figure class="venn">
<svg viewBox="0 0 760 420" role="img" aria-label="Diagrama de Venn das tarefas de perfilamento em dados relacionais e não relacionais">
  <circle cx="300" cy="215" r="185" fill="#1565C0" fill-opacity=".10" stroke="#1565C0" stroke-width="2"/>
  <circle cx="460" cy="215" r="185" fill="#00695C" fill-opacity=".10" stroke="#00695C" stroke-width="2"/>
  <g font-family="Liberation Sans, Arial, sans-serif" font-size="15" fill="#202122" text-anchor="middle">
    <text x="190" y="22" font-weight="bold" fill="#1565C0">Relacional</text>
    <text x="570" y="22" font-weight="bold" fill="#00695C">Não relacional</text>
    <text x="200" y="190">data type</text>
    <text x="200" y="230">dependências</text>
    <text x="200" y="250" font-size="13">(UCC, FD, IND)</text>
    <g font-size="13.5">
      <text x="380" y="120">cardinalidades</text>
      <text x="380" y="146">distribuições de valores</text>
      <text x="380" y="172">basic type · decimals</text>
      <text x="380" y="198">patterns · domain</text>
      <text x="380" y="224">clustering</text>
      <text x="380" y="250">correlations</text>
      <text x="380" y="276">summaries &amp; sketches</text>
      <text x="380" y="302">sequential dep.</text>
    </g>
    <text x="565" y="200">tamanho de arrays</text>
    <text x="565" y="230">presença de campos</text>
  </g>
</svg>
<figcaption>Tarefas de perfilamento por modelo de dados. O lado não relacional mostra exemplos de metadados próprios de documentos, sem tarefa equivalente na classificação de Abedjan, Golab e Naumann (2015).</figcaption>
</figure>

Nos exemplos, quando uma tarefa não funciona em um motor, a página do smell diz por quê e mostra o resultado nos demais.

## Referências

- {{ referencias.abedjan2015.abnt | mdInline | safe }}
