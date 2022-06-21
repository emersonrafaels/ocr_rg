# :sunglasses: Nossos modelos

O projeto de OCR RG utiliza quatro modelos para obtenção dos dados:

## ♤♠♧♣  Modelos

 - **Modelo 1** - Detecção de campos utilizando HOG e SVM (Em desenvolvimento)
 - **Modelo 2** - Aplicação de uma máscara de acordo com o template do OCR, obtendo os campos de acordo com as coordenadas pré definidas.
 - **Modelo 3** - Aplicação do OCR no documento inteiro.
 - **Modelo 4** - Aplicação da técnica de bounding box recursivo, identificando locais que possuem texto e realizando o OCR em seguida.
