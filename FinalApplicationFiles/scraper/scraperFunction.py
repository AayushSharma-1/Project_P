import requests
import os
import re
import string
from bs4 import BeautifulSoup

"""
this htmlFilesCreator function creates HTML files for the given month and year.
The function takes two arguments: month and year.
The function sends a POST request to the PIB website to get the HTML content for the given month and year.
The function then extracts the relevant HTML content and saves it in a file named as the month and year.


"""

def htmlFilesCreator(month, year):
    import requests
    from bs4 import BeautifulSoup

    calendar = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    
# Set up session and headers
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "Origin": "https://pib.gov.in",
        "Referer": "https://pib.gov.in/allRel.aspx?reg=3&lang=1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
    }

    # Initial GET request to get ViewState and validation fields
    url = "https://pib.gov.in/allRel.aspx"
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
    event_validation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
    viewstate_generator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
    
    
    payload = {
    "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlday",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewstate_generator,
    "__VIEWSTATEENCRYPTED": "",
    "__EVENTVALIDATION": event_validation,
    "ctl00$Bar1$ddlregion": "3",  # Region code
    "ctl00$Bar1$ddlLang": "1",    # Language code
    "ctl00$ContentPlaceHolder1$hydregionid": "3",
    "ctl00$ContentPlaceHolder1$hydLangid": "1",
    "ctl00$ContentPlaceHolder1$ddlMinistry": "0",  # 0 = All Ministry
    "ctl00$ContentPlaceHolder1$ddlday": "0",       # 0 = All Days
    "ctl00$ContentPlaceHolder1$ddlMonth": month,     # 1 = January
    "ctl00$ContentPlaceHolder1$ddlYear": year,   # Selected year
}

# Add cookies from your request
    cookies = {
        "PIB_Accessibility": "Lang=1&Region=3",
        "style": "null",
        "_ga": "GA1.1.2099942994.1738260074",
    }

    # Make the POST request
    response = session.post(
        url,
        headers=headers,
        data=payload,
        cookies=cookies
    )

    
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    relevant_soup = soup.find('div', class_ = 'content-area')
   
    directory = f'HTML{str(year)[2:]}' # Takes last 2 digits of year (e.g., 24 for 2024)
    directory = os.path.join('ScraperFiles', directory)
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save file in the year-specific directory
    file_path = os.path.join(directory, f'{calendar[month]}{str(year)[2:]}.html')
    
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(str(relevant_soup))
    print("HTML file created successfully!")    


"""
This function extracts the data from the HTML files and returns it in a dictionary format.
"""
def dataExtractor(path):
    names = os.listdir(path)
    allData = {}
    for nam in names:
        with open(os.path.join(path, nam), encoding='utf-8') as f:
            rawData = f.read()
        
        soup = BeautifulSoup(rawData, 'html.parser')
        l = [loc.text.strip() for loc in soup.find_all('h3', class_ = 'font104')]
        data = {}

        for i,j in zip(range(len(l)), l):
            names = []
            links = []
            for k in (soup.find_all('ul', class_ = 'leftul')[i].find_all('li')):
                names.append(k.text.strip())
            # print(names)

            for k in soup.find_all('ul', class_ = 'leftul')[i].find_all('li'):
                links.append('https://pib.gov.in/' + k.find('a').attrs['href'])
            # print(links)    
            data[j] = (names, links)
        allData[nam] = data
    return allData



"""
This is the format of the dictionary that is returned by the dataExtractor function: 

{"month":{"ministry1":([heading 1, heading2, ...], [link1, link2, ...]),
            "ministry2":([heading 1, heading2, ...], [link1, link2, ...]),
            ......},

"month":{"ministry1":([heading 1, heading2, ...], [link1, link2, ...]),
            "ministry2":([heading 1, heading2, ...], [link1, link2, ...]),
            },
......}            

"""




"""
This function cleans the text by removing HTML tags, punctuation marks, and extra spaces.
"""

def clean_text(text):
    # Remove HTML tags using regex
    html_tag_pattern = re.compile(r'<[^>]+>')
    text = re.sub(html_tag_pattern, '', text)

    # Remove punctuation marks
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Replace multiple spaces with a single underscore
    text = re.sub(r'\s+', '_', text.strip())
    
    # Truncate text to a maximum length of 40 characters
    if len(text) > 40:
        text = text[:40]
    
    return text

"""
This function creates text files for each heading in the data dictionary.
"""

def textFilesCreator(data):
    months = data.keys()
    for i in months: #If you want to customize the months, you can use list slicing here
        types = data[i].keys()
        for j in types:
            path = os.path.join(clean_text(i), clean_text(j)) # Here Clean Text function is used to remove special characters from the folder name
            os.makedirs(path, exist_ok=True)  # Avoid error if directory already exists
            
            for k in range(len(data[i][j][0])): # k= 0
                heading = data[i][j][0][k]
                link = data[i][j][1][k]
                linkRes = requests.get(link)
                
                if linkRes.status_code == 200:
                    linkSoup = BeautifulSoup(linkRes.content, 'html.parser')
                    s = ''
                    
                    for l in linkSoup.find_all('h2'):
                        s += l.text.strip() + '\n'
                        
                    for m in linkSoup.find_all('h3'):
                        s += m.text.strip() + '\n'
                        
                    n = len(linkSoup.find_all('p')) // 2

                    for o in linkSoup.find_all('p')[:n]:
                        s += o.text.strip() + '\n'

                    # Create the file and write the content
                    file_path = os.path.join(path, f"{clean_text(heading)}.txt")
                    with open(file_path, 'w+', encoding='utf-8') as f:
                        f.write(s)

# if __name__ == "__main__":
    # path = 'specify the path of html files here'
    # data = dataExtractor(path)
    # textFilesCreator(data)
    # print("Text files created successfully!")
    # month = int(input("Enter the number of month: "))
    # year = int(input("Enter the year: "))
    # htmlFilesCreator(month, year)