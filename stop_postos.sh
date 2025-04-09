#!/bin/bash

NUM_POSTOS=100

for ((i=0; i<NUM_POSTOS; i++)); do
  CONTAINER="posto_$((i+1))"
  echo "Removendo $CONTAINER..."
  docker rm -f $CONTAINER
done