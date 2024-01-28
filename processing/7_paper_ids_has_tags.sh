#!/bin/bash
set -xe

# Note: script takes arguments through env
LANG=$(test -z $LANG && echo en || echo $LANG)
FOS_LIST="history biology medicine computer_science environmental_science mathematics geography materials_science chemistry political_science economics psychology business sociology art philosophy engineering geology physics"
VALID_SET_FN=tmp/raw_data/doc_ids_paper_has_tags.txt

bzip2 -c -d tmp/raw_data/paper_tags.jsonl | jq -r 'select(.keywords | length >0).doc_id' | sort | uniq  > ${VALID_SET_FN}      

# Note: we can assume from the stage six that the doc_ids.txt are unique already
echo $FOS_LIST  | tr ' ' '\n' | parallel -I{} cat ${VALID_SET_FN} tmp/datasets/en/{}/doc_ids.txt \| sort \| uniq -d \> tmp/datasets/en/{}/doc_ids_pubdate_filtered.txt '&&' mv tmp/datasets/en/{}/doc_ids_pubdate_filtered.txt tmp/datasets/en/{}/doc_ids.txt
