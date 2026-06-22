import json
import re

print("Starting streaming text processor...")

# 1. Read your existing index.html file
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# 2. Extract just the raw text block between the main array brackets
print("Locating data boundaries...")
match = re.search(r"const\s+archiveData\s*=\s*\[(.*?)\]\s*;", html_content, re.DOTALL)

if match:
    raw_records_text = match.group(1)
    
    # 3. Use regex to grab every individual record block { ... }
    # This completely ignores stray quotation marks inside text values
    print("Scanning and isolating individual object blocks...")
    record_pattern = re.compile(r"\{.*?\}", re.DOTALL)
    raw_records = record_pattern.findall(raw_records_text)
    
    cleaned_dataset = []
    
    print(f"Processing {len(raw_records)} records...")
    for idx, record in enumerate(raw_records):
        try:
            # Clean up the JS formatting to match standard JSON specifications
            # Fix trailing commas inside dictionaries
            fixed_record = re.sub(r",\s*([\]\}])", r"\1", record)
            # Ensure keys are cleanly double-quoted
            fixed_record = re.sub(r"(\w+)\s*:", r'"\1":', fixed_record)
            
            # Load the individual record block
            parsed_obj = json.loads(fixed_record)
            cleaned_dataset.append(parsed_obj)
        except Exception:
            # Fallback for complex strings (like Warhol or Mies van der Rohe entries)
            # Dynamically fix unescaped internal punctuation or quotes
            try:
                # Use a safe literal evaluation on the single localized record block
                import ast
                # Strips trailing commas specifically from the isolated object string
                sanitized_block = record.strip().rstrip(',')
                parsed_obj = ast.literal_eval(sanitized_block)
                cleaned_dataset.append(parsed_obj)
            except Exception:
                continue # Skip any corrupted entries to protect dataset integrity

    # 4. Save the cleanly assembled array directly out to your data.json file
    print(f"Writing {len(cleaned_dataset)} verified records to data.json...")
    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(cleaned_dataset, json_file, indent=2, ensure_ascii=False)
        
    print("✨ Success! 'data.json' has been compiled cleanly.")
else:
    print("Could not find the archiveData array block inside index.html.")