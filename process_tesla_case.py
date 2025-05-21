import json
import nltk
import re

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab') # Add check for punkt_tab
except LookupError:
    print("NLTK 'punkt' or 'punkt_tab' resource not found. Downloading...")
    nltk.download('punkt', quiet=False)
    nltk.download('punkt_tab', quiet=False) # Add download for punkt_tab
    print("'punkt' and 'punkt_tab' downloaded.")

from nltk.tokenize import sent_tokenize

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def clean_text(text):
    # Remove page numbers and headers/footers that might interfere with sentence tokenization
    text = re.sub(r"--- PAGE \d+ ---", "", text)
    text = re.sub(r"Authorized for use only in the course SGMA 591 L01 at University of Calgary taught by PENGFEI LI from 5/5/2025 to 6/17/2025\. Use outside these parameters is a copyright violation\.", "", text)
    text = re.sub(r"\d+\s+714-413\s+Tesla Motors", "", text)
    text = re.sub(r"Tesla Motors\s+714-413", "", text)
    text = re.sub(r"Exhibit \d+[A-Za-z]?\s+.*", "", text) # Remove Exhibit titles for now, will handle them separately
    text = re.sub(r"Source:.*", "", text) # Remove source lines
    text = re.sub(r"\s*\n\s*", "\n", text) # Normalize multiple newlines
    text = re.sub(r"\[cite:\d+\]", "", text) # Remove citation markers
    return text.strip()

def tag_excerpts(text):
    sentences = sent_tokenize(text)
    tagged_excerpts = []

    categories_keywords = {
        "Financials": [
            "income", "sales", "stock", "cost", "price", "billion", "million", "profitable", 
            "revenue", "market cap", "financials", "capital", "assets", "expenses", "profit", "loss", "WACC",
            "equity", "debt", "financing", "investment", "valuation", "earnings", "cash flow"
        ],
        "Technology": [
            "battery", "powertrain", "electric motor", "charging", "Supercharger", "software update", 
            "touchscreen", "Li-Ion", "18650 form factor", "energy density", "motor", "engine", 
            "transmission", "chassis", "design", "manufacturing", "assembly plant", "robotic",
            "stamping press", "injection molding", "panoramic roof", "cellular connection", "fob"
        ],
        "Competition": [
            "Nissan", "GM", "BMW", "Audi", "Ford", "Fisker", "Leaf", "Volt", "competitors", 
            "outsold", "market share", "rival", "Toyota", "Mercedes", "Porsche", "Coda"
        ],
        "Strategy": [
            "mass manufacturer", "Model S", "Model X", "Roadster", "Gen 3", "dealerships", 
            "stores", "service", "Supercharger network", "battery swapping", "drivetrains", 
            "master plan", "affordable car", "direct-to-consumer sales", "reservations", 
            "sales target", "high-end", "market segment", "expansion", "production capacity",
            "in-house", "outsourced", "vertically integrated", "Silicon Valley roots"
        ],
        "Risks": [
            "controversy", "bankrupt", "halted production", "range anxiety", "longevity", 
            "resale value", "safety", "hurdles", "conflict with dealership lobby", 
            "cost disadvantage", "lack of experience", "delays", "dwindling capital", 
            "uncertainty", "challenges", "issues", "problems", "overcapacity", "warranty"
        ]
    }

    # Max 20 excerpts per category to keep it manageable, aiming for 5-10 good ones
    category_counts = {cat: 0 for cat in categories_keywords}
    max_excerpts_per_category = 15 

    for sentence in sentences:
        # Basic cleaning for individual sentences
        sentence_clean = sentence.replace('\n', ' ').strip()
        if not sentence_clean or len(sentence_clean.split()) < 5: # Skip very short sentences
            continue

        matched_categories = []
        for category, keywords in categories_keywords.items():
            if category_counts[category] < max_excerpts_per_category:
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', sentence_clean, re.IGNORECASE):
                        tagged_excerpts.append({"category": category, "excerpt": sentence_clean})
                        category_counts[category] += 1
                        matched_categories.append(category)
                        break # Match first keyword, then move to next category to avoid duplicate entries for same sentence under same category.
            # If a sentence matches multiple categories, allow it, but only once per category.
            # This will be handled by the break and the main loop continuing.
            # For now, let's keep it simple: one sentence, one primary category match (first one found)
            # Or, allow multiple categories if keywords from different categories appear. The current structure allows this.

    # Manual additions from Exhibits (simplified examples)
    # This part needs careful manual crafting based on the actual content of exhibits.
    # For this exercise, I'll add a few representative examples based on exhibit descriptions.
    
    # Financials from Exhibits
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Exhibit 1: Estimated Cost Structure for a $25,000 IC Car shows materials and parts make up 50% of the car price."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Exhibit 2: Typical Revenue and Cost Structure of U.S. Dealer indicates new-vehicle sales are 56% of sales but service is 44% of gross margin."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Exhibit 12: Income Statement Tesla Motors (in US$ thousand) for H1 2013 shows Revenues of $966,931 and Gross profit of $196,803."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Exhibit 13: Assets on Balance Sheet Tesla Motors (in US$ thousand) as of Jun-13 shows Total assets of $1,887,844."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Exhibit 14: Income Statement and Invested Capital BMW Group, excluding financial services (in million Euros) for 2012 shows Revenues of 57,293 million Euros."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "Tesla raised its Model S sales target for its first full year from 20,000 to 21,000 cars."})
        category_counts["Financials"] +=1
    if category_counts["Financials"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Financials", "excerpt": "On May 8, Tesla announced a net income of more than $10mln on $560 mln in sales."})
        category_counts["Financials"] +=1


    # Technology from Exhibits
    if category_counts["Technology"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Technology", "excerpt": "Exhibit 3 visually compares the powertrain of a Conventional Internal Combustion Engine and Tesla Model S, highlighting the EV's relative simplicity."})
        category_counts["Technology"] +=1
    if category_counts["Technology"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Technology", "excerpt": "Exhibit 4: Lithium-Ion Battery Market indicates automotive usage share was 14% in 2012 and projected to be 25% in 2016."})
        category_counts["Technology"] +=1
    if category_counts["Technology"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Technology", "excerpt": "Exhibit 5: Cost Structure of Newly Developed Li-Ion Battery of 24KWh shows Variable Cost at $500/KWh and Fixed Cost at $700/KWh."})
        category_counts["Technology"] +=1
    if category_counts["Technology"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Technology", "excerpt": "Tesla's 85kWh battery, for example, consisted of more than 7,000 cells in the 18650 form factor."})
        category_counts["Technology"] +=1
    if category_counts["Technology"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Technology", "excerpt": "The car also had a 17\" touchscreen in the middle console to control almost all its functions, from air conditioning and lights to entertainment system."})
        category_counts["Technology"] +=1


    # Competition from Exhibits
    if category_counts["Competition"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Competition", "excerpt": "Exhibit 9: Comparison of Tesla Model S, Nissan Leaf, and BMW 528i shows Model S MSRP $61,070, Leaf $19,650, BMW 528i $48,725."})
        category_counts["Competition"] +=1
    if category_counts["Competition"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Competition", "excerpt": "Its Model S had sold more than the BMW 7 and Audi A8 combined."})
        category_counts["Competition"] +=1
    if category_counts["Competition"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Competition", "excerpt": "While some of its most visible EV competitors went bankrupt or halted production, Tesla became profitable."})
        category_counts["Competition"] +=1


    # Strategy from text (already covered by keywords, but can add specific important ones)
    if category_counts["Strategy"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Strategy", "excerpt": "Elon Musk wanted Tesla to be a mass manufacturer of electric cars."})
        category_counts["Strategy"] +=1
    if category_counts["Strategy"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Strategy", "excerpt": "In a blog post titled \"The Secret Tesla Motors Master Plan (just between you and me),\" he stated that the plan was to \"[b]uild sports car, [u]se that money to build an affordable car, [u]se that money to build an even more affordable car.\""})
        category_counts["Strategy"] +=1
    if category_counts["Strategy"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Strategy", "excerpt": "Instead of independent dealerships like other car manufacturers, Tesla built a network of company-owned stores with salespeople on salary rather than on commission."})
        category_counts["Strategy"] +=1

    # Risks from text
    if category_counts["Risks"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Risks", "excerpt": "The second were different sources of \"range anxiety,\" which included the limited range of most EVs, the time it took to charge a car, and the early lack of charging stations."})
        category_counts["Risks"] +=1
    if category_counts["Risks"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Risks", "excerpt": "This approach put Tesla in conflict with the dealership lobby, which had pushed many states to pass laws requiring car companies to sell through independent dealerships recognized by the dealership association."})
        category_counts["Risks"] +=1
    if category_counts["Risks"] < max_excerpts_per_category:
        tagged_excerpts.append({"category": "Risks", "excerpt": "Analysts worried that this might put Tesla at a cost disadvantage."})
        category_counts["Risks"] +=1
        
    # Remove duplicates that might have been added by both keyword search and manual addition
    unique_excerpts = []
    seen_excerpts_text = set()
    for excerpt_obj in tagged_excerpts:
        if excerpt_obj["excerpt"] not in seen_excerpts_text:
            unique_excerpts.append(excerpt_obj)
            seen_excerpts_text.add(excerpt_obj["excerpt"])
            
    return unique_excerpts

def main():
    input_filepath = "tesla source case.txt"
    output_filepath = "output/annotated.json"

    text_content = read_file(input_filepath)
    cleaned_text = clean_text(text_content)
    
    # Further split by paragraphs to handle context better, then tokenize sentences
    # For simplicity here, we're tokenizing the whole cleaned text.
    # A more advanced approach might segment by paragraph first.
    
    annotated_data = tag_excerpts(cleaned_text)

    # Add some specific exhibit data manually if keyword search is insufficient
    # This part is simplified for now. A robust solution would parse exhibits more directly.

    # Example of adding a very specific financial data point from an exhibit table if not caught
    # This should ideally be integrated into a more systematic exhibit parsing logic
    # For now, we rely on the keyword search and the manual additions in tag_excerpts

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(annotated_data, f, indent=2, ensure_ascii=False)

    print(f"Annotated data saved to {output_filepath}")
    
    # Print summary
    category_summary = {}
    for item in annotated_data:
        cat = item["category"]
        category_summary[cat] = category_summary.get(cat, 0) + 1
    
    print("\nNumber of annotations per category:")
    for category, count in category_summary.items():
        print(f"- {category}: {count}")

if __name__ == "__main__":
    main()
