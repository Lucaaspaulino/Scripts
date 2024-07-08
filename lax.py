import paramiko
from jumpssh import SSHSession
import requests
from netmiko import ConnectHandler
from netmiko.exceptions import ReadTimeout
import pandas as pd
import re
import time

# Credenciais de acesso
GUACAMOLE_HOST = '102.130.68.190'
GUACAMOLE_USER = 'frederico.oliveira'
GUACAMOLE_PASSWORD = '239507/Astr23'

# Função para se conectar ao servidor Guacamole e executar um comando
def connect_and_execute_command(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

# Função para extrair os nomes dos servidores a partir da saída do comando
def extract_server_names(output):
    lines = output.strip().split('\n')
    servers = []
    for line in lines:
        parts = line.split()
        server_name = parts[-1]
        servers.append(server_name)
    return servers

# Função para coletar informações de portas dos servidores usando jumpssh
def collect_server_data(servers):
    data = []
    for hostname in servers:
        try:
            session = requests.Session()
            gateway_session = SSHSession(GUACAMOLE_HOST, GUACAMOLE_USER, password=GUACAMOLE_PASSWORD).open()
            remote_session = gateway_session.get_remote_session(str(hostname), GUACAMOLE_USER, password=GUACAMOLE_PASSWORD)
            
            port_1gb_cmd = 'show interfaces descriptions | match ge-| match FREE | count'
            port_10gb_cmd = 'show interfaces descriptions | match xe-| match FREE | count'
            port_100gb_cmd = 'show interfaces descriptions | match et-| match FREE | count'
            
            port_1gb = remote_session.get_cmd_output(port_1gb_cmd).strip()
            port_10gb = remote_session.get_cmd_output(port_10gb_cmd).strip()
            port_100gb = remote_session.get_cmd_output(port_100gb_cmd).strip()
            
            data.append({
                'Host': hostname,
                'Portas de 1GB': port_1gb,
                'Portas de 10GB': port_10gb,
                'Portas de 100GB': port_100gb
            })
            
            print_server_data(hostname, port_1gb, port_10gb, port_100gb)
        
        except Exception as e:
            print(f'Erro ao conectar ou enviar comandos ao host {hostname}: {str(e)}')
            continue
    return data

# Função para imprimir os dados do servidor
def print_server_data(hostname, port_1gb, port_10gb, port_100gb):
    print('\n')
    print('############################################')
    print(f'Host: {hostname}')
    print(f'Portas de 1GB : {port_1gb}')
    print(f'Portas de 10GB : {port_10gb}')
    print(f'Portas de 100GB : {port_100gb}')
    print('############################################')

# Função para coletar informações de portas dos dispositivos usando netmiko
def collect_device_data(devices):
    data = []
    for device in devices:
        try:
            with ConnectHandler(**device) as net_connect:
                net_connect.read_timeout = 20
                prompt = net_connect.find_prompt()
                escaped_prompt = re.escape(prompt)

                # Adicionando linhas de debug
                print(f'Enviando comandos para o dispositivo {device["host"]}')

                # Limpar o buffer antes de enviar cada comando
                net_connect.clear_buffer()

                port_1g = net_connect.send_command('show port description | match FREE | match 1G | count', expect_string=escaped_prompt).strip()
                print(f'Saída do comando para 1G do dispositivo {device["host"]}: {port_1g}')
                time.sleep(3)  # Pequena pausa para garantir que o comando foi processado

                # Adicionando mais debug
                output_10g = net_connect.send_command('show port description | match FREE | match 10G | count', expect_string=escaped_prompt)
                print(f'Output bruto para 10G do dispositivo {device["host"]}: {output_10g}')
                port_10g = output_10g.strip()
                print(f'Saída do comando para 10G do dispositivo {device["host"]}: {port_10g}')
                time.sleep(3)  # Pequena pausa para garantir que o comando foi processado

                # Adicionando mais debug
                output_100g = net_connect.send_command('show port description | match FREE | match 100G | count', expect_string=escaped_prompt)
                print(f'Output bruto para 100G do dispositivo {device["host"]}: {output_100g}')
                port_100g = output_100g.strip()
                print(f'Saída do comando para 100G do dispositivo {device["host"]}: {port_100g}')
                time.sleep(3)  # Pequena pausa para garantir que o comando foi processado

                data.append({
                    'Host': device['host'],
                    'Portas de 1GB': port_1g,
                    'Portas de 10GB': port_10g,
                    'Portas de 100GB': port_100g
                })

                print(f'Portas de 1G do dispositivo {device["host"]}: {port_1g}')
                print(f'Portas de 10G do dispositivo {device["host"]}: {port_10g}')
                print(f'Portas de 100G do dispositivo {device["host"]}: {port_100g}')
        except ReadTimeout:
            print(f'Timeout ao tentar executar comandos no dispositivo {device["host"]}')
        except Exception as e:
            print(f'Erro ao conectar ou enviar comandos ao dispositivo {device["host"]}: {str(e)}')
    return data

# Função principal
def main():
    # Comando a ser executado no servidor Guacamole
    guacamole_command = 'cat /etc/hosts | grep rt'
    
    # Conectando ao servidor Guacamole e obtendo os nomes dos servidores
    output = connect_and_execute_command(GUACAMOLE_HOST, GUACAMOLE_USER, GUACAMOLE_PASSWORD, guacamole_command)
    servers = extract_server_names(output)
    
    # Coletando dados dos servidores
    server_data = collect_server_data(servers)
    
    # Informações dos dispositivos
    devices = [
        {
            'device_type': 'nokia_sros',
            'host': 'trt_nce1_bsb_bsa',
            'ip': '170.238.232.6',
            'username': GUACAMOLE_USER,
            'password': GUACAMOLE_PASSWORD,
            'port': 22,
            'verbose': True
        },
        {
            'device_type': 'nokia_sros',
            'host': 'trt_nce1_tel_gna',
            'ip': '170.238.232.7',
            'username': GUACAMOLE_USER,
            'password': GUACAMOLE_PASSWORD,
            'port': 22,
            'verbose': True
        },
        {
            'device_type': 'nokia_sros',
            'host': 'trt_nce1_btp_cgb',
            'ip': '170.238.232.196',
            'username': GUACAMOLE_USER,
            'password': GUACAMOLE_PASSWORD,
            'port': 22,
            'verbose': True
        }
    ]
    
    # Coletando dados dos dispositivos
    device_data = collect_device_data(devices)
    
    # Combinando todos os dados
    all_data = server_data + device_data
    
    # Criando um DataFrame com os dados
    df = pd.DataFrame(all_data)
    
    # Exportando para um arquivo Excel
    df.to_excel('resultados.xlsx', index=False)
    
    print('Resultados exportados para resultados-portas-livres.xlsx')

# Executando a função principal
if __name__ == "__main__":
    main()
