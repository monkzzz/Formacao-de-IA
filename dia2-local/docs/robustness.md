# Reconhecimento com maior robustez

Os candidatos de robustez continuam a usar uma CNN para dígitos e outra para
letras. Mantêm a arquitetura e o pré-processamento usados no navegador, mas
recebem treino adicional com variações de escrita e ruído. Os checkpoints,
pesos e relatórios originais permanecem disponíveis.

## Treino e seleção

- Usar apenas as partições de treino MNIST e EMNIST Letters e os mesmos índices
  de treino/validação das experiências originais.
- Incluir rotações pequenas, escala, translação, inclinação, deformação suave,
  variação de espessura, partículas, linhas fracas e pequenas interrupções.
  Não inverter nem rodar caracteres em 90 graus, pois isso pode mudar a classe.
- Manter aproximadamente 25% dos exemplos de cada lote sem perturbação adicional.
- Afinar os pesos originais durante dez épocas, com AdamW, taxa inicial de
  aprendizagem de 0,0003 e redução por cosseno até 0,00002.
- Selecionar pela média da entropia cruzada nas validações limpa e perturbada.
  Exigir melhoria na acurácia perturbada e limitar a perda na acurácia limpa a
  0,2 pontos percentuais para dígitos e 0,4 para letras.

As perturbações de validação são fixas. O teste usa outra semente, definida
antes do treino. O código só carrega as partições oficiais de teste depois de
selecionar os pesos. Nenhuma imagem ou previsão do Desafio entra no treino ou
na seleção.

## Avaliação e limites

Comparar o candidato e o modelo original sobre os mesmos exemplos oficiais e
sobre as mesmas versões sinteticamente perturbadas desses exemplos. Os
relatórios [de dígitos](../reports/robust-digits.json) e
[de letras](../reports/robust-letters.json) incluem contagens, matrizes de
confusão, histórico, critérios e identificação dos pesos.

O teste sintético mede apenas esta família de perturbações, aplicada aos
caracteres já normalizados. Não mede toda a cadeia de upload para fotografias
ou CAPTCHA, nem comprova melhoria nos dez casos oficiais do Desafio.
O resultado original do Desafio continua a descrever o primeiro modelo.

Na avaliação final dos novos pesos, o Desafio permaneceu em **2 acertos em 10**.
O [registo dos pesos e do código](../reports/robust-challenge-freeze.json), as
[previsões brutas](../reports/robust-challenge-raw.json) e a
[comparação](../reports/robust-challenge-comparison.json) são separados da
primeira execução. Os resultados anteriores já estavam disponíveis: esta é
uma avaliação posterior, não uma nova primeira avaliação cega. Não houve
ajustes após este teste. As imagens oficiais contêm apenas dígitos.

## Reproduzir e verificar

Na pasta `dia2-local`, com os checkpoints originais disponíveis:

```powershell
.\.venv\Scripts\python.exe -m digitlab.robust --epochs 10 --threads 4
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
python serve.py --port 8766
# Noutro terminal:
.\.venv\Scripts\python.exe -m digitlab.robust_qa
```

O treino recusa substituir experiências já existentes. Para reproduzir,
preservar os resultados existentes e usar uma cópia separada do projeto sem
`artifacts/robust/` nem `reports/robust-*.json`.

Os novos checkpoints ficam em `artifacts/robust/` e os modelos exportados em
`dist/model/robust/`. Os binários são locais e ignorados pelo Git; devem
acompanhar a aplicação quando esta for copiada. A verificação no navegador
compara ativações e previsões com Python para as duas redes, testa uploads,
troca de modo, recuperação de falhas e preservação dos pesos originais.
