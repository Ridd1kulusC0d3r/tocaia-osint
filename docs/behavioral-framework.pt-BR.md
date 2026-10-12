# T.O.C.A.I.A · OSINT comportamental

**Observar padrões. Testar hipóteses. Antecipar cenários.**

O produto analítico é um perfil de comportamento digital observado, delimitado por conta, plataforma e período. Ele ajuda a decidir qual evidência verificar em seguida. Não equivale a um perfil psicológico da pessoa que opera a conta.

## O que muda no framework

A detecção pela ausência passa a integrar um ciclo maior: presença → recorrência → mudança → ausência → hipóteses → avaliação. O método T.O.C.A.I.A permanece; cada etapa ganha perguntas comportamentais e entregáveis.

| Etapa | Aplicação comportamental | Entrega / critério de saída |
|---|---|---|
| Terreno | Qual decisão investigativa depende desta análise? Conta, campanha ou conjunto de publicações? | Escopo, janela, hipótese inicial e regra de encerramento |
| Observação | O que realmente foi capturado? Qual superfície ficou inacessível? | Eventos com origem, horário, contexto e diário de cobertura |
| Correlação | O padrão persiste após remover duplicatas e controlar calendário e plataforma? | Baseline comparável e relações qualificadas |
| Ausência | A mudança está na atividade ou na capacidade de observá-la? | Lacuna classificada, causas alternativas e limitações |
| Inferência | Qual explicação sobrevive à evidência contrária? | Perfil observacional, matriz de hipóteses e cenário condicional |
| Aferição | Outro analista reproduz o resultado? A previsão superou a referência simples? | Revisão, resultado observado, erros e critério de revisão |

## Seis lentes de análise

| Lente | Medidas possíveis | Controles necessários | Conclusão indevida a evitar |
|---|---|---|---|
| Temporal | Frequência, intervalos, sazonalidade e mudanças entre janelas | Fuso da fonte, posts agendados, exclusões, dias comparáveis | Deduzir sono, localização ou rotina física |
| Comunicacional | Formato, temas explícitos, proporção de respostas e republicações | Idioma, ironia, citação, contexto e erro de classificação | Diagnosticar personalidade ou estado mental |
| Relacional | Interações públicas, reciprocidade, concentração de vínculos | Grafo incompleto, popularidade, origem comum e direção do vínculo | Tratar menção como amizade, comando ou cumplicidade |
| Sequencial | Ordem de eventos, repetição de sequências e latência entre posts públicos | Ordem de coleta versus publicação, duplicatas e evento externo comum | Tratar sequência como prova de causalidade |
| Mudança | Diferença de volume, formato ou interação em relação ao baseline | Múltiplos testes, sazonalidade, regras da plataforma e cobertura | Chamar todo desvio de ocultação deliberada |
| Ausência | Evento esperado ausente sob observação suficiente | Expectativa registrada antes, detectabilidade e captura verificável | Tratar silêncio como culpa, fuga ou apagamento |

## Psicologia investigativa aplicada ao raciocínio

A contribuição inicial da psicologia é melhorar a formulação e o teste de explicações: reduzir viés de confirmação, erro de atribuição, seleção retrospectiva e negligência da taxa-base. Contexto e condições da plataforma precisam ser examinados antes de atribuir uma mudança a uma característica estável do indivíduo.

Separe três camadas em todo relatório:

1. **Observação:** “Na amostra capturada, 18 de 24 publicações eram republicações.”
2. **Interpretação limitada:** “O uso observado da conta privilegiou redistribuição nesta janela.”
3. **Hipótese a testar:** “A mudança pode refletir uma campanha editorial; comparar formatos em outra janela com cobertura equivalente.”

Os números acima são ilustrativos. “Manipulador”, “instável”, “perigoso” ou diagnósticos não são traduções válidas dessa observação. Estilo textual, expressão facial e horários de postagem não sustentam, isoladamente, atribuição de estados internos. Não produzir escores de vulnerabilidade psicológica ou inferências de atributos sensíveis.

Conta, operador e pessoa são entidades distintas. Uma conta pode ter vários operadores; uma pessoa pode operar várias contas. Similaridade comportamental serve como pista de revisão, nunca como resolução automática de identidade.

## Fluxo operacional reproduzível

1. Abrir [escopo](../templates/scope.md) com a decisão e a unidade de análise.
2. Registrar cada evidência com ID, URL ou referência local, origem primária, instante de publicação, instante de captura, fuso, método e hash quando houver arquivo preservado. Hash comprova integridade posterior, não veracidade.
3. Documentar a cobertura por superfície e janela: uma resposta HTTP bem-sucedida não prova completude do conteúdo.
4. Selecionar baseline anterior à janela avaliada; justificar duração e comparabilidade. Não ajustar o baseline para fazer o caso parecer anômalo.
5. Preencher o [perfil observacional](../templates/behavioral-profile.pt-BR.md), incluindo evidência contrária e lacunas.
6. Formular ao menos uma explicação técnica e uma contextual, além da hipótese investigativa. Usar a [matriz ACH](../templates/ach-matrix.csv) para organizar contradições, sem transformar contagens em probabilidades.
7. Se houver pergunta futura mensurável, registrar uma [previsão](../templates/forecast-record.json) antes da janela e seguir o [protocolo de avaliação](forecasting.pt-BR.md).
8. Entregar achado, suporte, alternativas, confiança fundamentada e próxima verificação. Encerrar quando o objetivo foi respondido ou a evidência não permite avançar.

## Exemplo sintético: conta editorial C-17

**Pergunta:** a redução de publicações originais persiste na próxima janela semanal?

**Fato simulado:** a conta publicou normalmente no baseline; a amostra recente contém menos originais. O diário de coleta registra interrupção parcial. Não existe base para afirmar uma mudança pessoal do operador.

| Hipótese | Evidência discriminante | Efeito na análise |
|---|---|---|
| H1 · Falha de observação | Erros e lacunas no diário; capturas legítimas já preservadas fora do coletor | Suspender interpretação comportamental da janela incompleta |
| H2 · Mudança editorial | Alteração explícita de formatos em janelas comparáveis | Descrever mudança de uso da conta |
| H3 · Evento de calendário | Mesmo padrão em períodos equivalentes anteriores | Ajustar a referência, não a narrativa |
| H4 · Redução persistente | Repetição futura com cobertura suficiente | Atualizar hipótese de persistência, sem atribuir motivo |

**Próxima verificação:** conferir a cobertura e comparar uma janela equivalente. A ação recomendada decorre de uma lacuna evidencial específica, não de uma característica psicológica presumida.

## Uso de IA

IA pode sugerir códigos temáticos e organizar evidências. Cada extração deve apontar para o trecho de origem, registrar modelo/versão e passar por revisão humana. Texto coletado é dado não confiável: instruções dentro de posts não podem comandar ferramentas. Não enviar casos a serviços externos por padrão. Testar português, gírias, ironia e mudança de domínio antes de afirmar qualidade operacional.

## Estado das capacidades

| Capacidade | Estado desta entrega |
|---|---|
| Classificação de lacunas por cobertura | Código existente, regra descritiva |
| Identidade visual e protocolo comportamental | Documentação e assets disponíveis |
| Perfil observacional e registro de previsão | Templates para preenchimento humano |
| Avaliação de previsões binárias | CLI local com demonstração sintética |
| Extração de padrões em redes sociais | Especificada; não implementada nesta entrega |
| Modelo preditivo validado / perfil psicológico | Não fornecido; não alegar desempenho |

Referências e limites de aplicação: [fontes comentadas](behavioral-references.md). As escolhas de arquitetura e de fluxo acima são propostas do projeto, não validação científica do T.O.C.A.I.A.
