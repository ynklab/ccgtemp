#!/bin/bash

problem=$1
core=${2:-3}
dirs=`find ${problem}_plain/* -maxdepth 0 -type d`
for dir in $dirs; do
    path=${dir##*/}
    problems_list=${problem}_plain/${path}_problems_list
    # if [ "${problem}" == "jsem" ]; then
    #     core='1'
    # fi
    ./temporal_inference_parallel.sh $core $problems_list
    echo -e "\n$path done"
done

rm ${problem}_plain/*_list_*
python temporal_inference_evaluate.py $problem
