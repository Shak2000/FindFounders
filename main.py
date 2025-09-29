import json
import ollama
import requests

from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

def extract_descriptions_from_json(file_path):
    """
    Loads JSON data from a file, extracts all 'og:description' values 
    from the 'metatags' within 'items', and returns them concatenated
    by newline characters.
    """
    descriptions = []
    
    # Open and load the JSON data from the specified file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON from '{file_path}'."
    
    # Iterate through the list of search results ('items')
    for item in data.get('items', []):
        
        # Navigate to the 'pagemap' and then to 'metatags'
        pagemap = item.get('pagemap')
        if pagemap:
            metatags_list = pagemap.get('metatags')
            
            # 'metatags' is a list of dictionaries, so iterate through it
            if isinstance(metatags_list, list):
                for tag in metatags_list:
                    
                    # Extract the value for 'og:description'
                    description = tag.get('og:description')
                    if description:
                        descriptions.append(description)

    # Concatenate all extracted strings with a newline character "\n"
    desc = "\n".join(descriptions)
    print(desc)
    return desc


def find_founders(company: str, file_name: str):
    """
    Find the founders of a company from a given URL and text file, and return a list of founder names.
    """
    descriptions = extract_descriptions_from_json(file_name)
    response = ollama.generate(model='gemma3:4b', prompt=f"Write a comma-separated list of the founders of {company} using the following descriptions: {descriptions}")
    founders = [founder.strip() for founder in response['response'].split(',')]
    return founders


def search_companies(file_name: str):
    """
    Search for the founders of the companies in the text file.
    Opens the text file, extracts each line (company + URL), uses Google Custom Search API
    to search for "{LINE} founders", saves results to info.json, calls find_founders,
    and assembles all results into founders.json.
    """
    all_founders = {}
    
    # Read companies from the text file
    try:
        with open(file_name, 'r') as f:
            companies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return
    
    for company_line in companies:
        if not company_line:
            continue
            
        print(f"Processing: {company_line}")
        
        # Create search query
        search_query = f"{company_line} founders"
        
        # Use Google Custom Search API
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': search_query,
            'num': 10  # Number of results to return
        }
        
        try:
            # Make API request
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            # Save results to info.json
            with open('info.json', 'w') as f:
                json.dump(search_results, f, indent=2)
            
            # Extract company name (remove URL part)
            company_name = company_line.split(' (')[0] if ' (' in company_line else company_line
            
            # Call find_founders to get the list of founders
            founders = find_founders(company_line, 'info.json')
            
            # Add to results dictionary
            all_founders[company_name] = founders
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for {company_line}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {company_line}: {e}")
            continue
    
    # Save all results to founders.json
    with open('founders.json', 'w') as f:
        json.dump(all_founders, f, indent=2)
    
    print(f"Completed processing. Results saved to founders.json")
    return all_founders


if __name__ == "__main__":
    # Process all companies in the companies.txt file
    search_companies("companies.txt")
