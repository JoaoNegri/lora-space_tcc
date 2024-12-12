import pandas as pd
import matplotlib.pyplot as plt
import os

path = '../../resultados/simulacao_completa_lt_pra_plot_inicial'

tipos_simulacao = os.listdir('../../resultados/simulacao_completa_lt_pra_plot_inicial')
j = 0
for tipo_simulacao in tipos_simulacao: #lb, lt...
    iteracoes = os.listdir(path+'/'+tipo_simulacao)
    df = pd.DataFrame({'7': [0],
                        '8': [0],
                        '9': [0],
                        '10': [0],
                        '11': [0],
                        '12': [0]})     
    
    for iteracao in iteracoes:#lr_3ch...
        sim =  os.listdir(path+'/'+tipo_simulacao+'/'+iteracao)[0]
        df2 = pd.read_csv(path+'/'+tipo_simulacao+'/'+iteracao+'/'+sim,names=['timestamp','id','dist','elev','SF','status', 'pckt2snd'])
        for i in range(7, 13):
            df[str(i)] += len(df2[df2['SF'] == i])
        

    df = df.T


    if 'LB'  == tipo_simulacao:
        label = 'Lora conservative'


    elif 'LR' == tipo_simulacao:
        label = 'Lora random'


    elif 'LT' == tipo_simulacao:
        label = 'Lora trajectory'


    elif 'LTr' == tipo_simulacao:
        label = 'Lora trajectory random'


    elif 'LTb' == tipo_simulacao:
        label = 'Trajectory skip'


    elif 'LTbr' == tipo_simulacao:
        label = 'Lora trajectory random skip'

    
    colors = {7: 'navy', 8: 'blue', 9: 'lightblue', 10: 'lightsalmon', 11: 'red', 12: 'darkred'}   
    df2 = df

    #df2.iloc[SF-7]/nº de pacotes transmitidos * TOA* 3 pacotes
    df2.iloc[0] = df2.iloc[0]/540000 * 0.0566*3
    df2.iloc[1] = df2.iloc[1]/540000 * 0.1029*3
    df2.iloc[2] = df2.iloc[2]/540000 * 0.1853*3
    df2.iloc[3] = df2.iloc[3]/540000 * 0.3707*3
    df2.iloc[4] = df2.iloc[4]/540000 * 0.7414*3
    df2.iloc[5] = df2.iloc[5]/540000 * 1.3189*3


    if j ==0:
        plt.bar(label, df[0].iloc[0], label='SF 7', color=colors[7])#, c=a.values)
        plt.bar(label, df[0].iloc[1], label='SF 8',bottom=df[0].iloc[0], color=colors[8])#, c=a.values)
        plt.bar(label, df[0].iloc[2], label='SF 9',bottom=df[0].iloc[0]+df[0].iloc[1], color=colors[9])#, c=a.values)
        plt.bar(label, df[0].iloc[3], label='SF 10',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2], color=colors[10])#, c=a.values)
        plt.bar(label, df[0].iloc[4], label='SF 11',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3], color=colors[11])#, c=a.values)
        plt.bar(label, df[0].iloc[5], label='SF 12',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3]+df[0].iloc[4], color=colors[12])#, c=a.values)
    else:
        plt.bar(label, df[0].iloc[0], color=colors[7])#, c=a.values)
        plt.bar(label, df[0].iloc[1],bottom=df[0].iloc[0], color=colors[8])#, c=a.values)
        plt.bar(label, df[0].iloc[2],bottom=df[0].iloc[0]+df[0].iloc[1], color=colors[9])#, c=a.values)
        plt.bar(label, df[0].iloc[3],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2], color=colors[10])#, c=a.values)
        plt.bar(label, df[0].iloc[4],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3], color=colors[11])#, c=a.values)
        plt.bar(label, df[0].iloc[5],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3]+df[0].iloc[4], color=colors[12])#, c=a.values)
    j+= 1
plt.title('Tempo médio de transmissão', fontsize=24)
plt.xlabel('Política de transmissão',fontsize=22)
plt.ylabel('Tempo de transmissão (s)',fontsize=22)
plt.legend(fontsize=20)
plt.xticks(fontsize=20, rotation=-11)
plt.yticks(fontsize=20)
plt.show()

