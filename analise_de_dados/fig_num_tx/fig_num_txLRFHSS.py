import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

path ='../../resultados/teste_lrfhss/'

folders = os.listdir(path)

###-----Criação do DataFrame com os dados de todas as simulações------
#
#
# Os dados são organizados pelo prefixo (nome da simulação mae), satélite (1 ou 2 ou 3) e numero de nodos (5, 10, 50 ...)
#
#

df_list = []

for folder in folders:
    prefix = folder.split('sat')[0]
    files = os.listdir(os.path.join(path, folder))     

    for file in files:

        sim = pd.read_csv(os.path.join(path, folder, file), names=['timestamp','id','dist','elev','SF', 'num','status','a','b','c','d'])
        sim = sim[sim['timestamp'] <= 900]

        temp_df = pd.DataFrame({
            'id': sim['num'],
            'node': sim['id'],
            'processed': sim['status'],
            'prefix': prefix,
            'sat': file.split('/')[-1].split('SAT')[-1].split('.csv')[0],
            'num_nodes': file.split('/')[-1].split('3CH')[0].split('eb_')[1][:-1]
        })
        
        
        if int(temp_df['num_nodes'][0]) > 5000 and int(folder.split('_')[3].split('p')[1]) >= 8 :
            df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

# print(df.head(5))

# print(df[df['num_nodes'] == '5'].head(20))
###----- Análise para cada prefixo (analise entre as 3 smulações de um mesmo prefixo)

# o que eu quero analisar? 
# aqui quero fazer duas imagens:

# média para cada satélite
# média geral da simulação (sat1, sat2 e sat3)

# Com isso tenho uma "validação" de funcionamento do meu simulador
# Depois eu preciso mostrar que o meu simulador tem um comportamento parecido com esse


# print(df['prefix'].unique())

# [(prefixo, sat?, num_nodes, percentual), ...] <- lista dessa tupla no for

sim_results_individual = []
sim_results_completo = []

# relacao de algum jeito, tipo -> [(node, id, boolean)] ou df colunas node, id, satn, boolean
transmitidos = []
for prefix in df['prefix'].unique():
    #em cada simulação eu vou querer o percentual em relação ao número de satélites por satélite
    #o total da simulacao sat1 + sat2 +sat3
    
    df_filtrado_prefixo = df[df['prefix'] == prefix]

    for num_nodes in df_filtrado_prefixo['num_nodes'].unique():
        
        df_simulacao = df_filtrado_prefixo[df_filtrado_prefixo['num_nodes'] == num_nodes]
        sim_results_completo_aux = 0

        sim_results_completo_aux = pd.DataFrame(columns=['node','id','sat','recieved'])



        transmitidos.append((int(num_nodes),len(df_simulacao['id'])/int(num_nodes)/3))
# Dicionário para armazenar listas de amostras para cada item do eixo X
samples = {}

# Organizando as amostras no dicionário
for x, y in transmitidos:
    if x not in samples:
        samples[x] = []
    samples[x].append(y)

# Calculando as médias
x_values = sorted(samples.keys())  # Ordenando os valores do eixo X
y_means = [sum(samples[x])/len(samples[x]) for x in x_values]  # Média para cada item do eixo X

# Convertendo os valores de x_values para strings
x_labels = [str(x) for x in x_values]

# Verificação de dados
# for x in x_values:
    # print(f"Num Nodes: {x}, Amostras: {samples[x]}, Média: {sum(samples[x])/len(samples[x])}")

# Definindo a largura das barras
bar_width = 0.5  # Largura das barras
b = y_means
a = x_labels
# Criando o gráfico de barras
plt.bar(x_labels, y_means, width=bar_width, label='Pacotes enviados na constelação de 3 satélites')
print(y_means)
print('---------')
# Adicionando título e rótulos dos eixos
plt.title('Número de pacotes transmitidos por Número de end devices em rede LR-FHSS', fontsize=16)
plt.xlabel('Número de Nós', fontsize=14)
plt.ylabel('Média de Pacotes Transmitidos', fontsize=14)


# plt.yscale("log")

# Mostrando o gráfico


import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

path ='../../resultados/teste_lrfhss_original/'

folders = os.listdir(path)

###-----Criação do DataFrame com os dados de todas as simulações------
#
#
# Os dados são organizados pelo prefixo (nome da simulação mae), satélite (1 ou 2 ou 3) e numero de nodos (5, 10, 50 ...)
#
#

df_list = []

for folder in folders:
    prefix = folder.split('sat')[0]
    files = os.listdir(os.path.join(path, folder))     
    for file in files:
        
        sim = pd.read_csv(os.path.join(path, folder, file), names=['timestamp','id','dist','elev','SF', 'num','status','a','b','c','d'])
        sim = sim[sim['timestamp'] <= 900]

        temp_df = pd.DataFrame({
            'node': sim['id'],
            'id': sim['num'],
            'processed': sim['status'],
            'prefix': prefix,
            'num_nodes': file.split('/')[-1].split('3CH')[0].split('EB2_')[1][:-1]
        })
        if int(temp_df['num_nodes'][0]) > 5000 and int(folder.split('_')[3].split('p')[1])  >= 8:
            df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

# print(df.head(5))

# print(df[df['num_nodes'] == '5'].head(20))
###----- Análise para cada prefixo (analise entre as 3 smulações de um mesmo prefixo)

# o que eu quero analisar? 
# aqui quero fazer duas imagens:

# média para cada satélite
# média geral da simulação (sat1, sat2 e sat3)

# Com isso tenho uma "validação" de funcionamento do meu simulador
# Depois eu preciso mostrar que o meu simulador tem um comportamento parecido com esse


# print(df['prefix'].unique())

# [(prefixo, sat?, num_nodes, percentual), ...] <- lista dessa tupla no for

sim_results_individual = []
sim_results_completo = []

# relacao de algum jeito, tipo -> [(node, id, boolean)] ou df colunas node, id, satn, boolean
transmitidos = []
for prefix in df['prefix'].unique():
    #em cada simulação eu vou querer o percentual em relação ao número de satélites por satélite
    #o total da simulacao sat1 + sat2 +sat3
    
    df_filtrado_prefixo = df[df['prefix'] == prefix]

    for num_nodes in df_filtrado_prefixo['num_nodes'].unique():
        
        df_simulacao = df_filtrado_prefixo[df_filtrado_prefixo['num_nodes'] == num_nodes]
        sim_results_completo_aux = 0

        sim_results_completo_aux = pd.DataFrame(columns=['node','id','sat','recieved'])



        transmitidos.append((int(num_nodes),len(df_simulacao['id'])/int(num_nodes)))
# Dicionário para armazenar listas de amostras para cada item do eixo X
samples = {}

# Organizando as amostras no dicionário
for x, y in transmitidos:
    if x not in samples:
        samples[x] = []
    samples[x].append(y)

# Calculando as médias
x_values = sorted(samples.keys())  # Ordenando os valores do eixo X
y_means = [sum(samples[x])/len(samples[x]) for x in x_values]  # Média para cada item do eixo X

# Convertendo os valores de x_values para strings
x_labels = [str(x) for x in x_values]

# Verificação de dados
# for x in x_values:
#     print(f"Num Nodes: {x}, Amostras: {samples[x]}, Média: {sum(samples[x])/len(samples[x])}")

# Definindo a largura das barras
bar_width = 0.5  # Largura das barras

# Criando o gráfico de barras
plt.bar(x_labels, y_means, width=bar_width, label='Pacotes enviados na constelação de 1 satélite')
# plt.bar(a, b, width=bar_width, label='Pacotes enviados na constelação de 33333 satélite')

# Adicionando título e rótulos dos eixos
plt.title('Número de pacotes transmitidos por Número de end devices em rede LR-FHSS', fontsize=16)
plt.xlabel('Número de Nós', fontsize=14)
plt.ylabel('Média de Pacotes Transmitidos', fontsize=14)
plt.grid()
plt.legend(fontsize=14)
print(y_means)
print('---------')
# plt.yscale("log")

# Mostrando o gráfico
plt.show()