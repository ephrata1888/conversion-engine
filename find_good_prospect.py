import csv
import json

with open("data/crunchbase_sample.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        # Look for US/CA companies with funding and employees
        if (row.get("country_code") in ["US", "CA"] and 
            row.get("funding_rounds_list", "[]") not in ["[]", "", "null"] and
            row.get("num_employees") in ["11-50", "51-100", "101-250"]):
            
            funding = json.loads(row["funding_rounds_list"])
            if len(funding) > 0:
                print(f"Name: {row['name']}")
                print(f"Employees: {row['num_employees']}")
                print(f"Industries: {row.get('industries', '')[:80]}")
                print(f"Funding rounds: {len(funding)}")
                print(f"Latest round: {funding[-1].get('announced_on', 'unknown')}")
                print()
                count += 1
                if count >= 5:
                    break