import requests


def get_solubility(cid):
  url = f'https://nih.gov{cid}/JSON'
  response = requests.get(url)

  if response.status_code != 200:
    return 'Error fetching data'

  data = response.json()

  # Safely drill down into the deep nested JSON structure
  try:
    sections = data['Record']['Section']
    for section in sections:
      if section.get('TOCHeading') == 'Chemical and Physical Properties':
        for sub in section.get('Section', []):
          if sub.get('TOCHeading') == 'Experimental Properties':
            for prop in sub.get('Section', []):
              if prop.get('TOCHeading') == 'Solubility':
                # Return the string descriptions of solubility found
                return [
                    info['Value']['StringWithMarkup'][0]['String']
                    for info in prop.get('Information', [])
                    if 'StringWithMarkup' in info.get('Value', {})
                ]
  except KeyError:
    pass

  return 'Solubility data not found'


# Example: Get solubility for Caffeine (CID 2519)
print(get_solubility(2519))