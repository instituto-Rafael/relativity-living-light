# RLL Ω — índice de codificação 5 bits / Telex

Acesse [o relatório do mesmo texto nas mesmas cinco janelas](../NOVOexport/LOW_LEVEL_TEXT_ENCODING/TELEX_5BIT_FIXED_WINDOW_20261108/README.md).

**SOURCE:** [texto original português](../NOVOexport/LOW_LEVEL_TEXT_ENCODING/BRAILLE_FIXED_WINDOW_20261108/texto_portugues.txt).

**MÉTODO:** janela semântica 256/256/256/256/232 caracteres; limite de janela Zstd 1.024 B; comparação de 5 bits com escapes vs Braille 6 bits vs UTF-8.

**EVIDÊNCIA:** tabela `janelas.csv`; medidas verificadas localmente; GitHub CI exato ainda pendente.

**LIMITES:** ITA2 é versão estendida, não compatível com Telex original; sem inferência física RLL, sem alteração de YML.
