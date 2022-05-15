#!/bin/bash

# A script for paralell processing on jsem
# Set how many processes in parallel you want to run.
# The maximum number should be inferior to the number of cores in your machine.
# Default: 3

cores=${1:-3}
problems_list=$2
start_time=`date +%s`

# Set the semantic templates we want to evaluate:
templates="./templates/semantic_templates_ja_tense.yaml"
template_dir="./templates"

function inference() {
    dirname=$1
    fname=$2
    basename=${fname##*/}
    ./rte_tsurgeon_vamp.sh ./$fname \
        $templates ja vampire 1 $template_dir/transform.tsgn ${dirname}

    answer=`cat ${dirname}/ja_results/${basename}.answer`
    sentence=`cat ${dirname}/ja_plain/${basename}`
    if [ "`echo ${sentence} | grep '以前'`" ] || [ "`echo ${sentence} | grep '以後'`" ] || [ "`echo ${sentence} | grep '以降'`" ]; then
        if [ "$answer" == "unknown" ] || [ "$answer" == "no" ]; then
            python scripts/negated_required.py ${dirname}/ja_parsed/${basename}.pos.tptp
            flag=`cat ${dirname}/ja_parsed/${basename}.pos.tptp.flag`
            if [ "$flag" == "yes" ]; then
                if [ "`echo ${sentence} | grep '以降'`" ]; then
                    sentence2="`echo "${sentence}" | sed -e "$ s/以降/以前/g"`"
                    if [ "$sentence" != "$sentence2" ]; then
                        echo "`echo "${sentence}" | sed -e "$ s/以降/以前/g"`" > ${dirname}/ja_plain/${basename/.txt/.neg.txt}
                    fi
                fi
                if [ "`echo ${sentence} | grep '以後'`" ]; then
                    sentence2="`echo "${sentence}" | sed -e "$ s/以後/以前/g"`"
                    if [ "$sentence" != "$sentence2" ]; then
                        echo "`echo "${sentence}" | sed -e "$ s/以後/以前/g"`" > ${dirname}/ja_plain/${basename/.txt/.neg.txt}
                    fi
                fi
                if [ "`echo ${sentence} | grep '以前'`" ]; then
                    sentence2="`echo "${sentence}" | sed -e "$ s/以前/以降/g"`"
                    if [ "$sentence" != "$sentence2" ]; then
                        echo "`echo "${sentence}" | sed -e "$ s/以前/以降/g"`" > ${dirname}/ja_plain/${basename/.txt/.neg.txt}
                    fi
                fi
                ./rte_tsurgeon_vamp.sh ${dirname}/ja_plain/${basename/.txt/.neg.txt} \
                $templates ja vampire 1 $template_dir/transform.tsgn ${dirname}

                neganswer=`cat ${dirname}/ja_results/${basename/.txt/.neg.txt}.answer`
                if [ "$neganswer" == "yes" ]; then
                    real_answer="no"
                else
                    real_answer="unknown"
                fi
                echo "$real_answer" > ${dirname}/ja_results/${basename}.answer
            fi
        fi
    fi
}

# Split filename entries into several files, for parallel processing:
n=$((`cat $problems_list | wc -l`+1))
lines_per_split=`python -c "from math import ceil; print(int(ceil(float(${n})/${cores})))"`
split -l $lines_per_split $problems_list ${problems_list}_

# Run pipeline for each entailment problem.
for ff in ${problems_list}_??; do
  for f in `cat ${ff}`; do
    dir=$(dirname ${f})
    inference ./${dir/_plain/} $f
    mid_time=`date +%s`
    mid_run_time=$((mid_time - start_time))
    allcount=`find ./${dir/_plain/}/ja_plain/ -name "*.txt" | wc -l`
    negcount=`find ./${dir/_plain/}/ja_plain/ -name "*.neg.txt" | wc -l`
    c=$(($allcount-$negcount))
    printf "\r[%3d/${n}] %5ds" $c $mid_run_time
  done &
done

# Wait for the parallel processes to finish.
wait
