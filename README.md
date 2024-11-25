Este script automatiza o processo de conexão a roteadores e servidores, coleta informações sobre portas disponíveis (1GB, 10GB, e 100GB), e exporta os resultados em uma planilha Excel. Ele usa diversas bibliotecas para SSH, manipulação de dados e tratamento de saída de comandos.
Bibliotecas Utilizadas

    paramiko
        Biblioteca para realizar conexões SSH.
        Usada para se conectar ao servidor principal (Guacamole) e executar comandos de forma remota.

    jumpssh
        Permite criar uma sessão SSH via um gateway (salto SSH).
        Utilizada para acessar servidores intermediários e estabelecer sessões remotas em roteadores.

    requests
        Biblioteca para realizar requisições HTTP.
        Embora não seja usada diretamente neste código para comunicação HTTP, ela é necessária para sessões jumpssh.

    netmiko
        Framework especializado em automação de redes.
        Usado para interagir diretamente com roteadores e executar comandos para coletar dados.
        Oferece suporte a diversos tipos de dispositivos de rede, incluindo Nokia SR OS.

    pandas
        Utilizada para manipulação e organização de dados tabulares.
        Cria DataFrames com os dados coletados e exporta para um arquivo Excel.

    re
        Biblioteca para trabalhar com expressões regulares.
        Utilizada para manipular strings e processar a saída dos prompts dos dispositivos.

    time
        Fornece funcionalidades para manipular o tempo.
        Adiciona atrasos entre comandos para evitar problemas de processamento em dispositivos.

Descrição das Funções
connect_and_execute_command

    Conecta-se ao servidor Guacamole via SSH usando paramiko.
    Executa um comando remoto e retorna a saída.
    Fecha a conexão ao final.

extract_server_names

    Processa a saída do comando do servidor para extrair os nomes dos servidores ou roteadores.

collect_server_data

    Conecta-se aos servidores listados usando jumpssh.
    Executa comandos específicos para contar portas disponíveis:
        Portas de 1GB, 10GB e 100GB.
    Organiza os dados coletados em um dicionário e os retorna.

print_server_data

    Exibe as informações coletadas (portas disponíveis) para um servidor ou dispositivo.

collect_device_data

    Conecta-se diretamente a roteadores usando netmiko.
    Executa comandos para contar portas disponíveis:
    Usa filtros como "FREE" e velocidades específicas (1G, 10G, 100G).
    Trata exceções como timeouts ou erros de conexão e organiza os dados em um dicionário.

main

    Função principal que:
        Conecta-se ao servidor Guacamole e lista os servidores disponíveis.
        Coleta informações de portas dos servidores e roteadores.
        Combina os dados coletados de diferentes fontes.
        Cria um DataFrame com os resultados.
        Exporta os dados para um arquivo Excel.

Como Funciona

    Conexão ao Servidor:
        Acesse o servidor principal e execute um comando para listar os roteadores disponíveis.
        Processa a saída para extrair os nomes dos roteadores.

    Coleta de Dados dos Servidores:
        Conecta-se a cada servidor listado e coleta informações sobre portas disponíveis (1GB, 10GB, e 100GB) usando comandos específicos.

    Coleta de Dados dos Roteadores:
        Estabelece conexões diretas aos roteadores via netmiko.
        Executa comandos para identificar portas livres de diferentes velocidades.

    Exportação dos Dados:
        Combina os dados coletados de servidores e roteadores.
        Salva os dados organizados em uma planilha Excel chamada resultados.xlsx.

Destaques Técnicos

    Automação de SSH: O script combina paramiko, jumpssh, e netmiko para gerenciar diferentes tipos de conexões SSH.
    Tratamento de Exceções: Lida com erros como timeouts e falhas de conexão, evitando que o script falhe completamente.
    Exportação de Resultados: Utiliza pandas para transformar dados brutos em uma planilha Excel organizada.
    Flexibilidade: Pode ser adaptado para diferentes tipos de dispositivos ou comandos.

Como Executar

    Configure as credenciais do servidor e roteadores nas variáveis no início do código.
    Execute o script em um ambiente Python configurado com as dependências necessárias.
    O arquivo resultados.xlsx será gerado com as informações coletadas.

Requisitos

    Python: Versão >= 3.7.
    Bibliotecas Necessárias:
    Instale com:

    pip install paramiko jumpssh requests netmiko pandas

    Acesso a Dispositivos de Rede: Certifique-se de que as conexões SSH estejam configuradas e acessíveis.

Este projeto é uma demonstração de como automatizar tarefas de rede utilizando Python, otimizando a coleta de informações e a integração com ferramentas de rede.
