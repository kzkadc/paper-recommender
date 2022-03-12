import re
import time
from typing import Callable

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, help="URL")
    parser.add_argument("-c", required=True, help="conference",
                        choices=["neurips", "cvf", "pmlr"])
    parser.add_argument("-o", required=True, help="output csv file name")
    args = parser.parse_args()
    main(args)


def main(args):
    source = requests.get(args.i).text
    soup = BeautifulSoup(source, "lxml")

    metadata_getter: Callable[[str], dict]
    if args.c == "neurips":
        paper_urls = soup.find(
            "div", class_="container-fluid").find("ul").find_all("li")

        paper_urls = ["https://papers.nips.cc" +
                      p.find("a").get("href") for p in paper_urls]
        metadata_getter = get_neurips_metadata
    elif args.c == "cvf":
        paper_urls = soup.find_all("dt", class_="ptitle")
        paper_urls = ["https://openaccess.thecvf.com" +
                      p.find("a").get("href") for p in paper_urls]
        metadata_getter = get_cvf_metadata
    elif args.c == "pmlr":
        paper_urls = soup.find_all("div", class_="paper")
        paper_urls = [p.find("a", text="abs").get("href")
                      for p in paper_urls]
        metadata_getter = get_pmlr_metadata
    else:
        raise ValueError(f"invalid conference: {args.c}")

    df = {
        "title": [],
        "abstract": [],
        "url": []
    }
    for i, p in tqdm(enumerate(paper_urls), total=len(paper_urls)):
        sleep_random_time(3, 2, 1)

        metadata = metadata_getter(p)
        tqdm.write(metadata["title"])

        df["title"].append(metadata["title"])
        df["abstract"].append(metadata["abstract"])
        df["url"].append(p)

        if i % 10 == 1:
            pd.DataFrame(df).to_csv(args.o, index=False)

    pd.DataFrame(df).to_csv(args.o, index=False)


def get_arxiv_metadata(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    metadata = {}
    metadata["title"] = soup.find(
        class_="title mathjax").text.replace("Title:", "")
    metadata["abstract"] = soup.find(class_="abstract mathjax").text.replace(
        "Abstract: ", "").replace("\n", " ").strip()
    metadata["authors"] = soup.find(
        class_="authors").text.replace("Authors:", "")
    metadata["date"] = soup.find(
        "meta", attrs={"name": "citation_date"})["content"]

    comments = soup.find(class_="tablecell comments mathjax")
    if comments is not None:
        comments = comments.text.strip()
        conference = re.search(r"(?:accepted)|(?:appear) .+ ([a-z]{4})\s?[0-9]{4}",
                               comments, flags=re.IGNORECASE)
        if conference is None:
            conference = re.fullmatch(r"([A-Z]{4})\s?[0-9]{4}", comments)
        is_not_workshop = re.search(
            "workshop", comments, re.IGNORECASE) is None
        if is_not_workshop and conference is not None:
            metadata["conference"] = conference.group(1).upper()

    return metadata


def get_cvf_metadata(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")

    metadata = {
        "title": soup.find("meta", attrs={"name": "citation_title"}).get("content"),
        "abstract": soup.find(id="abstract").text.replace("\n", " ").strip(),
        "authors": soup.find(id="authors").find("b").text
    }

    conf_full = soup.find(id="authors").text
    is_not_workshop = re.search(
        r"workshop", conf_full, flags=re.IGNORECASE) is None
    if is_not_workshop:
        conf_title = re.search(r"([A-Z]{4})\s?\d{4}", soup.find("title").text)
        if conf_title is not None:
            metadata["conference"] = conf_title.group(1)

    return metadata


def get_neurips_metadata(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")

    return {
        "title": soup.find("meta", attrs={"name": "citation_title"}).get("content"),
        "authors": soup.find("h4", text="Authors").next_sibling.next_sibling.text,
        # "abstract": soup.find("h4", text="Abstract").next_sibling.next_sibling.text.replace("\n", " "),
        "abstract": soup.find("div", class_="col").find_all("p", recursive=False)[-1].text.replace("\n", " "),
        "conference": "NeurIPS",
        "date": ""
    }


def get_pmlr_metadata(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")

    metadata = {
        "title": soup.find("meta", attrs={"name": "citation_title"}).get("content"),
        "abstract": soup.find(id="abstract").text.replace("\n", " ").strip(),
        "date": soup.find("meta", attrs={"name": "citation_publication_date"}).get("content"),
        "authors": soup.find(class_="authors").text.replace("\xa0", " ").strip()
    }

    CONF_TABLE = {
        "International Conference on Machine Learning": "ICML",
        "Conference on Learning Theory": "COLT",
        "International Conference on Artificial Intelligence and Statistics": "AISTATS",
        "Asian Conference on Machine Learning": "ACML",
        "Medical Imaging with Deep Learning": "MIDL",
        "Uncertainty in Artificial Intelligence": "UAI",
        "International Symposium on Imprecise Probability: Theories and Applications": "ISIPTA",
        "International Conference on Grammatical Inference": "ICGI"
    }
    conf = soup.find(id="info").find("i").text
    for fullname, name in CONF_TABLE.items():
        m = re.search(fullname, conf, flags=re.IGNORECASE)
        if m is not None:
            metadata["conference"] = name
            break

    return metadata


def sleep_random_time(mean: float, std: float, at_least: float):
    t = np.maximum(np.random.normal(mean, std), at_least)
    time.sleep(t)


if __name__ == "__main__":
    parse_args()
