---
---
Como o [tipo básico](/tarefas/basic-type/), o tipo de dado concreto se reconhece pelo padrão dos valores: timestamp, boolean ou int seguem um padrão fixo, às vezes específico do SGBD. Prefira o tipo mais específico e evite char e varchar sempre que possível.[@abedjan2015]

Quando a coluna já tem esquema, a tarefa é uma leitura de metadados, não um cálculo sobre os valores:

- **DuckDB e PostgreSQL:** `information_schema.columns`; por valor, `typeof` (DuckDB) e `pg_typeof` (PostgreSQL).
- **MongoDB:** não há esquema fixo; `$type` devolve o tipo BSON de cada valor, que pode variar de documento para documento.
- **JSON:** só há `string`, `number`, `boolean`, `null`, `array` e `object`; o jq expõe esse tipo com `type`.

O smell aparece quando o tipo declarado não combina com os valores, como inteiros guardados em ponto flutuante. Compare o tipo extraído aqui com o que o [tipo básico](/tarefas/basic-type/) e as [casas decimais](/tarefas/decimals/) dizem dos valores.
