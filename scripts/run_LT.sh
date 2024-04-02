#!/bin/bash

# Defina o diretório onde estão os arquivos Python
diretorio="lts"

# Verifica se o diretório existe
if [ ! -d "$diretorio" ]; then
    echo "O diretório especificado não existe."
    exit 1
fi
n=30
# Loop para percorrer todos os arquivos Python no diretório
for arquivo in "$diretorio"/*.py; do
    for ((i=1; i<=$n; i++))
    do
        numero_aleatorio=$(shuf -i 1-10000 -n 1)
        numero_aleatorio_pacotes=$(shuf -i 1-10 -n 1)
        chan=3
        packetlen=20   ##NODES SEND PACKETS OF JUST 20 Bytes
        total_data=60 ##$((20 * numero_aleatorio_pacotes)) ##TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
        beacon_time=120 ###SAT SENDS BEACON EVERY CERTAIN TIME
        maxBSReceives=16 ##MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
        pskip=4000
        echo "totaldata: $total_data"
        echo "Executando o arquivo: $arquivo"
        echo "-----------------------------------------"
        python3 "$arquivo" "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 1 1 2 5 7 1 1 1 1 2 2 2 2 6000 3500  "$pskip"
        echo "-----------------------------------------"
        echo "O número aleatório gerado é: $numero_aleatorio"
    done
done


## normal        python3 "$arquivo" "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 10 100 200 500 750 1000 1250 1500 1750 2000 2250 2500 2750 3000 3500  "$pskip"
