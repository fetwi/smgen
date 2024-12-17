import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import csv
import re
import zipfile
from io import BytesIO

dir_path = os.path.dirname(os.path.realpath(__file__))

def update_template(lang, version, edate):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        if lang == 'en':
            template_file = os.path.join(dir_path, "smtemplate_en.html")
            csv_file = os.path.join(dir_path, "smurls_en.csv")            
            # Read the smtemplate.html file
            with open(template_file, 'r', encoding='utf-8') as file:
                template = file.read()
            # Read the smurls.csv file
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                for row in reader:
                    placeholder, url = row
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    # Parse the HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    chapter_content = soup.find('div', id='ChapterContent') or soup.find('div', id='smg-main')
                    if chapter_content is None:
                        raise ValueError(f'ChapterContent div not found for URL: {url}')
                    if placeholder == '{toc}':
                        # Remove the first <h3> tag
                        first_h3 = chapter_content.find('h3')
                        if first_h3:
                            first_h3.decompose()
                        last_a = chapter_content.find_all('a')[-1]
                        if last_a:
                            last_a.decompose()
                        last_h3 = chapter_content.find_all('h3')[-1]
                        if last_h3:
                            a_gl_tag = soup.new_tag('a', href='#gl')
                            a_gl_tag.string = '1 Supply Manual glossary'
                            last_h3.replace_with(a_gl_tag)
                        # Process remaining <h3> tags
                        for h3 in chapter_content.find_all('h3'):
                            strong_tag = h3.find('strong')
                            if strong_tag and len(strong_tag.text) >= 5:
                                href_second = strong_tag.text[9] if strong_tag.text[9].isdigit() else ''
                                href_value = strong_tag.text[8]
                                a_tag = soup.new_tag('a', href=f'#_{href_value}{href_second}')
                                a_tag.string = f'{href_value}{href_second} {h3.text}'
                                h3.replace_with(a_tag)
                        for tag in chapter_content.find_all(True):
                            if tag.name not in ['section', 'h3', 'strong', 'ul', 'li', 'a']:
                                tag.decompose()
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
                    if 'an' in placeholder or 'ch' in placeholder:
                        for tag in chapter_content.find_all(True):
                            if tag.name in ['script']:
                                tag.decompose()
                    if 'glo' in placeholder:
                        for p_tag in chapter_content.find_all('p'):
                            if p_tag.text.startswith('French:'):
                                p_tag.decompose()
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'glossa' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    if 'ch' in placeholder:
                        annex_tag = chapter_content.find('a', id='_Annexes') or chapter_content.find('h2', id='_annexes')
                        if annex_tag:
                            # Get the third and fourth characters of the placeholder
                            third_char = placeholder[3]
                            fourth_char = placeholder[4] if placeholder[4] != '}' else ''
                            new_id = f'an_{third_char}{fourth_char}'
                            annex_tag['id'] = new_id
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'annex' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    if 'an' in placeholder:
                        number = re.search(r'an(\d+)', placeholder).group(1)
                        for a in chapter_content.find_all('a', id=True):
                            a_id = a['id']
                            if 'ote_' in a_id:
                                # Remove everything before the #
                                a_id = f'an{number}{a_id}'
                                a['id'] = a_id
                            elif re.search(r'_\d', a_id):
                                # Remove everything before the #
                                a_id = f'an{a_id}'
                                a['id'] = a_id
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'annex' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if '#_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if 'Note_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = f'#an{number}Note_' + href[-1]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if 'note_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = f'#an{number}note_' + href[-1]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    chapter_content = chapter_content.decode_contents()
                    toc = str(chapter_content)

                    # Replace the placeholder with the content
                    template = template.replace(placeholder, toc)

            # Replace {version}, {edate}, and {lang} placeholders
            template = template.replace('{version}', version)
            template = template.replace('{edate}', edate)
            template = template.replace('{lang}', lang)

            # Save the updated content to a new file
            output_file_name = f'SM-{version}_{lang}.html'
            with open(output_file_name, 'w', encoding='utf-8') as file:
                file.write(template)
            print(f'Template updated and saved as {output_file_name}')

        if lang == 'fr':
            template_file = os.path.join(dir_path, "smtemplate_fr.html")
            csv_file = os.path.join(dir_path, "smurls_fr.csv")
            with open(template_file, 'r', encoding='utf-8') as file:
                template = file.read()
            # Read the smurls.csv file
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                for row in reader:
                    placeholder, url = row
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    # Parse the HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    chapter_content = soup.find('div', id='ChapterContent') or soup.find('div', id='smg-main')
                    if chapter_content is None:
                        raise ValueError(f'ChapterContent div not found for URL: {url}')
                    if placeholder == '{toc}':
                        # Remove the first <h3> tag
                        first_h3 = chapter_content.find('h3')
                        if first_h3:
                            first_h3.decompose()
                        last_a = chapter_content.find_all('a')[-1]
                        if last_a:
                            last_a.decompose()
                        last_h3 = chapter_content.find_all('h3')[-1]
                        if last_h3:
                            a_gl_tag = soup.new_tag('a', href='#gl')
                            a_gl_tag.string = '1 Glossaire du Guide des approvisionnements'
                            last_h3.replace_with(a_gl_tag)
                        # Process remaining <h3> tags
                        for h3 in chapter_content.find_all('h3'):
                            strong_tag = h3.find('strong')
                            if strong_tag and len(strong_tag.text) >= 5:
                                href_second = strong_tag.text[10] if strong_tag.text[10].isdigit() else ''
                                href_value = strong_tag.text[9]
                                a_tag = soup.new_tag('a', href=f'#_{href_value}{href_second}')
                                a_tag.string = f'{href_value}{href_second} {h3.text}'
                                h3.replace_with(a_tag)
                        for tag in chapter_content.find_all(True):
                            if tag.name not in ['section', 'h3', 'strong', 'ul', 'li', 'a']:
                                tag.decompose()
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

                    if 'an' in placeholder or 'ch' in placeholder:
                        for tag in chapter_content.find_all(True):
                            if tag.name in ['script']:
                                tag.decompose()
                    if 'glo' in placeholder:
                        for p_tag in chapter_content.find_all('p'):
                            if p_tag.text.startswith('Anglais'):
                                p_tag.decompose()
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'glossa' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    if 'ch' in placeholder:
                        annex_tag = chapter_content.find('a', id='_Annexes') or chapter_content.find('h2', id='_annexes')
                        if annex_tag:
                            # Get the third and fourth characters of the placeholder
                            third_char = placeholder[3]
                            fourth_char = placeholder[4] if placeholder[4] != '}' else ''
                            new_id = f'an_{third_char}{fourth_char}'
                            annex_tag['id'] = new_id
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'annex' in href or '964950' in href: # 964950 is a fix for french chapter 9 node urls
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    if 'an' in placeholder:
                        number = re.search(r'an(\d+)', placeholder).group(1)
                        for a in chapter_content.find_all('a', id=True):
                            a_id = a['id']
                            if 'emarque_' in a_id:
                                # Remove everything before the #
                                a_id = f'an{number}{a_id}'
                                a['id'] = a_id
                            elif re.search(r'_\d', a_id):
                                # Remove everything before the #
                                a_id = f'an{a_id}'
                                a['id'] = a_id
                        for a in chapter_content.find_all('a', href=True):
                            href = a['href']
                            if 'annex' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if '#_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = '#an' + href[1:]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if 'Remarque_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = f'#an{number}Remarque_' + href[-1]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                            if 'remarque_' in href:
                                # Check if '#' is in href before using index()
                                if '#' in href:
                                    # Remove everything before the #
                                    href = href[href.index('#'):]
                                    href = f'#an{number}remarque_' + href[-1]
                                    a['href'] = href
                                else:
                                    # Handle the case where '#' is not found in href
                                    print(f"Warning: '#' not found in href: {href}")
                    chapter_content = chapter_content.decode_contents()
                    toc = str(chapter_content)

                    # Replace the placeholder with the content
                    template = template.replace(placeholder, toc)

            # Replace {version}, {edate}, and {lang} placeholders
            template = template.replace('{version}', version)
            template = template.replace('{edate}', edate)
            template = template.replace('{lang}', lang)

        output_file_name = f'SM-{version}_{lang}.html'
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(template)

        return output_file_name
    except Exception as e:
        st.error(f'Error updating template: {e}')
        return None

# Streamlit app
st.title('SM Template Updater')

lang = st.selectbox('Select Language', ['en', 'fr'])
version = st.text_input('Enter Version (yyyy-m)', '2024-7')
edate = st.text_input('Enter Effective Date (yyyy-mm-dd)', '2024-11-08')

if st.button('Update Template'):
    output_file_name = update_template(lang, version, edate)
    if output_file_name:
        # Create a zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(output_file_name, os.path.basename(output_file_name))
        zip_buffer.seek(0)

        # Provide a download link for the zip file
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name=f'SM-{version}_{lang}.zip',
            mime='application/zip'
        )