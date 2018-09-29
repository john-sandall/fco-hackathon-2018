import codecs
import json
from geotext import GeoText
import numpy as np
import pandas as pd
import spacy
import unicodedata


def specials(error):
    return specstd.get(ord(error.object[error.start]), u''), error.end


specstd = {ord(u'’'): u"'", }


def asciify(x):
    return unicodedata.normalize('NFKD', x).encode('ASCII', 'specials')


# Generate asciified gt_index
codecs.register_error('specials', specials)
gt_index = [asciify(x).decode('utf-8').lower() for x in GeoText('').index[1].keys()]
gt_index += [asciify(x).decode('utf-8').lower() for x in GeoText('').index[2].keys()]
gt_index = list(set(gt_index) - set(['', ' ', 'un', None, 'oi', 'po', 'ek', 'ho', 'wa', 'bo', 'of']))


with open('data/section_a.json', 'r') as f:
    data = json.loads(f.read())


def extract_location(x):
    extra_locations = gt_index
    extra_locations += [
        'usa',
    ]
    # london_jobs = [
    #     'Political Adviser Far East Forces',
    # ]
    places = GeoText(x)
    cities = ' '.join(places.cities)
    countries = ' '.join(places.countries)
    if (len(cities) > 1) and (len(countries) > 1):
        return f"{cities}, {countries}"
    elif (len(cities) > 0) or (len(countries) > 0):
        return f"{cities}{countries}"
    else:
        for location in extra_locations:
            if f" {location}" in x.lower().replace('.', ''):
                return location
        # raise UserWarning(x)
        return ''


df = pd.DataFrame(data, columns=['persname', 'date_from', 'date_to', 'seg'])
out = []
for i, row in df.iterrows():
    row_out = {'persname': row.persname}
    row_out['born'] = int(row.date_from) if row.date_from != '' else np.nan
    row_out['died'] = int(row.date_to) if row.date_to != '' else np.nan
    for seg in row.seg:
        row_out['rs'] = seg['rs']
        row_out['date_from'] = seg['date_from']
        row_out['date_to'] = seg['date_to']
        out += [row_out]

df_all = pd.DataFrame(out)
df_all['location'] = df_all.rs.apply(lambda x: extract_location(x))

# Export as JSON
df_all.to_json('data/section_a_locations.json', orient='records')
df_all.to_csv('data/section_a_locations.csv', index=False)

# Edge cases to be fixed
with open('data/location_edge_cases.csv', 'w') as f:
    f.write("\n".join(df_all[df_all.location == ''].rs.unique()))
