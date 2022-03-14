from django.contrib.auth.models import User
from django.utils.timezone import datetime

import pandas as pd
from tqdm import tqdm

from recommend.models import UserPaper


def parse_args(args: str):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--user", required=True)
    args_parsed = parser.parse_args(args.split(" "))
    return args_parsed


def run(args):
    args = parse_args(args)

    user = User.objects.get(username=args.user)

    df = pd.read_csv(args.csv)
    for _, row in tqdm(df.iterrows(), total=len(df)):
        UserPaper.objects.create(
            title=row["title"],
            abstract=row["abstract"],
            owner=user,
            memo=row["memo"],
            added_at=datetime.now()
        )
