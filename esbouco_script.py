import paramiko
from jumpssh import SSHSession
import requests
from netmiko import ConnectHandler
from netmiko.exceptions import ReadTimeout
import pandas as pd
import re

# Credentials
guacamole_host = '102.130.68.190'
guacamole_user = 'frederico.oliveira'
guacamole_password = '239507/Astr23'

# Connection to guacamole server
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(guacamole_host, username=guacamole_user, password=guacamole_password)

# Command to interact with server
guacamole_command = 'cat /etc/hosts | grep rt'

# Send and get commands in guacamole server
stdin, stdout, stderr = client.exec_command(guacamole_command)
output = stdout.read().decode()

# Close the SSH connection
client.close()

lines = output.strip().split('\n')

# Colocando o nome dos routers dentro de uma lista.
servers = []

for line in lines:
    parts = line.split()
    server_name = parts[-1]
    servers.append(server_name)

# Lista para armazenar os resultados
data = []

# Para cada hostname, executar comandos remotos
for hostname in servers:
    try:
        session = requests.Session()
        gateway_session = SSHSession(guacamole_host, guacamole_user, password=guacamole_password).open()
        remote_session = gateway_session.get_remote_session(str(hostname), guacamole_user, password=guacamole_password)
        
        port_1gb_cmd = 'show interfaces descriptions | match ge-| match FREE | count'
        port_10gb_cmd = 'show interfaces descriptions | match xe-| match FREE | count'
        port_100gb_cmd = 'show interfaces descriptions | match et-| match FREE | count'
        
        port_1gb = remote_session.get_cmd_output(port_1gb_cmd).strip()
        port_10gb = remote_session.get_cmd_output(port_10gb_cmd).strip()
        port_100gb = remote_session.get_cmd_output(port_100gb_cmd).strip()
        
        # Adiciona os resultados à lista
        data.append({
            'Host': hostname,
            'Portas de 1GB': port_1gb,
            'Portas de 10GB': port_10gb,
            'Portas de 100GB': port_100gb
        })

        print('\n')
        print('############################################')
        print(f'Host: {hostname}')
        print(f'Portas de 1GB : {port_1gb}')
        print(f'Portas de 10GB : {port_10gb}')
        print(f'Portas de 100GB : {port_100gb}')
        print('############################################')
        
    except Exception as e:
        print(f'Erro ao conectar ou enviar comandos ao host {hostname}: {str(e)}')
        continue

# Informações dos dispositivos
devices = [
    {
        'device_type': 'nokia_sros',
        'host': 'trt_nce1_bsb_bsa',
        'ip': '170.238.232.6',
        'username': guacamole_user,
        'password': guacamole_password,
        'port': 22,
        'verbose': True
    },
    {
        'device_type': 'nokia_sros',
        'host': 'trt_nce1_tel_gna',
        'ip': '170.238.232.7',
        'username': guacamole_user,
        'password': guacamole_password,
        'port': 22,
        'verbose': True
    },
    {
        'device_type': 'nokia_sros',
        'host': 'trt_nce1_btp_cgb',
        'ip': '170.238.232.196',
        'username': guacamole_user,
        'password': guacamole_password,
        'port': 22,
        'verbose': True
    }
]

# Para cada dispositivo, conectar e enviar comandos
for device in devices:
    try:
        with ConnectHandler(**device) as net_connect:
            # Definindo tempo de leitura mais longo
            net_connect.read_timeout = 20

            # Capturando o prompt e escapando caracteres especiais
            prompt = net_connect.find_prompt()
            escaped_prompt = re.escape(prompt)

            # Enviando comandos e capturando saída
            port_1g = net_connect.send_command('show port description | match FREE | match 1G | count', expect_string=escaped_prompt)
            port_10g = net_connect.send_command('show port description | match FREE | match 10G | count', expect_string=escaped_prompt)
            port_100g = net_connect.send_command('show port description | match FREE | match 100G | count', expect_string=escaped_prompt)
            
            data.append({
                'Host': device['host'],
                'Portas de 1GB': port_1g,
                'Portas de 10GB': port_10g,
                'Portas de 100GB': port_100g
            })

            # Imprimindo resultados
            print(f'Portas de 1G do dispositivo {device["host"]}: {port_1g.strip()}')
            print(f'Portas de 10G do dispositivo {device["host"]}: {port_10g.strip()}')
            print(f'Portas de 100G do dispositivo {device["host"]}: {port_100g.strip()}')
    except ReadTimeout:
        print(f'Timeout ao tentar executar comandos no dispositivo {device["host"]}')
    except Exception as e:
        print(f'Erro ao conectar ou enviar comandos ao dispositivo {device["host"]}: {str(e)}')

# Criando um DataFrame com os dados
df = pd.DataFrame(data)

# Exportando para um arquivo Excel
df.to_excel('resultados.xlsx', index=False)

print('Resultados exportados para resultados.xlsx')