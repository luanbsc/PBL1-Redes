#!/bin/bash

# Número de postos a criar
NUM_POSTOS=100
IMAGEM="imagem_posto"
PORTA_INICIAL=9001

for ((i=0; i<NUM_POSTOS; i++)); do
  PORTA=$((PORTA_INICIAL + i))
  CONTAINER="posto_$((i+1))"
  echo "Iniciando $CONTAINER na porta $PORTA..."
  docker run -d -p $PORTA:$PORTA -e STATION_TCP_PORT=$PORTA --name $CONTAINER $IMAGEM
done
