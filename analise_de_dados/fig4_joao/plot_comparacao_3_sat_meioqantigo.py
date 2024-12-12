import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

satellites = ['sat1', 'sat2', 'sat3']
base_path = '../../resultados/'

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for idx, sat in enumerate(satellites):
    folders = os.listdir(base_path + sat + '/')
    dfs = []

    for folder in folders:
        iteracao = os.listdir(base_path + sat + '/' + folder)
        node = []
        percentual = []
        i = 0
        df = pd.DataFrame()

        for it in iteracao:
            files = os.listdir(base_path + sat + '/' + folder + '/' + it)
            for file in files:
                sim = pd.read_csv(base_path + sat + '/' + folder + '/' + it + '/' + file, names=['timestamp', 'id', 'dist', 'elev', 'SF', 'num', 'status', 'a', 'b', 'c', 'd'])
                node.append(int(file.split('_')[1]))
                processed = len(sim[sim['status'] == 'PE'])
                num_packet = len(sim['status'])
                percentual.append(processed / num_packet)

            if df.empty:
                data = {'num_nodes' + 'LB' + '0': node, 'percentual' + "LB" + '0': percentual}
                df = pd.DataFrame(data)
                df = df.sort_values('num_nodes' + 'LB' + '0')
                df.reset_index(inplace=True, drop=True)
            else:
                data = {'num_nodes' + folder + str(i): node, 'percentual' + folder + str(i): percentual}
                df2 = pd.DataFrame(data)
                df2 = df2.sort_values('num_nodes' + folder + str(i))
                df2.reset_index(inplace=True, drop=True)
                df['num_nodes' + folder + str(i)] = df2['num_nodes' + folder + str(i)]
                df['percentual' + folder + str(i)] = df2['percentual' + folder + str(i)]

            node = []
            percentual = []
            i += 1
        dfs.append(df)

    for item in dfs:
        colunas_percentual = [coluna for coluna in item.columns if 'percentual' in coluna]
        colunas_num_nodes = [coluna for coluna in item.columns if 'num_nodes' in coluna]

        desvio_padrao_por_linha = item[colunas_percentual].std(axis=1)
        media = item[colunas_percentual].mean(axis=1)
        soma = 2.45 * (desvio_padrao_por_linha / np.sqrt(30))

        if 'percentualLB0' in item.columns:
            label = 'lora conservative'
            axes[idx].plot(item[colunas_num_nodes[0]], media, label=label)
            axes[idx].fill_between(item[colunas_num_nodes[0]], media - soma, media + soma, alpha=0.3)

    axes[idx].set_title(f'Satellite {sat}')
    axes[idx].set_ylim(0.17, 1)
    axes[idx].set_xlim(0, 3e3)
    axes[idx].set_yscale("log")
    axes[idx].grid(True, axis='both')
    axes[idx].legend()

plt.yticks([1, 0.6, 0.4, 0.3, 0.2])
plt.show()
