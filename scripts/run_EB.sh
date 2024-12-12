#!/bin/bash

# Defina o diretório onde estão os arquivos Python
diretorio="../antigos_simuladores/es"

# Verifica se o diretório existe
if [ ! -d "$diretorio" ]; then
    echo "O diretório especificado não existe."
    exit 1
fi
n=1
# Loop para percorrer todos os arquivos Python no diretório
for arquivo in "$diretorio"/*.py; do
    for ((i=1; i<=$n; i++))
    do
if [ "$arquivo" != "../antigos_simuladores/es/EB2_args_v05.py" ]; then
        numero_aleatorio=$(shuf -i 1-10000 -n 1)
        chan=3
        packetlen=20   ##NODES SEND PACKETS OF JUST 20 Bytes
        # total_data=200 ##TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
        total_data=$(echo "100 120 140 160 180 200" | tr " " "\n" | shuf -n 1)
        beacon_time=120 ###SAT SENDS BEACON EVERY CERTAIN TIME
        maxBSReceives=500 ##MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
        pskip=100000
        echo "Executando o arquivo: $arquivo"
        echo "-----------------------------------------"
        echo "$arquivo" "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 5 10 50 100 200 500 750 1000 5000 10000 25000 50000 75000 100000 "$pskip"
        python3 "$arquivo" "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 5 10 50 100 200 500 750 1000 5000 10000 25000 50000 75000 100000 "$pskip"
        echo "-----------------------------------------"
        echo "O número aleatório gerado é: $numero_aleatorio"
        fi
    done
done
