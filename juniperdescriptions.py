import paramiko
import time


def juniper_descriptions():
    switch_ip = "170.238.232.207"
    username = "frederico.oliveira"
    password = "239507/Astr23"
    ssh_port = 22

    # Lista de prefixos de interfaces que não devem ter suas descrições alteradas
    exclude_interfaces = [
        ".32768", ".32767", ".16386", "pimd", "mtun", "pime", "fxp", 
        "cbp0", "demux0", "dsc  ", "em0", "em1", "esi", "irb", "ae", "gre"
    ]
    
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(switch_ip, port=ssh_port, username=username, password=password, timeout=10)
        print('Conectou com Sucesso no Roteador!')

        remote_shell = ssh_client.invoke_shell()
        time.sleep(1)  # Pequena espera para garantir que o shell está pronto

        # Enviar comando para obter interfaces em estado "down"
        remote_shell.send('show interfaces terse | match "down *down"\n')
        time.sleep(2)  # Espera para garantir que o comando tenha tempo de ser executado

        # Receber a saída do comando
        output = remote_shell.recv(65535).decode('utf-8')
        print(output)

        # Processar a saída
        lines = output.strip().split('\n')
        down_interfaces = []
        for line in lines:
            parts = line.split()
            if len(parts) > 0:
                interface = parts[0]
                down_interfaces.append(interface)

        print(f"Interfaces with down state: {down_interfaces}")

        # Entrar no modo de configuração e fazer alterações
        remote_shell.send('configure\n')
        time.sleep(1)  # Espera para entrar no modo de configuração

        for interface in down_interfaces:
            # Verificar se a interface começa com qualquer um dos prefixos na lista de exclusão
            if not any(interface.startswith(exclude) for exclude in exclude_interfaces):
                set_command = f'set interfaces {interface} description "FREE-PORT"\n'
                remote_shell.send(set_command)
                time.sleep(1)  # Pequena espera após cada comando

        # Commit and exit configuration mode
        remote_shell.send('commit\n')
        time.sleep(2)  # Espera para commit
        remote_shell.send('exit\n')
        time.sleep(1)  # Espera para sair do modo de configuração

        # Fechar a sessão SSH
        ssh_client.close()
        print("Conexão fechada.")
        
    except paramiko.AuthenticationException:
        print("Autenticação falhou, verifique as credenciais.")
    except paramiko.SSHException as ssh_exc:
        print("Conexão SSH falhou.")
    except Exception as exc:
        print(f"Ocorreu um erro: {exc}")

juniper_descriptions()
