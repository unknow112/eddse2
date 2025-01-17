import json
import os
from multiprocessing import Pool

import click
from src.oneliner_utils import join_path, read_jsonl_plain
from tqdm import tqdm


def add_abstracts(lang: str, fos: str, prog_bar_position: int):
    # Folder paths
    datasets_path = join_path("tmp", "datasets")
    lang_path = join_path(datasets_path, lang)
    dataset_path = join_path(lang_path, fos)
    final_dataset_path = join_path("datasets", lang, fos)
    os.makedirs(final_dataset_path, exist_ok=True)

    # File paths
    papers_path = join_path(dataset_path, "papers.jsonl")
    abstracts_path = join_path(dataset_path, "abstracts.jsonl")
    collection_path = join_path(final_dataset_path, "collection.jsonl")

    papers_dict = {x["id"]: x for x in read_jsonl_plain(papers_path)}

    with open(abstracts_path, "r") as abstracts_f, open(
        collection_path, "w"
    ) as write_f:
        for line in tqdm(
            abstracts_f,
            mininterval=1.0,
            desc="Adding abstracts",
            dynamic_ncols=True,
            position=prog_bar_position,
        ):
            abstract = json.loads(line)
            doc_id = abstract["doc_id"]
            paper = papers_dict.get(doc_id, False)
            if paper:
                paper["text"] = abstract["text"]
                del paper["cit_count"]
                del paper["estimated_cit_count"]
                del paper["ref_count"]
                write_f.write(json.dumps(paper) + "\n")
                del papers_dict[doc_id]
            else:
                print(doc_id, "not found")
                exit()


@click.command()
@click.argument("fos_list", nargs=-1)
@click.option("--lang", default="en")
def main(lang, fos_list):
    with Pool(len(fos_list)) as pool:
        pool.starmap(
            add_abstracts,
            ((lang, fos, i) for i, fos in enumerate(fos_list)),
        )


if __name__ == "__main__":
    main()
