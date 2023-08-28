from datetime import datetime
import pandas as pd
import sys


def get_csv(uri: str) -> pd.DataFrame:
    df = pd.read_csv(uri)
    return df


def last_message_sent(file_name: str, df: pd.DataFrame) -> bool:
    with open(file_name) as fl:
        last_date = fl.readlines()[-1]

    firm = df.iloc[0]["Polling Firm"]
    end = df.iloc[0]["Fieldwork End"]

    return f"{firm},{end}" != last_date


def get_parties(df: pd.DataFrame):
    return df.columns[9:]


def last_poll(df: pd.DataFrame) -> dict:
    firm = df.iloc[0]["Polling Firm"]
    firm_polls: pd.DataFrame = df[df["Polling Firm"] == firm].iloc[:2]
    parties = get_parties(df)
    parties_change = firm_polls[parties]
    # remove % sign
    parties_change = parties_change.apply(lambda x: x.str.replace("%", ""))
    # replace 'Not Available' with NaN
    parties_change = parties_change.replace("Not Available", float("nan"))
    parties_change = parties_change.dropna(how="all", axis=1)
    # convert to float
    parties_change = parties_change.astype(float)

    parties_change = (
        parties_change.diff().iloc[1].apply(lambda x: -x if x != 0 else 0).to_dict()
    )

    last = firm_polls.iloc[1]["Fieldwork End"]
    now = firm_polls.iloc[0]["Fieldwork End"]

    parties_change["last"] = last
    parties_change["now"] = now

    return parties_change


def build_image():
    ...


def send_message():
    ...


def main():
    ...


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: polls.py [country_code]", file=sys.stderr)
        sys.exit(1)

    uri = f"https://filipvanlaenen.github.io/eopaod/{sys.argv[1]}.csv"
    df = get_csv(uri)

    if not last_message_sent("last_poll.txt", df):
        print("Poll already sent")
        sys.exit(0)

    get_parties(df)
