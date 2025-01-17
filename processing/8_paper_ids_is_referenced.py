import json
import os
from collections import defaultdict
import bz2
from multiprocessing import Pool

import click
from src.oneliner_utils import join_path, read_list, write_list
from tqdm import tqdm


def get_doc_ids(lang: str, fos: str):
    # Folder paths
    raw_data_path = join_path("tmp", "raw_data")
    datasets_path = join_path("tmp", "datasets")
    lang_path = join_path(datasets_path, lang)
    dataset_path = join_path(lang_path, fos)

    # File paths
    papers_path = join_path(raw_data_path, "papers.jsonl")
    paper_references_path = join_path(raw_data_path, "paper_references.jsonl")
    doc_ids_path = join_path(dataset_path, "doc_ids.txt")
    final_doc_ids_path = join_path(dataset_path, "final_doc_ids.txt")
    doc_ids_with_timestamps = dict.fromkeys(read_list(doc_ids_path), None)

    with bz2.open(papers_path, "r") as papers_f:
        for line in tqdm(
            papers_f,
            mininterval=1.0,
            desc="Loading paper dates",
            dynamic_ncols=True,
        ):
            paper = json.loads(line)
            paper_id = paper["id"]
            if paper_id in doc_ids_with_timestamps:
                doc_ids_with_timestamps[paper_id] = paper["timestamp"]

    paper_references_dict = {}
    is_referenced_ids = set()

    with bz2.open(paper_references_path, "r") as f_in:
        for line in tqdm(
            f_in,
            mininterval=1.0,
            desc="Loading paper references",
            dynamic_ncols=True,
        ):
            paper_references = json.loads(line)
            doc_id = paper_references["doc_id"]

            if doc_id in doc_ids_with_timestamps:
                date = doc_ids_with_timestamps[doc_id]
                rel_doc_ids = paper_references["rel_doc_ids"]

                # Keep only references in current fos and pointing backword
                rel_doc_ids = set(
                    x
                    for x in rel_doc_ids
                    if x in doc_ids_with_timestamps
                    and doc_ids_with_timestamps[x] < date
                )

                paper_references_dict[doc_id] = rel_doc_ids
                is_referenced_ids |= rel_doc_ids

    while len(is_referenced_ids) > 5_000_000:
        paper_references_dict = {
            k: v
            for k, v in tqdm(
                paper_references_dict.items(),
                mininterval=1.0,
                desc="Removing non-referenced papers",
                dynamic_ncols=True,
            )
            if k in is_referenced_ids
        }

        is_referenced_ids = set()
        for rel_doc_ids in tqdm(
            paper_references_dict.values(),
            mininterval=1.0,
            desc="Getting referenced paper ids",
            dynamic_ncols=True,
        ):
            rel_doc_ids = [x for x in rel_doc_ids if x in paper_references_dict]
            is_referenced_ids |= set(rel_doc_ids)

    print(set(paper_references_dict) == is_referenced_ids)
    print(f"Remaining papers: {len(is_referenced_ids)}")
    write_list(list(is_referenced_ids), final_doc_ids_path)


@click.command()
@click.argument("fos_list", nargs=-1)
@click.option("--lang", default="en")
def main(lang, fos_list):
    for i, fos in enumerate(fos_list):
        print(f"{i+1}/{len(fos_list)} - {fos}")
        get_doc_ids(lang, fos)


if __name__ == "__main__":
    main()
