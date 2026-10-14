# Exercício 5 — Inferência local e publicação no GitHub Pages

## Objetivo da atividade

Aprender a **integrar um modelo treinado numa aplicação web estática**, testar sua equivalência com a implementação original e orientar o agente na publicação e verificação em ambiente real.

**Conceitos:** integração, limites de autonomia, validação de deployment e reprodução do comportamento do modelo.

## Material de partida

Modelo e pesos do Exercício 3, interface e Issues do Exercício 4.

## Requisito central

A classificação deverá acontecer **no navegador do usuário**, sem enviar o desenho para uma API de inferência e sem depender de um backend remoto de classificação. O site deverá funcionar hospedado no **GitHub Pages**.

## Ficha de requisitos

1. **Investigar opções de execução local:** discutir com o Copilot formas de exportar e carregar o modelo no navegador. Avaliar alternativas compatíveis com a arquitetura escolhida, sem impor uma biblioteca.
2. **Integrar o modelo real:** exportar os pesos e os arquivos necessários e conectá-los ao site estático.
3. **Preservar o pré-processamento:** verificar que o desenho submetido pelo usuário recebe transformações equivalentes às usadas no treinamento.
4. **Verificar equivalência:** comparar saídas da implementação de origem e da versão web sobre as mesmas entradas de referência, registrando as diferenças e tolerâncias aceitas.
5. **Testar a experiência:** conferir desenho por mouse e toque, limpeza, inferência, resultados, visualização da rede e mensagens de erro.
6. **Publicar:** configurar GitHub Pages com o agente e **revisar qualquer ação de publicação ou alteração de configuração antes de autorizá-la**.
7. **Validar o resultado publicado:** abrir a URL pública fora do ambiente local e verificar carregamento dos artefatos, classificação e ausência de dependência de servidor de inferência.

## O que observar durante o trabalho com o agente

Se a saída do site divergir daquela produzida pelo modelo original, investigar causas possíveis com base em evidências, em vez de compensar diferenças por alterações manuais nas previsões. Conferir também o carregamento de arquivos, caminhos de publicação e erros do navegador.

Não considerar a tarefa concluída apenas porque o agente informa que fez o deployment: **a URL deve funcionar e a inferência deve ser testada**.

## Entregável

**Aplicação pública no GitHub Pages**, com o modelo realmente treinado executando no navegador, interface interativa e evidências de integração, testes e publicação.
