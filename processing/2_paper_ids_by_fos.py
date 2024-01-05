import json
import bz2
import os

import click
from src.oneliner_utils import join_path, read_jsonl_iter, read_iterable
from tqdm import tqdm

fos_id_dict = {
    "history": "95457728",
    "biology": "86803240",
    "medicine": "71924100",
    "computer_science": "41008148",
    "environmental_science": "39432304",
    "mathematics": "33923547",
    "geography": "205649164",
    "materials_science": "192562407",
    "chemistry": "185592680",
    "political_science": "17744445",
    "economics": "162324750",
    "psychology": "15744967",
    "business": "144133560",
    "sociology": "144024400",
    "art": "142362112",
    "philosophy": "138885662",
    "engineering": "127413603",
    "geology": "127313418",
    "physics": "121332964",
}


@click.command()
@click.option("--lang", default="en")
def main(lang):
    # Folder paths
    raw_data_path = join_path("tmp", "raw_data")
    datasets_path = join_path("tmp", "datasets")
    doc_ids_by_lang_path = join_path(raw_data_path, "lang")
    lang_path = join_path(datasets_path, lang)

    # File paths
    fos_path = join_path(raw_data_path, "fields_of_study.jsonl")
    paper_fos_path = join_path(raw_data_path, "paper_fields_of_study.jsonl")
    lang_doc_ids_path = join_path(doc_ids_by_lang_path, f"{lang}_doc_ids.txt")

    lang_doc_ids = set(read_iterable(lang_doc_ids_path))
    print("lang_doc_ids loaded OK")
    fos_dict = {x["id"]: x for x in read_jsonl_iter(fos_path)}
    print("fos_dict loaded OK")

    doc_ids_by_fos_dict={}
    try: 
        for fos, fos_id in fos_id_dict.items():
            dataset_path = join_path(lang_path, fos)
            os.makedirs(dataset_path, exist_ok=True)
            write_path = join_path(dataset_path, "doc_ids.txt.bz2")
            doc_ids_by_fos_dict[fos_id] = bz2.open(write_path, "wt")

        with bz2.open(paper_fos_path, "rt") as f_in:
            for line in tqdm(
                f_in,
                mininterval=1.0,
                desc="Dividing doc ids by discipline",
                dynamic_ncols=True,
            ):
                doc = json.loads(line)
                doc_fos_id = doc["fos_id"]
                fos_id = fos_dict[doc_fos_id]["level_0"]

                if doc["doc_id"] in lang_doc_ids and fos_id in doc_ids_by_fos_dict:
                    print(doc["doc_id"], file=doc_ids_by_fos_dict[fos_id], flush=False)
    
    finally:
        for f in doc_ids_by_fos_dict.values():
            f.close()


if __name__ == "__main__":
    main()

# TODO: add stage 2.1 where the doc_ids per field of study get unzipped and removed duplicates