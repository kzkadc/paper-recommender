from recommend.models import ReferencePaper, ConferenceName, Conference

import pandas as pd
from tqdm import tqdm


def parse_args(args: str):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--conference", required=True)
    parser.add_argument("--year", type=int, required=True)
    args_parsed = parser.parse_args(args.split(" "))
    return args_parsed


def run(args):
    args = parse_args(args)

    conf_name = ConferenceName.objects.get(name=args.conference)
    conf = Conference.objects.get(conference=conf_name, year=args.year)

    df = pd.read_csv(args.csv)
    for _, row in tqdm(df.iterrows(), total=len(df)):
        ReferencePaper.objects.create(
            title=row["title"],
            abstract=row["abstract"],
            url=row["url"],
            published_at=conf
        )
