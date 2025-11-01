# 1. Usar a mesma imagem base (Ubuntu 22.04)
FROM --platform=linux/amd64 ubuntu:22.04

# 2. Instalar apenas os pacotes essenciais (Python, pip, git)
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    vim \
    && apt-get clean

# 3. Instalar TODAS as bibliotecas Python que precisamos
#    (google-generativeai para o wrapper,
#     prov para o novo padrão,
#     numpy e pandas para os scripts científicos,
#     e lxml para o parser)
RUN pip3 install \
    google-generativeai\
    pandas \
    numpy \
    prov \
    lxml \
    rdflib
# 4. Criar uma pasta de trabalho limpa
WORKDIR /app

# 5. Definir o comando padrão para iniciar o terminal
CMD ["/bin/bash"]