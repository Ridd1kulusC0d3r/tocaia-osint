# Previsibilidade como hipótese testável

Prever aqui significa estimar um evento digital observável, com janela e regra de resolução explícitas. A confiança do analista na evidência é registrada separadamente da probabilidade do evento. Uma narrativa convincente não é uma avaliação de desempenho.

## Contrato da previsão

Antes da janela de teste, registrar:

- ID, unidade de análise e escopo autorizado;
- evento binário, início/fim com fuso, instante de emissão;
- cutoff dos dados usados e versão do modelo ou método humano;
- probabilidade entre 0 e 1 e justificativa;
- probabilidade da referência simples, obtida somente com dados anteriores;
- fontes, regra de cobertura e regra objetiva de resolução;
- alternativas, limitações e condição para abstenção;
- ao encerrar a janela: resultado 0/1 ou `null` se não resolvível.

Exemplo admissível: “A conta editorial sintética publicará ao menos um original na janela semanal W.” Não extrapolar para paradeiro, intenção criminosa, diagnóstico ou vulnerabilidade de uma pessoa.

## Teste temporal

Separar desenvolvimento, validação e teste em ordem temporal. Fixar thresholds na validação. Comparar com taxa-base e persistência calculadas antes do cutoff. Evitar que duplicatas do mesmo evento ou contas da mesma campanha vazem entre conjuntos. Quando se avalia generalização para novas contas, separar também por conta/campanha. Janelas sobrepostas exigem tratamento da dependência.

Repetir a avaliação em períodos posteriores e reportar mudanças de plataforma. Amostras sintéticas verificam mecânica; não medem validade em pessoas ou plataformas reais.

## Métricas e abstenção

Para previsões binárias resolvidas, Brier = média de `(p - resultado)²`; menor é melhor. Brier skill = `1 - Brier_modelo / Brier_referência`; valores negativos indicam desempenho inferior à referência. Quando o Brier da referência é zero, o skill é indefinido e deve ser `null`.

Reportar total, resolvidas e não resolvidas, distribuição dos resultados, cobertura e desempenho por período. Nunca converter janela sem observabilidade em resultado negativo. Exibir a taxa de abstenção junto com desempenho: excluir os casos difíceis pode melhorar artificialmente a aparência do modelo.

Calibração exige muitos casos: agrupar probabilidades e comparar com frequências observadas, informando o tamanho de cada grupo. O Brier sozinho não comprova calibração. Intervalos de incerteza devem respeitar dependência por conta/período. Falsos positivos, falsos negativos e utilidade dependem de um limiar de decisão declarado e de custos definidos no escopo.

## CLI disponível

```bash
tocaia-evaluate examples/synthetic-forecast/forecasts.json
```

O arquivo de entrada é uma lista JSON. Campos exigidos por registro: `forecast_id`, `probability`, `baseline_probability`, `outcome` (0, 1 ou null). Campos adicionais do contrato são preservados no arquivo de origem, mas **não são auditados pelo avaliador atual**. Usar [forecast-record.json](../templates/forecast-record.json) no trabalho analítico.

O avaliador rejeita IDs repetidos, amostras vazias, valores não finitos e probabilidades inválidas. Ele calcula pontuações das previsões fornecidas; não gera previsões, verifica proveniência, detecta vazamento temporal ou certifica validade investigativa. A saída inclui abstenções. Um arquivo sem resultados resolvidos retorna métricas `null`.

## Gate antes de alegar utilidade

Publicar protocolo, dados adequados ao escopo, definição de cobertura, benchmark temporal, desempenho por grupo pertinente, erros e revisão independente. Demonstrar ganho sobre uma referência prévia em dados fora do desenvolvimento. Até lá, rotular como **experimental / desempenho não validado**.
