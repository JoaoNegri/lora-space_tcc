
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# import scienceplots
# import matplotlib as mpl

# mpl.rcParams.update(mpl.rcParamsDefault)


# plt.style.use('ieee')


folders = os.listdir('../aaaa')

dfs =[]

# cada tipo de simulador
for folder in folders:

    iteracao = os.listdir('../aaaa/'+folder)
    node = []
    percentual = []
    i=0
    df = pd.DataFrame
    # cada parametro de simulaçao
    for it in iteracao:
        files = os.listdir('../aaaa/'+folder+'/'+it)
        #cada simulação
        for file in files:
            sim = pd.read_csv('../aaaa/'+folder+'/'+it+'/'+file, names=['timestamp','id','dist','elev','SF','status'])

            node.append(int(file.split('_')[1]))

            processed = len(sim[sim['status']=='PE']) # mensagens recebidas com sucesso
            num_packet = len(sim['status']) # Total de transmissão
            # print(sim)
            percentual.append(processed/num_packet)
            # if ('1568' in file and '3000' in file )| ('1627' in file and '3000' in file ):
            #     print(f'file = {file}')
            #     print('processed = ',processed)
            #     print('num_packet = ',num_packet)
            #     print(f'prob = {processed/num_packet}')

        if df.empty:
            data = {'num_nodes'+folder+'0' : node, 'percentual'+folder+'0' : percentual}
            df = pd.DataFrame(data)
            df = df.sort_values('num_nodes'+folder+'0')
            df.reset_index(inplace=True,drop=True)
        else:
            data = {'num_nodes'+folder+str(i) : node, 'percentual'+folder+str(i) : percentual}
            
            df2 = pd.DataFrame(data)
            # print(df2)
            df2 = df2.sort_values('num_nodes'+folder+str(i))            
            # print(df2)
            df2.reset_index(inplace=True,drop=True)
            df['num_nodes'+folder+str(i)] = df2['num_nodes'+folder+str(i)]
            df['percentual'+folder+str(i)] = df2['percentual'+folder+str(i)]
            
        node = []
        percentual = []
        i+=1
    dfs.append(df) # cada df contém todas as 30 simulações de um simulador

for item in dfs:
    colunas_percentual = [coluna for coluna in item.columns if 'percentual' in coluna]
    colunas_num_nodes = [coluna for coluna in item.columns if 'num_nodes' in coluna]

    desvio_padrao_por_linha = item[colunas_percentual].std(axis=1) #axis 1 pq faz o desvio padrão da linha que contém todas as simulações no mesmo simulador com o mesmo número de end devices
    media = item[colunas_percentual].mean(axis=1)
    
    print(desvio_padrao_por_linha)
    print(item.head())
    try:

        print(item[item['num_nodesLB0'] == 3000])
    except:
        pass


    soma = 2.45*(desvio_padrao_por_linha/np.sqrt(30)) #intervalo de confiança


    if 'percentualLB0'  in item.columns:
        label = 'lora conservative'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)

    elif 'percentualLR0' in item.columns:
        label = 'lora random'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)

    elif 'percentualLT0'  in item.columns:
        label = 'lora trajectory'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)


    elif 'percentualLTb0'  in item.columns:
        label = 'Trajectory skip'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
    elif 'percentualLTbr0'  in item.columns:
        label = 'lora trajectory random skip'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)

    elif 'percentualLTr0'  in item.columns:
        label = 'lora trajectory random'
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)

    

plt.legend()
plt.yticks([1,0.6,0.4,0.3,0.2])
plt.ylim(0.17,1)
plt.xlim(0,3e3)
plt.yscale("log")
plt.grid(True,axis='both')
plt.show()
