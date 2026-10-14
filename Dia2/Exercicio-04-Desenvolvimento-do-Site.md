# Exercício 4 — Especificação e delegação do site interativo

## Objetivo da atividade

Aprender a **transformar uma funcionalidade em GitHub Issue**, definir critérios de aceitação e delegar a implementação ao coding agent de forma controlada.

**Conceitos:** Caderno 04 — Issues como contrato de trabalho; Caderno 05 — delegação, revisão e critérios de aceitação.

## Material de partida

Modelo funcional e artefatos produzidos no Exercício 3. O site deverá utilizar **a rede neural realmente treinada**, e não uma simulação com respostas fixas.

## Desafio

Criar uma aplicação web na qual o usuário consiga **desenhar um número**, solicitar a classificação e observar o resultado e **algum comportamento real da rede neural durante a inferência**.

Antes de pedir ao Copilot que escreva o código da interface, o participante deverá **criar pelo menos uma GitHub Issue específica** para o desenvolvimento do site. A Issue pode ser dividida em outras menores, conforme as dependências encontradas.

## Ficha de requisitos da Issue

A especificação do site deve contemplar:

- **Entrada interativa:** área de desenho utilizável com mouse e toque.
- **Repetição da experiência:** opção de limpar o desenho e tentar novamente.
- **Pré-processamento:** conversão do desenho para a representação exigida pelo modelo.
- **Resultado:** identificação da classe prevista e apresentação de pontuações ou probabilidades, de acordo com a saída real do modelo.
- **Inspeção da rede:** maneira compreensível de visualizar arquitetura e/ou ativações ou outras informações reais do modelo. **Animação decorativa não é suficiente.**
- **Compatibilidade:** funcionamento em navegadores modernos e possibilidade de hospedagem estática no GitHub Pages.
- **Verificação:** critérios e evidências que permitam distinguir uma interface funcional de uma demonstração apenas visual.

## Como realizar

1. Conversar com o agente sobre os requisitos da experiência web e as restrições impostas pelo modelo treinado.
2. Registrar a especificação numa ou mais **Issues do GitHub**, com critérios de aceitação verificáveis.
3. Solicitar ao Copilot um plano de implementação e revisar dependências, arquivos afetados e verificações previstas.
4. Delegar a execução gradualmente, testar a interface e examinar alterações antes de aceitá-las.
5. Registrar na Issue as evidências de implementação e os commits ou Pull Request relacionados.

Nesta atividade o objetivo é **usar o agente para desenvolver o site**, não escrever a interface manualmente ou aceitar uma demonstração que apenas aparenta classificar números.

## Ponto de verificação

Verificar se a aplicação usa o modelo e os artefatos efetivamente treinados, se o desenho é convertido corretamente e se a visualização representa dados reais da rede.

## Entregável

**Issue(s) documentadas**, implementação inicial da interface interativa, verificações executadas e mudanças rastreáveis em commits ou Pull Request. A publicação pública ocorrerá no exercício seguinte.
