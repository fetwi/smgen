import requests
from bs4 import BeautifulSoup
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
template_file = os.path.join(dir_path, "smtemplate.html")

#def prompt_version():
#   return input('Enter the version (yyyy-m): ')
#def prompt_edate():
#   return input('Enter the effective date (yyyy-mm-dd): ')

# Main function to update the template
def update_template():
    try:
       #version = prompt_version()
       #edate = prompt_date()
        version = "2023-4"
        edate = "2023-04-01"
        lang = "en"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Fetch the HTML content from the URL
        tocurl = 'https://canadabuys.canada.ca/en/how-procurement-works/policies-and-guidelines/supply-manual'
        response = requests.get(tocurl, headers=headers)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        toc_content = soup.find('div', id='ChapterContent')

        if toc_content is None:
            raise ValueError('ChapterContent div not found')

        # Remove all tags that are not <ul>, <li>, or <a>
        if placeholder == '{toc}':
            for tag in toc_content.find_all(True):  # True finds all tags
                if tag.name not in ['section', 'ul', 'li', 'a']:
                    tag.decompose()  # Remove the tag

        # Modify href attributes in <a> tags within toc_content
        for a in toc_content.find_all('a', href=True):
            href = a['href']
            if '#' in href:
                # Remove everything before the #
                href = href[href.index('#'):]
                a['href'] = href

        toc = str(toc_content)

        # Read the smtemplate.html file
        with open(template_file, 'r', encoding='utf-8') as file:
            template = file.read()

        # Replace {tableofcontents} and {version} placeholders
        template = template.replace('{toc}', toc)
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