import pandas as pd
import matplotlib.pyplot as plt
import os

path = '../../resultados/teste_fig_7'

tipos_simulacao = os.listdir('../../resultados/teste_fig_7')
for tipo_simulacao in tipos_simulacao: #lb, lt...
    i = 0
    iteracoes = os.listdir(path+'/'+tipo_simulacao)
    for iteracao in iteracoes:#lr_3ch...
        print(iteracao)
        if iteracao.split('_')[-1] == 'p3':
            
            sim =  os.listdir(path+'/'+tipo_simulacao+'/'+iteracao)
            for aux in sim:
                if aux.split('_')[1] == '6000':

                    df = pd.read_csv(path+'/'+tipo_simulacao+'/'+iteracao+'/'+aux,names=['timestamp','id','dist','elev','SF','status','pct2snd'])
                    print(df)
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
                    plt.scatter(df['timestamp'], df['id'], alpha=0.2, c=a.values)
                    import matplotlib.patches as mpatches
                    legend_patches = [mpatches.Patch(color=color, label=f'SF {value}') for value, color in colors.items()]
                    plt.legend(handles=legend_patches)
                    plt.xticks([0, 250, 500, 750, 1000, 1200])
                    if 'LTb' == tipo_simulacao or 'LTbr' == tipo_simulacao:
                        plt.xlabel('Tempo de passagem', fontsize=14)
                    plt.ylabel('End device id',fontsize=14)
                    plt.title(label, fontsize=14)
                    plt.xlim(0,1200)
                    break

plt.show()


