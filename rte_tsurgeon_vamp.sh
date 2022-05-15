#!/bin/bash

# Script to Recognize Textual Entailment of problems in Japanese, using
# multiple CCG parsers (Jigg and depccg at the moment).
# This script receives a file with several sentences (one per line), where all
# sentences are premises except the last one, which is a conclusion. It returns
# 'yes' (the premises entail the conclusion), 'no' (there is a contradiction) or
# 'unknown' (none of the former).
# You can use it as:
# ./rte_tsurgeon_vamp.sh sample.txt templates/semantic_templates_ja_tense.yaml ja vampire 1 templates/transform.tsgn

USAGE="Usage: ./rte_tsurgeon_vamp.sh sample.txt templates/semantic_templates_ja_tense.yaml ja vampire 1 templates/transform.tsgn sample_dir"

# This variable contains the name of the dataset (fracas or jsem).
sentences_fname=$1
sentences_basename=${sentences_fname##*/}
if [ ! -f $sentences_fname ]; then
  echo "Error: File with plain sentences does not exist."
  echo $USAGE
  exit 1
fi

# This variable contains the filename where the category templates are.
category_templates=$2
if [ ! -f $category_templates ]; then
  echo "Error: File with semantic templates does not exist."
  echo $USAGE
  exit 1
fi

lang=$3
if [ ! $lang ]; then
  echo "Error: Set the language type."
  echo $USAGE
  exit 1
fi

proof=$4
if [ ! $proof ]; then
  echo "Error: Set the prover type."
  echo $USAGE
  exit 1
fi

# Set the number of nbest parses (Default: 1)
nbest='1'

# This variable contains the filename where the tsurgeon template are.
tsurgeon_templates=$6
# Create a file named "tregex_location.txt" at the "scripts" directory
# $ cat tregex_location.txt
# /path/to/stanford-tregex-20XX-XX-XX
tregex_dir=`cat tregex_location.txt`
export CLASSPATH=$tregex_dir/stanford-tregex.jar:$CLASSPATH



# These variables contain the names of the directories where intermediate
# results will be written.
dirname=$7
plain_dir=${dirname}"/"${lang}"_plain" # tokenized sentences.
parsed_dir=${dirname}"/"${lang}"_parsed" # parsed sentences into XML or other formats.
results_dir=${dirname}"/"${lang}"_results" # HTML semantic outputs, proving results, etc.
mkdir -p $dirname $plain_dir $parsed_dir $results_dir 

# Copy the input text to plain_dir
if [ ! -f ${plain_dir}/${sentences_basename} ]; then
  cp $sentences_fname ${plain_dir}/${sentences_basename}
fi

function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; }

function parse_depccg() {
  # Parse using depccg.
  base_fname=$1
  lang=$2
  if [ "${lang}" == "ja" ]; then
    cat ${plain_dir}/${base_fname} | \
    depccg_ja \
        --input-format raw \
        --annotator janome \
        --format jigg_xml \
        --nbest $nbest \
    > ${parsed_dir}/${base_fname}.jigg.xml \
    2> ${parsed_dir}/${base_fname}.log
  fi
  if [ "${lang}" == "en" ]; then
    cat ${plain_dir}/${base_fname} | \
    depccg_en \
        --input-format raw \
        --annotator spacy \
        --format jigg_xml \
    > ${parsed_dir}/${base_fname}.jigg.xml \
    2> ${parsed_dir}/${base_fname}.log
    # candc_dir=`cat en/candc_location.txt`
    # env CANDC=${candc_dir} depccg_en \
    #     --input-format raw \
    #     --annotator candc \
    #     --format jigg_xml \
  fi
}

function tsurgeon() {
  sentences_basename=$1
  tsurgeon=$2
  python scripts/brackets.py ${parsed_dir}/${sentences_basename}.jigg.xml \
    > ${parsed_dir}/${sentences_basename}.ptb
  python scripts/extract_tempex.py $dirname ${sentences_basename} ./templates/tempex_list.txt
  python scripts/tempex_new.py $dirname ${sentences_basename} ./templates/tempex_list.txt
  java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon -s -treeFile ${parsed_dir}/${sentences_basename}.mod.ptb $tsurgeon
}

function semantic_parsing() {
  sentences_basename=$1
  python scripts/rule_add.py \
    $parsed_dir/${sentences_basename}.jigg.xml
  python scripts/semparse.py \
    $parsed_dir/${sentences_basename}.jigg.xml \
    $category_templates \
    $parsed_dir/${sentences_basename}.sem.xml \
    --arbi-types \
    2> $parsed_dir/${sentences_basename}.sem.err
}

function proving_coq() {
 sentences_basename=$1
 start_time=`python -c 'import time; print(time.time())'`
   timeout 200 python scripts/prove.py \
     ${parsed_dir}/${sentences_basename}.sem.xml \
     --graph_out ${results_dir}/${sentences_basename}.html \
     > ${results_dir}/${sentences_basename}.answer \
     2> ${results_dir}/${sentences_basename}.err
 rte_answer=`cat ${results_dir}/${sentences_basename}.answer`
#  echo "judging entailment for ${parsed_dir}/${sentences_basename}.sem.xml $rte_answer"
 proof_end_time=`python -c 'import time; print(time.time())'`
 proving_time=`echo "${proof_end_time} - ${start_time}" | bc -l | \
      awk '{printf("%.2f\n",$1)}'`
 echo $proving_time > ${results_dir}/${sentences_basename}.time
}

function proving_vampire() {
  sentences_basename=$1
  start_time=`python -c 'import time; print(time.time())'`
    timeout 1000 python scripts/eval_vampire.py \
      ${parsed_dir}/${sentences_basename}.sem.xml \
      ${plain_dir}/${sentences_basename} \
      --prover vampire \
      > ${results_dir}/${sentences_basename}.answer \
      2> ${results_dir}/${sentences_basename}.err
  rte_answer=`cat ${results_dir}/${sentences_basename}.answer`
  # echo "judging entailment ${parsed_dir}/${sentences_basename}.sem.xml $rte_answer"
  proof_end_time=`python -c 'import time; print(time.time())'`
  proving_time=`echo "${proof_end_time} - ${start_time}" | bc -l | \
       awk '{printf("%.2f\n",$1)}'`
  echo $proving_time > ${results_dir}/${sentences_basename}.time
}

# Set the current answer
current_answer="unknown"

if [ ${lang} == "en" -a ! -e "${sentence_basename/.txt/.tok}" ]; then
    cat $sentences_fname | \
    sed -f en/tokenizer.sed | \
    sed 's/ _ /_/g' | \
    sed 's/[[:space:]]*$//' \
    > ${plain_dir}/${sentences_basename/.txt/.tok}
    mv ${plain_dir}/${sentences_basename} ${plain_dir}/${sentences_basename/.txt/.origin.txt}
    mv ${plain_dir}/${sentences_basename/.txt/.tok} ${plain_dir}/${sentences_basename}
fi

# CCG parsing, semantic parsing and theorem proving
# echo "parsing ${plain_dir}/${sentences_basename}"
parse_depccg $sentences_basename $lang


# # Apply tsurgeon script
if [ $tsurgeon_templates ]; then
    # echo "Execute tsurgeon"
    tsurgeon $sentences_basename $tsurgeon_templates \
      > ${parsed_dir}/${sentences_basename}.tsgn.ptb
    cat ${parsed_dir}/${sentences_basename}.tsgn.ptb \
      | sed 's/</(/g' | sed 's/>/)/g' \
      | sed 's/{/[/g' | sed 's/}/]/g' \
      > ${parsed_dir}/${sentences_basename}.tsgn.tmp.ptb
    python -m depccg.tools.ja.tagger --format jigg_xml ${parsed_dir}/${sentences_basename}.tsgn.tmp.ptb \
      > ${parsed_dir}/${sentences_basename}.jigg.tmp.xml

    python scripts/my_map_tokens.py ${parsed_dir}/${sentences_basename}.jigg.xml \
      ${parsed_dir}/${sentences_basename}.jigg.tmp.xml \
      ./templates/tempex_list.txt \
      > ${parsed_dir}/${sentences_basename}.jigg.mod.xml
    mv ${parsed_dir}/${sentences_basename}.jigg.xml ${parsed_dir}/${sentences_basename}.jigg.origin.xml
    mv ${parsed_dir}/${sentences_basename}.jigg.mod.xml ${parsed_dir}/${sentences_basename}.jigg.xml
fi

# echo "semantic parsing $parsed_dir/${sentences_basename}.sem.xml"
semantic_parsing $sentences_basename

if [ ${proof} == 'vampire' ]; then
    proving_vampire $sentences_basename
elif [ ${proof} == 'coq' ]; then
    proving_coq $sentences_basename
fi


if [ -e ${results_dir}/${sentences_basename}.answer ]; then
  python scripts/visualize.py ${parsed_dir}/${sentences_basename}.sem.xml \
  > ${results_dir}/${sentences_basename}.html
fi


