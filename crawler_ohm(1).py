from json import loads
from time import sleep
from urllib3 import PoolManager
import os
import pandas as pd;
import psutil as psutil;
import mysql.connector
import mysql.connector.errorcode
import csv

conexao = mysql.connector.connect(
        host = "localhost",
        user = "crawlerOHM",
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
    response = pool.request('GET', 'http://localhost:9000/data.json')
    data = loads(response.data.decode('utf-8'))
    core_count = psutil.cpu_count(logical=False)
    thread_count =psutil.cpu_count(logical=True)
    while True:
        name_desktop = data['Children'][0]['Text']
        name_mainboard = data['Children'][0]['Children'][0]['Text']
        name_cpu = data['Children'][0]['Children'][1]['Text']

        dataset_cpu= {
        }

        dataset_cpuDois= {
        }        

        vars_core_speed = {}
        for i in range(core_count + 1):
            if(i == 0) :
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
            'Min' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][3]['Min'])} W",
            'Atual' : f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][3]['Value'])} W",
            'Max': f"{conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][3]['Max'])} W"
        }
        comando.execute(f"INSERT INTO Potencia VALUES(null, 'cpuDram', {conversorPercent(data['Children'][0]['Children'][1]['Children'][3]['Children'][3]['Value'])})")
        
        file = open('C:/Users/mined/OneDrive/Documentos/crawler/dados-crawler.csv', mode='a', newline='')
        writer = csv.writer(file)
        if os.path.exists("C:/Users/mined/OneDrive/Documentos/crawler/dados-crawler.csv"):
            with open("C:/Users/mined/OneDrive/Documentos/crawler/dados-crawler.csv", 'r') as f:
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

    