from json import loads
from time import sleep
from urllib3 import PoolManager
import os
import platform as plat
import pandas as pd;
import psutil as psutil;
import mysql.connector
import mysql.connector.errorcode
import csv
import requests
import gzip
import unicodedata
import time

def remover_acentos(text):
    return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))

def get_and_process_data(url, output_csv_filename):
    while True:
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            data = resposta.json()
            if data and "data" in data[0] and "weather" in data[0]["data"][0]:
                weather_info = data[0]["data"][0]["weather"][0]
                cidade = remover_acentos(data[0]["data"][0]["locale"]["name"])   # Remove acentos
                temperatura = weather_info.get('temperature', 'N/A')
                umidade = weather_info.get('humidity', 'N/A')
                pressao = weather_info.get('pressure', 'N/A')
                data_hora_json = weather_info.get('date', 'N/A')

                # Separar a data e a hora do campo 'date' do JSON
                data_json, hora_json = data_hora_json.split()

                # Escrever os dados em um arquivo CSV
                with open(output_csv_filename, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    headers = ['Data', 'Hora', 'Cidade', 'Temperatura', 'Umidade', 'Pressao']
                    csv_writer.writerow(headers)
                    csv_writer.writerow([data_json, hora_json, cidade, temperatura, umidade, pressao])

                    sql = "insert into clima (dataJson, horaJson, cidade, temperatura, umidade, pressao) values (%s, %s, %s, %s, %s, %s)"
                    dados = ([data_json, hora_json, cidade, temperatura, umidade, pressao])
                    #cursor.execute(sql,dados)
                    #mydb.commit()

                print(f'Dados salvos em {output_csv_filename}')
            else:
                print("Os dados necessários estão ausentes no JSON.")
        else:
            print("Falha ao obter os dados do JSON da página da web.")

        # Defina o intervalo de tempo (em segundos) entre as solicitações
        intervalo = 3600  
        time.sleep(intervalo)

# URL da página da web a ser rastreada
url = "https://www.climatempo.com.br/json/myclimatempo/user/weatherNow?idlocale=3477"

# Nome do arquivo CSV de saída
output_csv_filename = "dados_climatempo.csv"

# Chamada da função para obter e processar os dados em um loop




def dados_ambiente():
    
    
    
    
    resposta_usuario = input("Deseja voltar? y/n")
    if resposta_usuario == "y":
        painel_principal()
    else:
        print("Programa encerrado!")


#    url = "https://www.climatempo.com.br/json/myclimatempo/user/weatherNow?idlocale=3477"

#   def remover_acentos(text):
#      return "".join((c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c) != "Mn"))







def dados_ohm():

    conexao = mysql.connector.connect(
            host = "localhost",
            user = "urubu100",
            password = "urubu100",
            port = 3306,
            database = "dadosCrawler"
            )

    comando = conexao.cursor()

    comando.execute("CREATE DATABASE IF NOT EXISTS dadosCrawler;")
    comando.execute("USe dadosCrawler;")
    comando.execute("CREATE TABLE IF NOT EXISTS Speed(idSpeed INT PRIMARY KEY auto_increment,nome VARCHAR(45),valorSpeed DOUBLE);")
    comando.execute("CREATE TABLE IF NOT EXISTS Temperatura(idTemp INT PRIMARY KEY auto_increment,nome VARCHAR(45),valorTemp DOUBLE);	")
    comando.execute("CREATE TABLE IF NOT EXISTS Uso(idUso INT PRIMARY KEY auto_increment,nome VARCHAR(45),valorUso DOUBLE);")
    comando.execute("CREATE TABLE IF NOT EXISTS Potencia(idPotencia INT PRIMARY KEY auto_increment,nome VARCHAR(45),valorPotencia DOUBLE);")

    def conversor(valor):
        return float(valor[0:5].replace(",", '.'))

    def conversorPercent(valor):
        return float(valor[0:4].replace(",", '.'))

    with PoolManager() as pool:
        response = pool.request('GET', 'http://10.18.34.141:9000/data.json') #Configurar o ohm
        data = loads(response.data.decode('utf-8'))
        core_count = psutil.cpu_count(logical=False)
        thread_count =psutil.cpu_count(logical=True)
        while True:
            name_desktop = data['Children'][0]['Text']
            name_mainboard = data['Children'][0]['Children'][0]['Text']
            name_cpu = data['Children'][0]['Children'][1]['Text']

            dataset_cpu= {}

            dataset_cpuDois= {}        

            vars_core_speed = {}
            

            for i in range(core_count + 1):
                if(i == 0) :

                    print((data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Min']))
                    vars_core_speed["dataset_bus_speed"] = {
                        'Min' : f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Min'])} MHz",
                        'Atual' : f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Value'])} MHz",
                        'Max': f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Max'])} MHz"
                    }
                    dataset_cpu["Bus Speed"] = vars_core_speed.get("dataset_bus_speed")
                    comando.execute(f"INSERT INTO Speed VALUES(null, 'busSpeed', {conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Value'])})")
                else:
                    vars_core_speed["dataset_core_speed{0}".format(i)] = {
                        'Min' : f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Min'])} MHz",
                        'Atual' : f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Value'])} MHz",
                        'Max': f"{conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Max'])} MHz"
                    }
                    dataset_cpu["Core {0} Speed".format(i)] = vars_core_speed.get(f"dataset_core_speed{i}")
                    comando.execute(f"INSERT INTO Speed VALUES(null, 'core{i}', {conversor(data['Children'][0]['Children'][1]['Children'][0]['Children'][i]['Value'])})")


            vars_core_temp = {}
            for i in range(core_count + 1):
                if(i - core_count  == 0) :
                    vars_core_temp["dataset_cpu_package"] = {
                        'Min' : f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Min'])} °C",
                        'Atual' : f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Value'])} °C",
                        'Max': f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Max'])} °C"
                    }
                    dataset_cpu["Cpu Package"] = vars_core_temp.get("dataset_cpu_package")
                    comando.execute(f"INSERT INTO Temperatura VALUES(null, 'cpuPackage', {conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Value'])})")
                    
                else:
                    vars_core_temp["dataset_core_temp{0}".format(i + 1)] = {
                        'Min' : f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Min'])} °C",
                        'Atual' : f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Value'])} °C",
                        'Max': f"{conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Max'])} °C"
                    }
                    dataset_cpu["Core {0} Temp".format(i + 1)] = vars_core_temp.get(f"dataset_core_temp{i + 1}")
                    comando.execute(f"INSERT INTO Temperatura VALUES(null, 'core{i + 1}', {conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Value'])})")

            vars_core_util = {}
            for i in range(core_count + 1):
                if(i == 0) :
                    vars_core_util["dataset_cpu_total"] = {
                        'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Min'])} %",
                        'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Value'])} %",
                        'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Max'])} %"
                    }
                    dataset_cpuDois["Cpu Total"] = vars_core_util.get("dataset_cpu_total")
                    comando.execute(f"INSERT INTO Uso VALUES(null, 'cpuTotal', {conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Value'])})")
                else:
                    vars_core_util["dataset_core_util{0}".format(i)] = {
                        'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Min'])} %",
                        'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Value'])} %",
                        'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Max'])} %"
                    }
                    dataset_cpuDois["Core {0} Utilização".format(i)] = vars_core_util.get(f"dataset_core_util{i}")
                    comando.execute(f"INSERT INTO Uso VALUES(null, 'core{i}', {conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Value'])})")

            dataset_cpuDois["CPU Package"] = {
                'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][0]['Min'])} W",
                'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][0]['Value'])} W",
                'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][0]['Max'])} W"
            }
            comando.execute(f"INSERT INTO Potencia VALUES(null, 'cpuPackage', {conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][0]['Value'])})")
            
            dataset_cpuDois["CPU Cores"] = {
                'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][1]['Min'])} W",
                'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][1]['Value'])} W",
                'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][1]['Max'])} W"
            }
            comando.execute(f"INSERT INTO Potencia VALUES(null, 'cpuCores', {conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][1]['Value'])})")
            dataset_cpuDois["CPU Graphics"] = {
                'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Min'])} W",
                'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Value'])} W",
                'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Max'])} W"
            }
            comando.execute(f"INSERT INTO Potencia VALUES(null, 'cpuGraphics', {conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Value'])})")
            dataset_cpuDois["CPU DRAM"] = { 
                'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Min'])} W", # Mudei o final de 3 para 2
                'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Value'])} W",
                'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Max'])} W"
            }
            comando.execute(f"INSERT INTO Potencia VALUES(null, 'cpuDram', {conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][2]['Value'])})")
            
            file = open('C:/Users/Gabriel B/Documents/crawler/dados-crawler.csv', mode='a', newline='')
            writer = csv.writer(file)
            if os.path.exists("C:/Users/Gabriel B/Documents/crawler/dados-crawler.csv"): #mudei o caminho
                with open("C:/Users/Gabriel B/Documents/crawler/dados-crawler.csv", 'r') as f: #mudei o caminho
                    if len(f.readlines()) == 0:
                        writer.writerow(["Temperatura da CPU", "Uso da CPU",])
                    else:
                        writer.writerow([conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][i]['Value']),conversorPercent(data['Children'][0]['Children'][1]['Children'][2]['Children'][i]['Value'])])
            file.close()

            
            
            print(f"""

            Usuário: {name_desktop}
            Placa Mãe: {name_mainboard}
            ____ ____  _   _ 
            / ___ |  _ \| | | |
            | |   | |_) | | | |
            | |___|  __/| |_| |
            \____ |_|    \___/ 

            CPU Atual : {name_cpu}  | Quantidade de Threads: {thread_count} | Quantidade de Cores: {core_count}
    -----------------------------------------------------------------------------------------------------------------------------------------
    {pd.DataFrame(dataset_cpu)}
    -----------------------------------------------------------------------------------------------------------------------------------------
    {pd.DataFrame(dataset_cpuDois)}

            """)
            conexao.commit()
            sleep(1)
            os.system("cls")
            resposta_usuario = input("Deseja voltar? y/n \n")
            if resposta_usuario == "y":
                painel_principal()
            



def painel_principal():
    nome_so = (plat.uname().system)

    
    print(
    """

    ------------------------------------------------------------
    Bem-vindo, qual tipo de informação você gostaria de receber:

    1 - Monitoramento da temperatura do servidor com OHM
    2 - Monitoramento do ambiente do servidor
    """
    )
    
    resposta_usuario = int(input("Digite sua resposta: "))

    if resposta_usuario == 1:
        if nome_so == "Windows":
            dados_ohm()
        else:
            print("O seu sistema operacional não suporta este tipo de monitoramento!\n")
            painel_principal()
            
    elif resposta_usuario == 2:
        get_and_process_data(url, output_csv_filename)
    else: 
        print("\nNúmero inválido!")
        painel_principal()
    
            


painel_principal()

            