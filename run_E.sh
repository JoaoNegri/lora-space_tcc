#!/bin/bash

# Defina o diretório onde estão os arquivos Python
diretorio="es"

# Verifica se o diretório existe
if [ ! -d "$diretorio" ]; then
    echo "O diretório especificado não existe."
    exit 1
fi
n=2
# Loop para percorrer todos os arquivos Python no diretório
for arquivo in "$diretorio"/*.py; do
    for ((i=1; i<=$n; i++))
    do
        numero_aleatorio=$(shuf -i 1-10000 -n 1)
        chan=3
        packetlen=20   ##NODES SEND PACKETS OF JUST 20 Bytes
        total_data=200 ##TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
        beacon_time=120 ###SAT SENDS BEACON EVERY CERTAIN TIME
        maxBSReceives=500 ##MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
        pskip=100000
        echo "Executando o arquivo: $arquivo"
        echo "-----------------------------------------"
        python3 "$arquivo" "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 5 10 50 100 200 500 750 1000 5000 10000 25000 50000 100000 150000 200000  "$pskip"
        echo "-----------------------------------------"
        echo "O número aleatório gerado é: $numero_aleatorio"
    done
done
