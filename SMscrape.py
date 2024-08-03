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

                # Remove all tags that are not <ul>, <li>, or <a>
                if placeholder == '{toc}':
                    # Remove the first <h3> tag
                    first_h3 = chapter_content.find('h3')
                    if first_h3:
                        first_h3.decompose()
                    last_a = chapter_content.find_all('a')[-1]
                    if last_a:
                        last_a.decompose()
                
                    # Process remaining <h3> tags
                    for h3 in chapter_content.find_all('h3'):
                        strong_tag = h3.find('strong')
                        if strong_tag and len(strong_tag.text) >= 5:
                            href_second = strong_tag.text[9] if strong_tag.text[9].isdigit() else ''
                            href_value = strong_tag.text[8]
                            a_tag = soup.new_tag('a', href=f'#_{href_value}{href_second}')
                            a_tag.string = f'{href_value}{href_second} {h3.text}'
                            h3.replace_with(a_tag)

                    for tag in chapter_content.find_all(True):  # True finds all tags
                        if tag.name not in ['section', 'h3', 'strong', 'ul', 'li', 'a']:
                            tag.decompose()  # Remove the tag
                
                    # Replace all <section> tags with <li> tags
                    for section in chapter_content.find_all('section'):
                        li_tag = soup.new_tag('li')
                        li_tag.extend(section.contents)
                        section.replace_with(li_tag)
                
                    # Modify href attributes in <a> tags within chapter_content
                    for a in chapter_content.find_all('a', href=True):
                        href = a['href']
                        if '#' in href:
                            # Remove everything before the #
                            href = href[href.index('#'):]
                            a['href'] = href
                        if 'annex' in href:
                            a_content = a.text
                            an_chap = a_content[-2:] if len(a_content) == 22 else a_content[-1]
                            href = f'#an_{an_chap}'
                            a['href'] = href

                    chapter_content = chapter_content.decode_contents()

                if 'an' in placeholder or 'ch' in placeholder:
                    for tag in chapter_content.find_all(True):  # True finds all tags
                        if tag.name in ['script']:
                            tag.decompose()  # Remove the tag

                if 'ch' in placeholder:
                    # Find the <a> tag with id "_Annexes" and modify its id
                    annex_tag = chapter_content.find('a', id='_Annexes')
                    if annex_tag:
                        # Get the third and fourth characters of the placeholder
                        third_char = placeholder[3]
                        fourth_char = placeholder[4] if placeholder[4] != '}' else ''
                        new_id = f'an_{third_char}{fourth_char}'
                        annex_tag['id'] = new_id
                    for a in chapter_content.find_all('a', href=True):
                        href = a['href']
                        if 'annex' in href:
                            # Remove everything before the #
                            href = href[href.index('#'):]
                            href = '#an' + href[1:]
                            a['href'] = href

                if 'an' in placeholder:
                    for a in chapter_content.find_all('a', id=True):
                        a_id = a['id']
                        if '_' in a_id:
                            # Remove everything before the #
                            a_id = f'an{a_id}'
                            a['id'] = a_id
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