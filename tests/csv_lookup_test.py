"""Ad-hoc smoke test: look up a coin name inside a CSV file."""
import csv

csv_coin_name = "MetaBUSDCoin"

with open('test.csv', 'rt') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        for field in row:
            if field == csv_coin_name:
                print("found:", csv_coin_name)
