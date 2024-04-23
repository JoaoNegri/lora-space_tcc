#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Uso: $0 <simulação_desejada>"
    exit 1
fi

valor=$1

simulacoes=("eb" "et" "er" "etb" "etbr" "etr")

for item in "${simulacoes[@]}"; do
    if [ "$item" = "$valor" ]; then
        encontrado=1
        break
    fi
done

if [ $encontrado -eq 1 ]; then
    echo "simulando '$valor'"
else
    echo "Erro: O valor '$valor' não é permitido, utilize um dos seguintes eb et er etb etbr etr "
    exit 1
fi

# Defina o diretório onde estão os arquivos Python
diretorio="../antigos_simuladores/es"

# Verifica se o diretório existe
if [ ! -d "$diretorio" ]; then
    echo "O diretório especificado não existe."
    exit 1
fi
n=3
# Loop para percorrer todos os arquivos Python no diretório


for ((i=1; i<=$n; i++))
do
    numero_aleatorio=$(shuf -i 1-10000 -n 1)
    chan=3
    packetlen=20   ##NODES SEND PACKETS OF JUST 20 Bytes
    total_data=200 ##TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
    beacon_time=120 ###SAT SENDS BEACON EVERY CERTAIN TIME
    maxBSReceives=500 ##MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
    pskip=100000
    echo "Executando o item: $valor"
    echo "-----------------------------------------"
    echo ../src/main.py "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 5 10 50 100 200 500 750 1000 5000 10000 25000 50000 100000 150000 "$pskip" "$valor"
    python3 ../src/main.py "$numero_aleatorio" "$chan" "$packetlen" "$total_data" "$beacon_time" "$maxBSReceives" 5 10 50 100 200 500 750 1000 5000 10000 25000 50000 100000 150000 "$pskip" "$valor"
    echo "-----------------------------------------"
    echo "O número aleatório gerado é: $numero_aleatorio"
done
