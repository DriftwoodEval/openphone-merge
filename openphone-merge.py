# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
# ]
# ///

import argparse

import pandas as pd


def open_sheet(file):
    with open(file, "r", errors="ignore") as f:
        df = pd.read_csv(f, dtype=str)
        return df


def filter_by_status(df):
    return df[df.STATUS != "Inactive"]


def normalize_names(df):
    for col in ["LASTNAME", "FIRSTNAME", "PREFERRED_NAME"]:
        df[col] = df[col].str.title().replace({"Iii": "III", "Ii": "II"}, regex=True)
    return df


def remove_test_names(df):
    test_names = [
        "Testman Testson",
        "Testman Testson Jr.",
        "Johnny Smonny",
        "Johnny Smonathan",
        "Test Mctest",
    ]
    return df[
        ~((df.FIRSTNAME + " " + df.LASTNAME).isin(test_names))
        & ~df.FIRSTNAME.isin(test_names)
        & ~df.LASTNAME.isin(test_names)
    ]


def prune_columns(df):
    df = df[["LASTNAME", "FIRSTNAME", "PHONE1"]]
    return df


def use_preferred_name(df):
    df["FIRSTNAME"] = df.apply(
        lambda row: row.PREFERRED_NAME
        if pd.notna(row.PREFERRED_NAME)
        else row.FIRSTNAME,
        axis=1,
    )
    return df


def remove_duplicates(ta_df, op_df):
    for index, row in ta_df.iterrows():
        phone_digits = "".join(filter(str.isdigit, str(row.PHONE1)))
        phone_with_code = "1" + phone_digits
        if (
            phone_digits
            in op_df.phone_number_1.str.replace(r"\D", "", regex=True).values
            or phone_with_code
            in op_df.phone_number_1.str.replace(r"\D", "", regex=True).values
        ):
            ta_df.drop(index, inplace=True)
    return ta_df


def reorganize(df):
    df.rename(columns={"PHONE1": "PHONE_NUMBER"}, inplace=True)
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--demo", type=str, default="demographic.csv")
    parser.add_argument("-o", "--openphone", type=str, default="openphone.csv")
    args = parser.parse_args()

    demo = open_sheet(args.demo)
    openphone = open_sheet(args.openphone)

    demo = filter_by_status(demo)
    demo = normalize_names(demo)
    demo = use_preferred_name(demo)
    demo = remove_test_names(demo)
    demo = prune_columns(demo)
    demo = remove_duplicates(demo, openphone)
    demo = reorganize(demo)

    demo.to_csv("openphone-merged.csv", index=False)


if __name__ == "__main__":
    main()
