# MNIST — dados para o Exercício 3

**Dataset exigido:** MNIST de dígitos manuscritos (Yann LeCun, Corinna Cortes e colaboradores). São **60.000 imagens de treino** e **10.000 imagens de teste**, em escala de cinza, de **28 × 28 pixels**, com rótulos de 0 a 9.

Os arquivos originais são distribuídos em formato **IDX compactado com gzip**, preservados sem conversão. A fonte é o espelho do [CVDF](https://github.com/cvdfoundation/mnist), utilizado também pelo [TensorFlow Datasets](https://github.com/tensorflow/datasets/blob/master/tensorflow_datasets/image_classification/mnist.py).

## Arquivos do dataset

| Arquivo | Conteúdo | Registros |
| --- | --- | ---: |
| `train-images-idx3-ubyte.gz` | Imagens de treino | 60.000 |
| `train-labels-idx1-ubyte.gz` | Rótulos de treino | 60.000 |
| `t10k-images-idx3-ubyte.gz` | Imagens de teste | 10.000 |
| `t10k-labels-idx1-ubyte.gz` | Rótulos de teste | 10.000 |

**Os arquivos binários serão versionados em `data/` pelo workflow de importação do repositório**, quando o GitHub Actions estiver autorizado para gravar na branch principal. Em qualquer ambiente, pode-se obtê-los usando o procedimento abaixo, mesmo que o diretório `data/` ainda não esteja preenchido.

## Disponibilização reproduzível, sem pacotes adicionais

Com **Python 3** instalado, a partir da raiz do repositório da formação:

```bash
python Dia2/Dataset-MNIST/download_mnist.py
```

O programa baixa os **quatro arquivos oficiais** para `Dia2/Dataset-MNIST/data/`, verifica seu tamanho, **hash MD5 de referência** e cabeçalho IDX, e informa o resultado. Não requer PyTorch, TensorFlow, NumPy, `npx` ou dependências de terceiros.

O downloader não contém código de treino ou de rede neural; ele apenas coloca à disposição o dataset comum da atividade. Os participantes devem orientar o **seu próprio agente** a preparar a leitura, o pré-processamento, o treinamento e a avaliação.

As bibliotecas eventualmente escolhidas para o classificador **podem exigir instalação**. A ausência de dependências extras se aplica somente ao downloader e às skills em Markdown, não ao desenvolvimento completo de machine learning.

## Separação dos dados

- Os **60.000 exemplos de treino** poderão ser reorganizados pelo participante em treinamento e validação, documentando seu critério.
- Os **10.000 exemplos de teste** não devem servir para decidir arquitetura nem hiperparâmetros; devem ser usados para avaliação final de generalização.
- As **[nove imagens do desafio](../Desafio/)** não fazem parte do MNIST. Use-as apenas no desafio independente, sem treinamento ou ajuste a partir desses nove casos.

## Fontes, integridade e licença

- [CVDF — espelho do MNIST](https://github.com/cvdfoundation/mnist)
- [TensorFlow Datasets — MNIST](https://www.tensorflow.org/datasets/catalog/mnist)
- [Keras — formato e licença](https://keras.io/api/datasets/mnist/)
- [Torchvision — valores MD5 oficiais utilizados na verificação](https://github.com/pytorch/vision/blob/main/torchvision/datasets/mnist.py)

Yann LeCun e Corinna Cortes detêm direitos autorais sobre o MNIST, derivado de dados NIST. A documentação do Keras informa disponibilização sob **Creative Commons Attribution–ShareAlike 3.0**: https://creativecommons.org/licenses/by-sa/3.0/

**Crédito sugerido:** LeCun, Y.; Cortes, C.; Burges, C. J. *The MNIST Database of Handwritten Digits*.

Os arquivos são disponibilizados para a atividade preservando origem e atribuição. O exercício **não inclui um modelo treinado nem exemplos de solução**.
