
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# import scienceplots
# import matplotlib as mpl

# mpl.rcParams.update(mpl.rcParamsDefault)


# plt.style.use('science')


folders = os.listdir('../../resultados/simulacao_completa_lt_pra_plot_inicial')

dfs =[]

# cada tipo de simulador
for folder in folders:

    iteracao = os.listdir('../../resultados/simulacao_completa_lt_pra_plot_inicial/'+folder)
    node = []
    percentual = []

    processed = []
    num_packet = []
    not_processed = []
    lost = []
    collided = []

    i=0
    df = pd.DataFrame
    # cada parametro de simulaçao
    for it in iteracao:
        files = os.listdir('../../resultados/simulacao_completa_lt_pra_plot_inicial/'+folder+'/'+it)
        #cada simulação
        for file in files:
            sim = pd.read_csv('../../resultados/simulacao_completa_lt_pra_plot_inicial/'+folder+'/'+it+'/'+file, names=['timestamp','id','dist','elev','SF','status'])

            node.append(int(file.split('_')[1]))

            processed_inst = len(sim[sim['status']=='PE']) 
            num_packet_inst = len(sim['status']) 
            not_processed_inst = len(sim[sim['status']=='NP']) 
            lost_inst = len(sim[sim['status']=='PL']) 
            collided_inst = len(sim[sim['status']=='PC']) 

            percentual.append(processed_inst/num_packet_inst)

            processed.append(processed_inst)
            num_packet.append(num_packet_inst)
            not_processed.append(not_processed_inst)
            lost.append(lost_inst)
            collided.append(collided_inst)


            # print(len(percentual))

            # print(len(processed))
            # print(len(num_packet))
            # print(len(not_processed))
            # print(len(lost))
            # print(len(collided))
        if df.empty:
            data = {'num_nodes'+folder+'0' : node, 'percentual'+folder+'0' : percentual, 'processed'+folder+'0' : processed, 'num_packet'+folder+'0' : num_packet, 'not_processed'+folder+'0' : not_processed, 'lost'+folder+'0' : lost, 'collided'+folder+'0' : collided}
            df = pd.DataFrame(data)
            df = df.sort_values('num_nodes'+folder+'0')
            df.reset_index(inplace=True,drop=True)
        else:
            data = {'num_nodes'+folder+str(i) : node, 'percentual'+folder+str(i) : percentual, 'processed'+folder+str(i) : processed, 'num_packet'+folder+str(i) : num_packet, 'not_processed'+folder+str(i) : not_processed, 'lost'+folder+str(i) : lost, 'collided'+folder+str(i) : collided}

            df2 = pd.DataFrame(data)
            print(df2)
            df2 = df2.sort_values('num_nodes'+folder+str(i))            
            print(df2)
            df2.reset_index(inplace=True,drop=True)
            df['num_nodes'+folder+str(i)] = df2['num_nodes'+folder+str(i)]
            df['percentual'+folder+str(i)] = df2['percentual'+folder+str(i)]
            
        processed = []
        num_packet = []
        not_processed = []
        lost = []
        collided = []

        node = []
        percentual = []
        i+=1
    dfs.append(df) # cada df contém todas as 30 simulações de um simulador

for item in dfs:
    colunas_percentual = [coluna for coluna in item.columns if 'percentual' in coluna]
    colunas_num_nodes = [coluna for coluna in item.columns if 'num_nodes' in coluna]

    colunas_processed = [coluna for coluna in item.columns if 'processed' in coluna]
    colunas_num_packet = [coluna for coluna in item.columns if 'num_packet' in coluna]
    colunas_not_processed = [coluna for coluna in item.columns if 'not_processed' in coluna]
    colunas_lost = [coluna for coluna in item.columns if 'lost' in coluna]
    colunas_collided = [coluna for coluna in item.columns if 'collided' in coluna]



    desvio_padrao_por_linha = item[colunas_percentual].std(axis=1) #axis 1 pq faz o desvio padrão da linha que contém todas as simulações no mesmo simulador com o mesmo número de end devices
    media = item[colunas_percentual].mean(axis=1)
    

    media_processed = item[colunas_processed].mean(axis=1)
    media_num_packet = item[colunas_num_packet].mean(axis=1)
    media_not_processed = item[colunas_not_processed].mean(axis=1)
    media_lost = item[colunas_lost].mean(axis=1)
    media_collided = item[colunas_collided].mean(axis=1)


    print(desvio_padrao_por_linha)
    print(item.head())
    try:

        print(item[item['num_nodesLB0'] == 3000])
    except:
        pass


    soma = 1.97*(desvio_padrao_por_linha/np.sqrt(30)) #intervalo de confiança


    if 'percentualLB12'  in item.columns:
        label = 'lora conservative'
        # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(627)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)


    elif 'percentualLR12' in item.columns:
        label = 'lora random'
      # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(628)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)

    elif 'percentualLT12'  in item.columns:
        label = 'lora trajectory'
      # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(629)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)

    elif 'percentualLTr12'  in item.columns:
        label = 'lora trajectory random'
      # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(6,2,10)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)

    elif 'percentualLTb12'  in item.columns:
        label = 'Trajectory skip'
      # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(6,2,11)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)

    elif 'percentualLTbr12'  in item.columns:
        label = 'lora trajectory random skip'
      # plt.subplot(211)
        plt.plot(item[colunas_num_nodes[0]],media, label=label)
        plt.fill_between(item[colunas_num_nodes[0]], media-soma, media+soma, alpha=0.3)
        # plt.subplot(6,2,12)
        # plt.title(label)
        # plt.plot(item[colunas_num_nodes[0]],media_num_packet, c='grey', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_collided, c='r', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_lost, c='b', ls='--')
        # plt.plot(item[colunas_num_nodes[0]],media_processed, c='orange')
        # plt.fill_between(item[colunas_num_nodes[0]],media_processed,0, color='orange', alpha=0.3)
        # plt.ylim(0, 3000)
    
    
# plt.subplot(211)
plt.title('Probabilidade de entrega de pacotes', fontsize=24)
plt.xlabel('Número de end devices', fontsize=22)
plt.ylabel('Probabilidade de recepção', fontsize=22)
plt.xticks(fontsize=20)
plt.legend(fontsize=20)

# plt.yticks()
plt.ylim(0.17,1)
plt.xlim(0,3e3)
plt.yscale("log")
yticks = [1, 0.6, 0.4, 0.3, 0.2]
plt.yticks(yticks, [str(y) for y in yticks], fontsize=20)
plt.grid(True,axis='both')
plt.subplots_adjust(hspace=0.5)
plt.show()
