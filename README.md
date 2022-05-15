# Logical Inference System for Temporal Order

## Setup

```
$ pip install depccg==1.1.0
$ pip install janome==0.3.9
$ depccg_ja download
$ pip install more_itertools
```

In addition, [vampire Ver.4.4 with Z3](https://vprover.github.io/bin/vampire_z3_rel_static_release_v4.4) and [tregex Ver.3.9.2](https://nlp.stanford.edu/software/stanford-tregex-2018-10-16.zip) are required. (You should rename the vampire file to "vampire".)

You need to write the path to the vampire and tregex directories in vampire_location.txt and tregex_location.txt respectively.

## data

Dataset is in data directory.
* data/jsem/jsem_temporal_order.csv: JSeM problems involving temporal order.
* data/plmute/cs1_test_ja.csv: test data of PLMUTE
* data/plmute/cs1_train_ja.csv: all training data of PLMUTE
* data/plmute/cs1_test_ja.csv: part of training data of PLMUTE

## Usage

### Sample Problem

If you want to perform inference with a sample problem, you can run commands like the following.
```
$ ./rte_tsurgeon_vamp.sh sample.txt templates/semantic_templates_ja_tense.yaml ja vampire 1 templates/transform.tsgn sample_dir
$ cat sample_dir/ja_results/sample.txt.answer
```
If you want to perform inference with a different problem, you need to delete the output of the previous inference.

### JSeM

If you want to perform inference with jsem, you can run following commands.
```
$ python3 make_problems.py jsem
$ ./temporal_inference_wrap.sh jsem
```
The result will be output to jsem/overall_results.tsv.

### PLMUTE

If you want to perform inference with PLMUTE_ja, you can run following commands.
```
$ python3 make_problems.py plmute
$ ./temporal_inference_wrap.sh plmute
```

It may take 20 hours to complete. (Depends on the performance of the execution environment)

The result will be output to plmute/overall_results.tsv.