# Logical Inference System for Temporal Order

## Setup

The system runs on docker. You need to execute the following commands.
```sh
$ docker pull masashiy/ccg2lambda
$ docker run -w /root/ -d -it -v <WORKDIR>:/home --name ccg2lambda masashiy/ccg2lambda:latest
$ docker exec -it ccg2lambda /bin/bash
$ apt update
$ apt install unzip
```

Then, you should clone this repository and place it on the container.

```sh
$ git clone https://github.com/ynklab/ccgtemp.git
$ cd ccgtemp
```

It is necessary to install depccg (version 1.1.0), janome (version 0.3.9), more_itertools.

```sh
$ pip install depccg==1.1.0 janome==0.3.9 more_itertools
$ depccg_ja download
```

In addition, [vampire Ver.4.4 with Z3](https://vprover.github.io/bin/vampire_z3_rel_static_release_v4.4) and [tregex Ver.3.9.2](https://nlp.stanford.edu/software/stanford-tregex-2018-10-16.zip) are required. (You should rename the vampire file to "vampire".)

```sh
$ curl --create-dirs -o "vampire/vampire" https://vprover.github.io/bin/vampire_z3_rel_static_release_v4.4
$ chmod 755 vampire/vampire
$ wget https://nlp.stanford.edu/software/stanford-tregex-2018-10-16.zip
$ unzip stanford-tregex-2018-10-16.zip
$ rm stanford-tregex-2018-10-16.zip
```

You need to write the path to the vampire and tregex directories in vampire_location.txt and tregex_location.txt respectively.

```sh
$ echo "./vampire" > vampire_location.txt
$ echo "./stanford-tregex-2018-10-16" > tregex_location.txt
```

## data

Dataset is in data directory.
* data/jsem/jsem_temporal_order.csv: JSeM problems involving temporal order.
* data/plmute/cs1_test_ja.csv: test data of PLMUTE
* data/plmute/cs1_train_ja.csv: all training data of PLMUTE
* data/plmute/cs1_test_ja.csv: part of training data of PLMUTE

## Usage

### Sample Problem

If you want to perform inference with a sample problem, you can run commands like the following.
```sh
$ ./rte_tsurgeon_vamp.sh sample.txt templates/semantic_templates_ja_tense.yaml ja vampire 1 templates/transform.tsgn sample_dir
$ cat sample_dir/ja_results/sample.txt.answer
```
If you want to perform inference with a different problem, you need to delete the output of the previous inference.

### JSeM

If you want to perform inference with jsem, you can run following commands.
```sh
$ python3 make_problems.py jsem
$ ./temporal_inference_wrap.sh jsem
```
The result will be output to jsem/overall_results.tsv.

### PLMUTE

If you want to perform inference with PLMUTE_ja, you can run following commands.
```sh
$ python3 make_problems.py plmute
$ ./temporal_inference_wrap.sh plmute
```

It may take 20 hours to complete. (Depends on the performance of the execution environment)

The result will be output to plmute/overall_results.tsv.

## Citation

If you use this dataset in any published research, please cite the following:

* Tomoki Sugimoto and Hitomi Yanaka. 2022. [Compositional Semantics and Inference System for Temporal Order based on Japanese CCG](https://aclanthology.org/2022.acl-srw.10/). In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop, pages 104–114, Dublin, Ireland. Association for Computational Linguistics.

```bibtex
@inproceedings{sugimoto-yanaka-2022-compositional,
    title = "Compositional Semantics and Inference System for Temporal Order based on {J}apanese {CCG}",
    author = "Sugimoto, Tomoki  and
      Yanaka, Hitomi",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.acl-srw.10",
    pages = "104--114",
}
```

## Contact

For questions and usage issues, please contact sugimoto.tomoki@is.s.u-tokyo.ac.jp .

## License

* [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
