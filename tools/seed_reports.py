#!/usr/bin/env python3
"""Generate seed data for lost-bag reports (CSV).

Usage:
    python seed_reports.py                      # 1000 rows -> reports.csv
    python seed_reports.py -n 5000 -o seed.csv
    python seed_reports.py --broken-rate 0.1 --seed 7
"""
import argparse
import csv
import random

COLOURS = ["black", "navy", "blue", "red", "green", "grey", "silver", "brown",
           "pink", "orange", "purple", "white", "yellow", "teal", "beige",
           "charcoal", "olive", "maroon"]

# bag_form -> (brands, (min_kg, max_kg), has_shell)
FORMS = {
    "suitcase": (["Samsonite", "Tumi", "Away", "Rimowa", "American Tourister",
                  "Delsey", "Antler", "Briggs & Riley"], (10.0, 24.0), True),
    "backpack": (["Osprey", "The North Face", "Fjallraven", "Berghaus"], (4.0, 12.0), False),
    "duffel": (["Nike", "Adidas", "Longchamp"], (6.0, 18.0), False),
}

HEADER = ["report_id", "colour", "bag_form", "shell", "brand", "weight_kg"]


def valid_row(n, rng):
    form = rng.choice(list(FORMS))
    brands, (lo, hi), has_shell = FORMS[form]
    return {
        "report_id": f"R-{n}",
        "colour": rng.choice(COLOURS),
        "bag_form": form,
        "shell": rng.choice(["hard", "soft"]) if has_shell else "",
        # brand is genuinely optional in the sample data, so blanks are valid
        "brand": rng.choice(brands) if rng.random() > 0.15 else "",
        "weight_kg": f"{rng.uniform(lo, hi):.1f}",
    }


def break_row(row, rng, used_ids):
    """Corrupt one field in a way that mirrors the hand-made bad rows."""
    kind = rng.choice([
        "missing_id", "duplicate_id", "bad_id_format", "missing_colour",
        "bad_form", "bad_shell", "shell_on_backpack", "missing_weight",
        "negative_weight", "outlier_weight", "text_weight", "messy_case",
    ])
    if kind == "missing_id":
        row["report_id"] = ""
    elif kind == "duplicate_id" and used_ids:
        row["report_id"] = rng.choice(used_ids)
    elif kind == "bad_id_format":
        row["report_id"] = rng.choice(["1099", "RPT-12", "r_88", "R-"])
    elif kind == "missing_colour":
        row["colour"] = ""
    elif kind == "bad_form":
        row["bag_form"] = rng.choice(["banana", "box", "", "SUITCASE "])
    elif kind == "bad_shell":
        row["bag_form"] = "suitcase"
        row["shell"] = rng.choice(["", "medium", "HARD"])
    elif kind == "shell_on_backpack":
        row["bag_form"] = "backpack"
        row["shell"] = "hard"
    elif kind == "missing_weight":
        row["weight_kg"] = ""
    elif kind == "negative_weight":
        row["weight_kg"] = str(-rng.randint(1, 20))
    elif kind == "outlier_weight":
        row["weight_kg"] = str(rng.choice([400, 999, 150, 0]))
    elif kind == "text_weight":
        row["weight_kg"] = rng.choice(["heavy", "n/a", "12kg", "abc"])
    elif kind == "messy_case":
        row["colour"] = row["colour"].upper() + " "
    return kind


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-n", "--count", type=int, default=1000)
    p.add_argument("-o", "--out", default="reports.csv")
    p.add_argument("--broken-rate", type=float, default=0.05,
                   help="fraction of rows to corrupt (default 0.05)")
    p.add_argument("--seed", type=int, default=42,
                   help="RNG seed so runs are reproducible")
    p.add_argument("--start", type=int, default=1001, help="first report number")
    args = p.parse_args()

    rng = random.Random(args.seed)
    rows, used_ids, broken = [], [], 0

    for i in range(args.count):
        row = valid_row(args.start + i, rng)
        used_ids.append(row["report_id"])
        if rng.random() < args.broken_rate:
            break_row(row, rng, used_ids[:-1])
            broken += 1
        rows.append(row)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.out} ({broken} intentionally broken)")


if __name__ == "__main__":
    main()