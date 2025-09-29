import json
import ollama

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
    return "\n".join(descriptions)


def find_founders(company: str, url: str, file_name: str):
    """
    Find the founders of a company from a given URL and text file, and save the results to a file.
    """
    descriptions = extract_descriptions_from_json(file_name)
    response = ollama.generate(model='gemma3:4b', prompt=f"Write a comma-separated list of the founders of {company} ({url}) using the following descriptions: {descriptions}")
    data = {
        company: [founder.strip() for founder in response['response'].split(',')]
    }
    with open('founders.json', 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    find_founders("Approval AI", "https://www.getapproval.ai/founders", "info.json")
