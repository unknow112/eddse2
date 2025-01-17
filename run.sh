#!/bin/bash
set -xe

# Create datasets folder
mkdir -p datasets

# DEFINE FIELDS OF STUDY (DISCIPLINES) -----------------------------------------
fos="computer_science physics political_science psychology"

# PARSING ----------------------------------------------------------------------
parallel -L 1 python -m  <<EOF
    parsing.abstracts
    parsing.affiliations
    parsing.authors
    parsing.conference_instances
    parsing.conference_series
    parsing.field_of_study_children
    parsing.fields_of_study
    parsing.journals
    parsing.paper_authors
    parsing.paper_field_of_study
    parsing.paper_languages
    parsing.paper_references
    parsing.paper_tags
    parsing.papers
    parsing.citation_contexts
EOF

# PROCESSING -------------------------------------------------------------------
python -m processing.0_fos
bzip2 tmp/raw_data/fields_of_study.jsonl
mv tmp/raw_data/fields_of_study.jsonl.bz2 tmp/raw_data/fields_of_study.jsonl
python -m processing.1_paper_ids_by_lang
python -m processing.2_paper_ids_by_fos
bash processing/2.1_paper_decompress.sh
python -m processing.3_paper_ids_has_abstract
bash processing/4_paper_ids_has_date.sh
bash processing/6_paper_ids_has_author.sh
bash processing/7_paper_ids_has_tags.sh
python -m processing.8_paper_ids_is_referenced $fos

python -m processing.9_papers $fos
python -m processing.10_abstracts $fos
python -m processing.11_paper_author_affiliations $fos
python -m processing.12_tags $fos
python -m processing.13_fos $fos
python -m processing.14_conference_instances $fos
python -m processing.15_conference_series $fos
python -m processing.16_journals $fos
python -m processing.17_paper_references $fos
python -m processing.18_authors $fos

python -m processing.19_add_abstracts_to_papers $fos
python -m processing.20_add_tags_to_papers $fos
python -m processing.21_add_fos_to_papers $fos


# QUERIES ----------------------------------------------------------------------
python -m processing.22_generate_queries $fos

python -m processing.23_split_queries psychology --year=2019
python -m processing.23_split_queries physics --year=2017
python -m processing.23_split_queries computer_science --year=2017
python -m processing.23_split_queries political_science --year=2016

python -m processing.24_filter_test_queries --fos=psychology --year=2019
python -m processing.24_filter_test_queries --fos=physics --year=2017
python -m processing.24_filter_test_queries --fos=computer_science --year=2017
python -m processing.24_filter_test_queries --fos=political_science --year=2016


python -m processing.25_filter_test_docs --fos=psychology --year=2019
python -m processing.25_filter_test_docs --fos=physics --year=2017
python -m processing.25_filter_test_docs --fos=computer_science --year=2017
python -m processing.25_filter_test_docs --fos=political_science --year=2016

# BM25 -------------------------------------------------------------------------
for FOS in $fos;
do
    python -m bm25.1_prepare_collection_for_indexing --fos=$FOS
    python -m bm25.2_index_collection --fos=$FOS
    python -m bm25.3_search_bm_25_config --fos=$FOS
    python -m bm25.4_compute_bm25_results --fos=$FOS
done

# Finalize datasets ------------------------------------------------------------
for FOS in $fos;
do
    python -m finalize_data.1_split_queries --fos=$FOS
    python -m finalize_data.2_extract_qrels --fos=$FOS
    python -m finalize_data.3_extract_bm25_runs --fos=$FOS
    python -m finalize_data.4_extract_query_ids --fos=$FOS
    python -m finalize_data.5_extract_references --fos=$FOS
    python -m finalize_data.6_extract_authors --fos=$FOS
    python -m finalize_data.7_extract_fos_hierarchies --fos=$FOS
    python -m finalize_data.8_extract_affiliations --fos=$FOS
    python -m finalize_data.9_extract_venues --fos=$FOS
done