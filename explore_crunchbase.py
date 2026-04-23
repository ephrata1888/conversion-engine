import csv

with open("data/crunchbase_sample.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    print("Columns:")
    for h in headers:
        print(f"  {h}")
    
    print("\nFirst 3 rows:")
    for i, row in enumerate(reader):
        if i >= 3:
            break
        print(f"\nCompany {i+1}:")
        for k, v in row.items():
            if v:
                print(f"  {k}: {v}")
