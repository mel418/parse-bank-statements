import pandas as pd
import pdfplumber
import re

# Define categories and keywords
def categorize_transaction(description):
    categories = {
        "Food & Beverage": ["ElPolloLoco", "BB.Q", "Hawaiian BBQ", "Meet Fresh", "Donut", "Boba", "Tea", "Cafe", "McDonalds", "Robeks"],
        "Shopping": ["Amazon", "Miniso", "Pop Mart", "Top Canvas", "Bunker"],
        "Target": ["Target"],
        "Transportation": ["Chevron", "Gas", "ATM"],
        "Utilities & Bills": ["Internet", "Payment", "Recurring"],
        "Entertainment": ["Venmo", "Paypal", "Universal", "Three Broomsticks", "Butterbeer"],
        "Savings & Transfers": ["Deposit", "Dividend", "Transfer"],
        "Other": []
    }
    
    for category, keywords in categories.items():
        if any(keyword.lower() in description.lower() for keyword in keywords):
            return category
    return "Other"

# Parse Discover CSV
def parse_discover_csv(file_path):
    df = pd.read_csv(file_path)
    df['Category'] = df['Description'].apply(categorize_transaction)
    return df

# Parse Orange County Credit Union PDF
def parse_occ_pdf(file_path):
    transactions = []
    date_pattern = re.compile(r"\d{2}/\d{2}/\d{2}")  # Matches dates in MM/DD/YY format
    pacific_checking = False  # Track if we're in the "Pacific Checking" section

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    # Debug: Check raw lines
                    print(f"Raw line: {line}")

                    if "PACIFICCHECKING #0040" in line.replace(" ", "").upper():
                        pacific_checking = True  # Start parsing transactions
                        print("Detected start of Pacific Checking #0040 section.")
                    elif "PACIFICSAVINGS" in line.replace(" ", "").upper():
                        pacific_checking = False  # End parsing transactions
                        print("Exited Pacific Checking #0040 section.")

                    if pacific_checking and date_pattern.search(line):
                        parts = re.split(r'\s{2,}', line.strip())  # Split by 2 or more spaces
                        print(f"Parsing line: {parts}")  # Debug: Check how the line is split
                        
                        if len(parts) >= 3:
                            date = parts[0]
                            description = " ".join(parts[1:-1])
                            amount = parts[-1]
                            
                            # Validate and clean data
                            if re.match(r"^-?\d+(\.\d{2})?$", amount):  # Check if amount is valid
                                category = categorize_transaction(description)
                                transactions.append({
                                    "Date": date,
                                    "Description": description,
                                    "Amount": amount,
                                    "Category": category
                                })
    print("Parsed transactions:", transactions)  # Debug: Show parsed transactions
    return pd.DataFrame(transactions)

# Main script
def main():
    # File paths
    discover_file = "Discover-Statement-20240924.csv"
    occ_file = "download(1).pdf"

    # Parse files
    discover_df = parse_discover_csv(discover_file)
    occ_df = parse_occ_pdf(occ_file)

    # Save separate files
    discover_df.to_csv("discover_transactions.csv", index=False)
    occ_df.to_csv("occ_transactions.csv", index=False)
    print("Discover transactions saved to discover_transactions.csv")
    print("Orange County Credit Union transactions saved to occ_transactions.csv")

if __name__ == "__main__":
    main()
