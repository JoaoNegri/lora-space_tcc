# lora-dts-iot-sim
LoRa Direct-to-Satellite IoT is a simulator tool based on discrete event library Simpy, for Python. 

shell faz a simulação do lora legacy certinho
aparentemente o alvarez guido errou no uso da formula do intervalo de confiança para o lora legacy e usou o do t-student

* Comando referencia (4000 é o pskip (deve ser alterado em lrfhss))

python3 LTb_args_v07.py 20 3 20 200 120 16 10 50 100 300 500 750 1000 1225 1500 2000 2250 2500 2750 3000 4000


LB = lora conservative
LR = lora random
LT = lora trajectory
LTb = lora trajectory skip
LTbr = lora trajectory random skip
LTR = lora trajectory random
