import pandas as pd
import matplotlib.pyplot as plt
import os

file = '/home/joao/tcc/lora-space/resultados_simulacao_30_random_3_pacotes/LTb/LTb_3CH_s39_p3/LTb_3000_3CH_16_s39_p3.csv'

path = '../resultados_simulacao_30_random_3_pacotes'

tipos_simulacao = os.listdir('../resultados_simulacao_30_random_3_pacotes')
for tipo_simulacao in tipos_simulacao: #lb, lt...
    i = 0
    iteracoes = os.listdir(path+'/'+tipo_simulacao)
    for iteracao in iteracoes:#lr_3ch...
        sim =  os.listdir(path+'/'+tipo_simulacao+'/'+iteracao)[0]

        df = pd.read_csv(path+'/'+tipo_simulacao+'/'+iteracao+'/'+sim,names=['timestamp','id','dist','elev','SF','status'])
            
        if 'LB'  == tipo_simulacao:
            label = 'lora conservative'
            plt.subplot(321)

        elif 'LR' == tipo_simulacao:
            label = 'lora random'
            plt.subplot(322)
        

        elif 'LT' == tipo_simulacao:
            label = 'lora trajectory'
            plt.subplot(323)


        elif 'LTr' == tipo_simulacao:
            label = 'lora trajectory random'
            plt.subplot(324)
        

        elif 'LTb' == tipo_simulacao:
            label = 'Trajectory skip'
            plt.subplot(325)

        elif 'LTbr' == tipo_simulacao:
            label = 'lora trajectory random skip'
            plt.subplot(326)
    
        colors = {7: 'darkblue', 8: 'blue', 9: 'lightblue', 10: 'lightcoral', 11: 'red', 12: 'darkred'}
        a = df['SF'].map(colors)
        print(df[df['id']==100])
        plt.scatter(df['timestamp'], df['id'], alpha=0.2, c=a.values)
        plt.xticks([0, 250, 500, 750, 1000, 1200])
        plt.title(label)
        plt.xlim(0,1200)
        
        break

plt.show()


