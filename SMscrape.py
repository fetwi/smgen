import requests
from bs4 import BeautifulSoup
import os
import csv

dir_path = os.path.dirname(os.path.realpath(__file__))
template_file = os.path.join(dir_path, "smtemplate.html")
csv_file = os.path.join(dir_path, "smurls.csv")

def update_template():
    try:
        version = "2023-4"
        edate = "2023-04-01"
        lang = "en"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Read the smtemplate.html file
        with open(template_file, 'r', encoding='utf-8') as file:
            template = file.read()

        # Read the smurls.csv file
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                placeholder, url = row
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Check for request errors

                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                chapter_content = soup.find('div', id='ChapterContent')

                if chapter_content is None:
                    raise ValueError(f'ChapterContent div not found for URL: {url}')

                toc = str(chapter_content)

                # Replace the placeholder with the content
                template = template.replace(placeholder, toc)

        # Replace {version}, {edate}, and {lang} placeholders
        template = template.replace('{version}', version)
        template = template.replace('{edate}', edate)
        template = template.replace('{lang}', lang)

        # Save the updated content to a new file
        output_file_name = f'SM-{version}.html'
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(template)

        print(f'Template updated and saved as {output_file_name}')
    except Exception as e:
        print(f'Error updating template: {e}')

# Run the main function
if __name__ == '__main__':
    update_template()