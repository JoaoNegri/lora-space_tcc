import pandas as pd
import matplotlib.pyplot as plt
import os

path = '../resultados_simulacao_30_random_3_pacotes'

tipos_simulacao = os.listdir('../resultados_simulacao_30_random_3_pacotes')

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
           
        df2 = pd.read_csv(path+'/'+tipo_simulacao+'/'+iteracao+'/'+sim,names=['timestamp','id','dist','elev','SF','status'])
        for i in range(7, 13):
            df[str(i)] += len(df2[df2['SF'] == i])
        

    df = df.T


    if 'LB'  == tipo_simulacao:
        label = 'lora conservative'


    elif 'LR' == tipo_simulacao:
        label = 'lora random'


    elif 'LT' == tipo_simulacao:
        label = 'lora trajectory'


    elif 'LTr' == tipo_simulacao:
        label = 'lora trajectory random'


    elif 'LTb' == tipo_simulacao:
        label = 'Trajectory skip'


    elif 'LTbr' == tipo_simulacao:
        label = 'lora trajectory random skip'

    
    colors = {7: 'navy', 8: 'blue', 9: 'lightblue', 10: 'lightsalmon', 11: 'red', 12: 'darkred'}   
    df2 = df

    df2.iloc[0] = df2.iloc[0]/540000 * 0.0566*3
    df2.iloc[1] = df2.iloc[1]/540000 * 0.1029*3
    df2.iloc[2] = df2.iloc[2]/540000 * 0.1853*3
    df2.iloc[3] = df2.iloc[3]/540000 * 0.3707*3
    df2.iloc[4] = df2.iloc[4]/540000 * 0.7414*3
    df2.iloc[5] = df2.iloc[5]/540000 * 1.3189*3


    if j ==0:
        plt.bar(label, df[0].iloc[0], label='7', color=colors[7])#, c=a.values)
        plt.bar(label, df[0].iloc[1], label='8',bottom=df[0].iloc[0], color=colors[8])#, c=a.values)
        plt.bar(label, df[0].iloc[2], label='9',bottom=df[0].iloc[0]+df[0].iloc[1], color=colors[9])#, c=a.values)
        plt.bar(label, df[0].iloc[3], label='10',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2], color=colors[10])#, c=a.values)
        plt.bar(label, df[0].iloc[4], label='11',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3], color=colors[11])#, c=a.values)
        plt.bar(label, df[0].iloc[5], label='12',bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3]+df[0].iloc[4], color=colors[12])#, c=a.values)
    else:
        plt.bar(label, df[0].iloc[0], color=colors[7])#, c=a.values)
        plt.bar(label, df[0].iloc[1],bottom=df[0].iloc[0], color=colors[8])#, c=a.values)
        plt.bar(label, df[0].iloc[2],bottom=df[0].iloc[0]+df[0].iloc[1], color=colors[9])#, c=a.values)
        plt.bar(label, df[0].iloc[3],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2], color=colors[10])#, c=a.values)
        plt.bar(label, df[0].iloc[4],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3], color=colors[11])#, c=a.values)
        plt.bar(label, df[0].iloc[5],bottom=df[0].iloc[0]+df[0].iloc[1]+df[0].iloc[2]+df[0].iloc[3]+df[0].iloc[4], color=colors[12])#, c=a.values)
    j+= 1
plt.legend()
plt.show()