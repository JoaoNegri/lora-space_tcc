import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

path ='../../resultados/simulacao_lb_args_v7/'

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
        
        temp_df = pd.DataFrame({
            'id': sim['num'],
            'node': sim['id'],
            'processed': sim['status'],
            'prefix': prefix,
            'sat': file.split('/')[-1].split('sat_')[-1].split('.csv')[0],
            'num_nodes': file.split('/')[-1].split('3CH')[0].split('LB2_')[1][:-1]
        })
        
        df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

print(df.head(5))

print(df[df['num_nodes'] == '5'].head(20))
###----- Análise para cada prefixo (analise entre as 3 smulações de um mesmo prefixo)

# o que eu quero analisar? 
# aqui quero fazer duas imagens:

# média para cada satélite
# média geral da simulação (sat1, sat2 e sat3)

# Com isso tenho uma "validação" de funcionamento do meu simulador
# Depois eu preciso mostrar que o meu simulador tem um comportamento parecido com esse


print(df['prefix'].unique())

# [(prefixo, sat?, num_nodes, percentual), ...] <- lista dessa tupla no for

sim_results_individual = []
sim_results_completo = []

# relacao de algum jeito, tipo -> [(node, id, boolean)] ou df colunas node, id, satn, boolean

for prefix in df['prefix'].unique():
    #em cada simulação eu vou querer o percentual em relação ao número de satélites por satélite
    #o total da simulacao sat1 + sat2 +sat3
    
    df_filtrado_prefixo = df[df['prefix'] == prefix]

    for num_nodes in df_filtrado_prefixo['num_nodes'].unique():
        
        df_simulacao = df_filtrado_prefixo[df_filtrado_prefixo['num_nodes'] == num_nodes]
        sim_results_completo_aux = 0

        sim_results_completo_aux = pd.DataFrame(columns=['node','id','sat','recieved'])

        for satelite in df_simulacao['sat'].unique():

            df_pacotes = df_simulacao[df_simulacao['sat'] == satelite]

            
            temp_data = []

            temp_data = df_pacotes[['node', 'id', 'sat']].copy()
            temp_data['recieved'] = df_pacotes['processed'] == 'PE'

            aux_sim_results_completo = pd.DataFrame(temp_data)
            
            sim_results_completo_aux = pd.concat([sim_results_completo_aux, aux_sim_results_completo], ignore_index=True)


            num_packtes = len(df_pacotes['id'])

            percentual = len(df_pacotes[df_pacotes['processed'] == 'PE'])/ num_packtes


            sim_results_individual.append((prefix, satelite, num_nodes, percentual))

        sim_results_completo_aux.drop(['sat'], axis=1, inplace=True)
        
        grouped = sim_results_completo_aux.groupby(['node', 'id'])['recieved'].any().reset_index()
        grouped.rename(columns={'recieved': 'successful'}, inplace=True)

        successful_packages = grouped['successful'].sum()

        percentual = successful_packages/num_packtes
        sim_results_completo.append((prefix, num_nodes, percentual))




df_plot_individual = pd.DataFrame(sim_results_individual, columns=['prefix', 'sat', 'num_nodes', 'percentage'])
df_plot_completo = pd.DataFrame(sim_results_completo, columns=['prefix', 'num_nodes', 'percentage'])

df_plot_completo = df_plot_completo.astype({
    'prefix': str,
    'num_nodes': int,
    'percentage': float
})
df_plot_individual = df_plot_individual.astype({
    'prefix': str,
    'num_nodes': int,
    'sat': int,
    'percentage': float
})



statistics_completo = df_plot_completo.groupby('num_nodes')['percentage'].agg(['mean', 'std']).reset_index()
statistics_individual = df_plot_individual.groupby(['num_nodes', 'sat'])['percentage'].agg(['mean', 'std']).reset_index()

# Renomear as colunas resultantes
statistics_completo.rename(columns={'mean': 'percentage_mean', 'std': 'percentage_std'}, inplace=True)
statistics_individual.rename(columns={'mean': 'percentage_mean', 'std': 'percentage_std'}, inplace=True)


soma_completo = 2.45*(statistics_completo['percentage_std']/np.sqrt(30))

plt.plot(statistics_completo['num_nodes'], statistics_completo['percentage_mean'], ls='--', label='Simulador original LoRa-Space')
plt.fill_between(statistics_completo['num_nodes'], statistics_completo['percentage_mean'] + soma_completo, statistics_completo['percentage_mean'] - soma_completo, alpha= 0.3)
plt.title('Probabilidade de recepção', fontsize=24)
plt.legend(fontsize=20)
plt.ylim(0.17,1)
plt.xlim(0,1e3)
plt.yscale("log")
plt.grid(True,axis='both')






import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

path ='../../resultados/simulacao_novo_sim_apenas_sat_3/'

folders = os.listdir(path)

###-----Criação do DataFrame com os dados de todas as simulações------
#
#
# Os dados são organizados pelo prefixo (nome da simulação mae), satélite (1 ou 2 ou 3) e numero de nodos (5, 10, 50 ...)
#
#

df_list = []

for folder in folders:
    prefix = folder.split('_NOVO')[0]
    files = os.listdir(os.path.join(path, folder))     

    for file in files:

        sim = pd.read_csv(os.path.join(path, folder, file), names=['timestamp','id','dist','elev','SF','status','a','num','c','d'])
        
        temp_df = pd.DataFrame({
            'id': sim['num'],
            'node': sim['id'],
            'processed': sim['status'],
            'prefix': prefix,
            'sat': file.split('/')[-1].split('sat_')[-1].split('.csv')[0],
            'num_nodes': file.split('/')[-1].split('3CH')[0].split('lb_')[1][:-1]
        })
        
        df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

print(df.head(5))

print(df[df['num_nodes'] == '5'].head(20))
###----- Análise para cada prefixo (analise entre as 3 smulações de um mesmo prefixo)

# o que eu quero analisar? 
# aqui quero fazer duas imagens:

# média para cada satélite
# média geral da simulação (sat1, sat2 e sat3)

# Com isso tenho uma "validação" de funcionamento do meu simulador
# Depois eu preciso mostrar que o meu simulador tem um comportamento parecido com esse


print(df['prefix'].unique())


# [(prefixo, sat?, num_nodes, percentual), ...] <- lista dessa tupla no for

sim_results_individual = []
sim_results_completo = []

# relacao de algum jeito, tipo -> [(node, id, boolean)] ou df colunas node, id, satn, boolean

for prefix in df['prefix'].unique():
    #em cada simulação eu vou querer o percentual em relação ao número de satélites por satélite
    #o total da simulacao sat1 + sat2 +sat3
    
    df_filtrado_prefixo = df[df['prefix'] == prefix]

    for num_nodes in df_filtrado_prefixo['num_nodes'].unique():
        
        df_simulacao = df_filtrado_prefixo[df_filtrado_prefixo['num_nodes'] == num_nodes]
        sim_results_completo_aux = 0

        sim_results_completo_aux = pd.DataFrame(columns=['node','id','sat','recieved'])

        for satelite in df_simulacao['sat'].unique():

            df_pacotes = df_simulacao[df_simulacao['sat'] == satelite]

            
            temp_data = []

            temp_data = df_pacotes[['node', 'id', 'sat']].copy()
            temp_data['recieved'] = df_pacotes['processed'] == 'PE'

            aux_sim_results_completo = pd.DataFrame(temp_data)
            
            sim_results_completo_aux = pd.concat([sim_results_completo_aux, aux_sim_results_completo], ignore_index=True)


            num_packtes = len(df_pacotes['id'])

            percentual = len(df_pacotes[df_pacotes['processed'] == 'PE'])/ num_packtes


            sim_results_individual.append((prefix, satelite, num_nodes, percentual))

        sim_results_completo_aux.drop(['sat'], axis=1, inplace=True)
        
        grouped = sim_results_completo_aux.groupby(['node', 'id'])['recieved'].any().reset_index()
        grouped.rename(columns={'recieved': 'successful'}, inplace=True)

        successful_packages = grouped['successful'].sum()

        percentual = successful_packages/num_packtes
        sim_results_completo.append((prefix, num_nodes, percentual))




df_plot_individual = pd.DataFrame(sim_results_individual, columns=['prefix', 'sat', 'num_nodes', 'percentage'])
df_plot_completo = pd.DataFrame(sim_results_completo, columns=['prefix', 'num_nodes', 'percentage'])

df_plot_completo = df_plot_completo.astype({
    'prefix': str,
    'num_nodes': int,
    'percentage': float
})
df_plot_individual = df_plot_individual.astype({
    'prefix': str,
    'num_nodes': int,
    'sat': int,
    'percentage': float
})



statistics_completo = df_plot_completo.groupby('num_nodes')['percentage'].agg(['mean', 'std']).reset_index()
statistics_individual = df_plot_individual.groupby(['num_nodes', 'sat'])['percentage'].agg(['mean', 'std']).reset_index()

# Renomear as colunas resultantes
statistics_completo.rename(columns={'mean': 'percentage_mean', 'std': 'percentage_std'}, inplace=True)
statistics_individual.rename(columns={'mean': 'percentage_mean', 'std': 'percentage_std'}, inplace=True)


soma_completo = 2.45*(statistics_completo['percentage_std']/np.sqrt(30))


plt.plot(statistics_completo['num_nodes'], statistics_completo['percentage_mean'], ls='--', label='Simulador atualizado')
plt.fill_between(statistics_completo['num_nodes'], statistics_completo['percentage_mean'] + soma_completo, statistics_completo['percentage_mean'] - soma_completo, alpha= 0.3)
plt.title('Probabilidade de recepção', fontsize=24)

plt.ylim(0.17,1)
plt.legend(fontsize=20)
plt.xlim(0,1e3)
plt.yscale("log")
plt.grid(True,axis='both')

yticks = [1, 0.6, 0.4, 0.3, 0.2]
plt.yticks(yticks, [str(y) for y in yticks], fontsize=20)
plt.xticks(fontsize=20)


plt.xlabel('Número de end devices', fontsize=22)
plt.ylabel('Probabilidade de recepção', fontsize=22)


plt.show()

