---
name: ask-me
description: Entrevista orientada por perguntas para esclarecer requisitos, riscos, restrições e decisões antes de planejar ou alterar um projeto. Use quando o pedido estiver aberto, incompleto ou contiver escolhas ainda não aprovadas.
---

# Ask Me — entrevista de requisitos

## Finalidade

Ajudar a pessoa a descobrir os requisitos que faltam antes de um agente atuar. Esta skill é genérica: não define arquitetura, dataset ou projeto e não substitui uma skill específica de bootstrap.

## Procedimento

1. Inspecione o pedido e o contexto disponível. Não pergunte novamente o que já está documentado.
2. Identifique lacunas materiais sobre objetivo, limites, critérios de sucesso, público, dados, ambiente, segurança, operação e validação. Priorize apenas as relevantes para o problema.
3. Faça perguntas curtas, progressivas e adaptadas às respostas. Comece pelos pontos que podem modificar a solução; não despeje um questionário completo.
4. Para cada alternativa importante, apresente consequências e trocas relevantes sem assumir uma escolha pela pessoa. Permita respostas como "a investigar" e "não definido".
5. Separe o que foi confirmado, o que é hipótese e o que permanece pendente. Quando houver conflito entre respostas, peça esclarecimento.
6. Ao reunir informação suficiente, apresente uma síntese de objetivos, requisitos, restrições, decisões e pendências. Peça que a pessoa confirme ou corrija a síntese.
7. **Não crie arquivos, código, Issues ou configurações durante a entrevista sem autorização.** Só execute ações aprovadas depois da confirmação e conforme as instruções do repositório.
8. Caso uma nova entrevista seja iniciada, preserve as decisões já validadas; pergunte apenas sobre lacunas ou alterações.

## Verificação

O resultado deve permitir responder: o que se deseja construir, o que não se deve fazer, quais decisões dependem de pesquisa e o que é necessário validar antes de implementar.

## Origem

Implementação didática própria, inspirada no padrão de entrevista da comunidade: https://www.skills.sh/dimabytes/skills-lib/ask-me. Não é uma cópia do arquivo de terceiros e não utiliza scripts, extensões nem pacotes externos.
