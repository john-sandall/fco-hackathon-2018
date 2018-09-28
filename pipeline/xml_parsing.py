from bs4 import BeautifulSoup
import json

with open('data/british-diplomats-directory.xml', 'r') as f:
    doc = BeautifulSoup(f.read(), 'lxml')


body = doc.find('body')
sections = [section for section in body.find_all('div', {'type': 'section'}) if section.has_attr('xml:id')]
section_a = sections[0]

# SECTION A: ALPHABETICAL LISTING OF DIPLOMATS 1820-2005
data = []
letters = [section for section in section_a.find_all('div') if section.has_attr('xml:id')]
for letter in letters:
    for entry in list(letter.find_all('entry')):
        entry_data = {}
        persname = entry.find('persname')
        entry_data['persname'] = persname.text
        print(persname.text)
        if persname.has_attr('corresp'):
            corresp = persname['corresp']
        else:
            corresp = ''
        entry_data['corresp'] = corresp
        if ', ' in persname.text:
            entry_data['persname_first'] = persname.text.split(', ')[1]
            entry_data['persname_last'] = persname.text.split(', ')[0]
        else:
            entry_data['persname_first'] = ''
            entry_data['persname_last'] = ''
        rolename = entry.find('rolename')
        if rolename is not None:
            entry_data['rolename'] = rolename.text
        else:
            entry_data['rolename'] = ''
        if entry.find('date') is not None:
            entry_data['date'] = entry.find('date').text
            entry_data['date_from'] = entry.find('date').get('from', '')
            entry_data['date_to'] = entry.find('date').get('to', '')
        else:
            entry_data['date'] = ''
            entry_data['date_from'] = ''
            entry_data['date_to'] = ''
        entry_data['seg'] = []
        for seg in list(entry.find_all('seg')):
            seg_data = {}
            if seg.has_attr('rs'):
                seg_data['rs'] = seg.find('rs').text,
            elif len(seg.find_all('date')) > 0:
                seg_data['rs'] = seg.text.replace(seg.find('date').text, '').replace(',', '')
            seg_data['date'] = seg.find('date').text,
            seg_data['date_from'] = seg.find('date').get('from', ''),
            seg_data['date_to'] = seg.find('date').get('to', ''),
            entry_data['seg'] += [seg_data]
        data += [entry_data]

with open('data/section_a.json', 'w') as f:
    f.write(json.dumps(data))
