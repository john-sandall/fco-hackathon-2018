import codecs
import json
from geotext import GeoText
import googlemaps  # noqa
import numpy as np
import pandas as pd
import time  # noqa
import unicodedata
import yaml


with open('config.yml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

google_api_key = config['google_api_key']


def specials(error):
    return specstd.get(ord(error.object[error.start]), u''), error.end


specstd = {ord(u'’'): u"'", }


def asciify(x):
    return unicodedata.normalize('NFKD', x).encode('ASCII', 'specials')


# Generate asciified gt_index
codecs.register_error('specials', specials)
gt_index = [asciify(x).decode('utf-8').lower() for x in GeoText('').index[1].keys()]
gt_index += [asciify(x).decode('utf-8').lower() for x in GeoText('').index[2].keys()]
gt_index = list(set(gt_index) -
                set(['', ' ', 'un', None, 'oi', 'po', 'ek', 'ho', 'wa', 'bo', 'of', 'uk', 'ara', 'mongo',
                     'of', 'ho', 'bo', 'wa', 'pau', 'bra', 'roy', 'dir', 'mul', 'man', 'leo', 'vic', 'uga',
                     'can', 'rho', 'mut', 'san', 'ita', 'osa', 'mol', 'bar', 'Man', 'bah', 'agr', 'pen',
                     'Asia', 'asia', 'disa', 'nehe', 'perm', 'mila', 'maur', 'mala', 'anta', 'york', 'mari',
                     'salo', 'agen', 'labo', 'indi', 'bata', 'kara', 'wels', 'soma', 'ruma',
                     'assis', 'union', 'tanza', 'gotha', 'Union', 'colon', 'jamai', 'roman', 'tanga', 'Enugu']))


london_jobs = pd.read_csv('data/london_roles.txt', header=None)[0].tolist()

with open('data/section_a.json', 'r') as f:
    data = json.loads(f.read())


def extract_location(x):
    rename = {
        'Luxemburg': 'Luxembourg',
        'Venenzuela': 'Venezuela',
        'Lourenco Marques': 'Maputo',
        'N.A.T.O.': 'Brussels',
        'Energy European Commission': 'Brussels',
        'St. Louis': 'st louis, missouri',
        'O.E.C.D.': 'paris',
        'United Nations Organization': 'new york',
        'Shanhai': 'shanghai',
        'German Confederation': 'germany',
        'New Hebrides': 'Vanuatu',
        'the Congo': 'Democratic Republic of the Congo',
        'Buda-Pest': 'Budapest',
        'Bavaria': 'Stuttgart',
        'Wurttemberg': 'Stuttgart',
        'Wurtemberg': 'Stuttgart',
        'Siam': 'Thailand',
        'Two Sicilies': 'Naples',
        'O.E.E.C.': 'paris',
        'O.E.C.C.': 'paris',
        'Camboadia': 'Cambodia',
        'Diarmament Conference': 'Geneva',
        'Disarmament Conference': 'Geneva',
        'German Democratic Republic': 'berlin',
        'Oporto': 'Porto',
        'Philiippines': 'Philippines',
        'Seycelles': 'Seychelles',
        'Casablance': 'Casablanca',
        'Yugoslavia': 'Belgrade',
        'Basra': 'Iraq',
        'Shangai': 'Shanghai',
        'Jedda': 'Jeddah',
        'Franfurt': 'Frankfurt',
        'Ceylon': 'Sri Lanka',
        'Istabul': 'Istanbul',
        'Rhineland': 'Bonn',
        'Prussia': 'Berlin',
        'Sardinia-Piedmont': 'Turin',
        'Piedmont-Sardinia': 'Turin',
        'Sir Lanka': 'Sri Lanka',
        'Middle East Command': 'Cairo',
        'Far East Command': 'Singapore',
        'Far East Forces': 'Singapore',
        'United Nations Department': 'new york',
        'United Nations Trusteeship Council': 'new york',
        'U.N.E.C.O.': 'new york',
        'European Commissioner for External Relations': 'Brussels',
        'Danzig': 'Gdansk',
        'Middle East Forces': 'Cairo',
        'to Korea': 'Seoul',
        'Resident Korea': 'Seoul',
        'United Nations Economic and Social Council': 'new york',
        'European Commissioner for Budget and Financial Control and Institutions': 'Brussels',
        'European Uniion': 'Brussels',
        'Comprehensive Test Ban Negotiations': 'Geneva',
        'Comprehensive Test Test Ban Treaty Negotiations': 'Geneva',
        'Comprehensive Test Ban Treaty Negotiations': 'Geneva',
        'C.in-C. Far East': 'Singapore',
        'Jersusalem': 'Jerusalem',
        'Saigon': 'Ho Chi Minh City',
        'Cameroun': 'Cameroon',
        'Swaziliand': 'Swaziland',
        'Zaire': 'Democratic Republic of the Congo',
        'Congo': 'Democratic Republic of the Congo',
        'Nicaragaua': 'Nicaragua',
        'U.N.E.S.C.O.': 'paris',
        'CommissionTanzania': 'Tanzania',
        'European Economic Communities': 'Brussels',
        'European Economic Community': 'Brussels',
        'E.E.C.': 'Brussels',
        'European Community': 'Brussels',
        'European Communities': 'Brussels',
        'European Free Trade Association ': 'Geneva',
        'E.F.T.A.': 'Geneva',
        'European Commission': 'Brussels',
        'Near East Forces/Middle East Command': 'Cairo',
        'Conventional Arms Control Negotiations ': 'Brussels',
        'Organization for Security and Co-operation in Europe ': 'Vienna',
        'Conference on Security and Co-operation in Europe': 'Vienna',
        'Organization for Economic Co-operation and Development ': 'paris',
        'U.N. Conference on Law of the Sea': 'Jamaica',
        'United Nations Conference on Law of the Sea': 'Jamaica',
        'Democratic People’s Republic of Korea': 'Pyongyang',
        'United Arab Republic': 'Cairo',
        'Middle East Office': 'Cairo',
        'South Arabia': 'Yemen',
        'United Provinces': 'Lucknow, India',
        'Nyasaland': 'Zomba, Malawi',
        'North-West Frontier Province': 'Peshawar',
        'Sind': 'Karachi',
        'Leeeward Islands': 'Leeward Islands',
        'Falkland Isles': 'Falkland Islands',
        'Madras': 'Chennai, India',
        'Holy See': 'Vatican City',
        'Bosnia-Herzegovina': 'Sarajevo',
        'Bosnia Herzegovina': 'Sarajevo',
        'Polish Government': 'Warsaw',
        'League of Nations': 'Geneva',
        'Council of Europe': 'Strasbourg',
        'Qaatar': 'Qatar',
        'Delegation to the European Union': 'Brussels',
        'Representation to European Union': 'Brussels',
        'Conference on Confidence and Security Building Measures and Disarmament in Europe': 'Stockholm',
        'Permanent Representation to the European Union': 'Brussels',
        'Permant Representation to the European Union': 'Brussels',
        'Security Union': 'Brussels',
        'Tanganykia': 'Dar es Salaam',
        'European Union Commission': 'Brussels',
        'Malaya': 'Kuala Lumpur',
        'European Union Trade Commissioner': 'Brussels',
        'Representative to European Union': 'Brussels',
        'Conference on Security and Disarmament in Europe': 'Vienna',
        'West Indies Associated States': 'Saint Lucia',
        'Salonica': 'Thessaloniki',
        'Osaka-Kobe': 'Osaka',
        'International Atomic Energy Agency': 'Vienna',
        'European Union Political and Security Committee': 'Brussels',
        'Political and Security Committee European Union': 'Brussels',
        'Representative to the European Union': 'Brussels',
        'Mutual Forces and Armaments Reductions Negotiations': 'Vienna',
        'Mutual and Balanced Reduction of Forces and Armaments in Europe': 'Vienna',
        'Rhodesia': 'Zimbabwe',
        'Wallachia and Moldavia': 'Romania',
        'Leopoldville': 'Kinshasa',
        'San Frncisco': 'San Francisco',
        'Trucial States': 'United Arab Emirates',
        'Mutual and Balanced Force Reductions Negotiations': 'Vienna',
        'Mutual Reduction of Forces and Armaments Negotiations': 'Vienna',
        'Negotiations on Mutual Reduction of Forces and Armaments': 'Vienna',
        'South-East Asia': 'Singapore',
        'Czechoslovakia': 'Prague',
        'Saxe-Coburg Gotha': 'Gotha',
    }
    london_offices = [
        'Foreign and Commonwealth Office',
        'Foreign Office',
        'Cabinet Office',
        'Chancellor of the Exchequer',
        'Joint Intelligence Committee',
        'Commonwealth Relations Department',
        'Foreign and Commonwealth Affairs',
        'Dominions Office',
        'Foreign and Commonwealth Offices',
    ]
    for k in london_offices:
        rename[k] = 'London, United Kingdom'
    extra_locations = gt_index
    extra_locations += [
        'usa',
        'persia',
        'burma',
        'somaliland',
        'milan',
        'ussr',
        'gotha',
        'gothenburg',
        'tuscany',
        'frankfurt',
        'czechoslovakia'
        'osaka',
        'yugoslavia',
        'seville',
        'maputo',
        'st louis, missouri',
        'saxony',
        'antwerp',
        'constantinople',
        'cologne',
        'tasmania',
        'bihar',
        'leeward islands',
        'falkland islands',
        'new south wales',
    ]
    for k, v in rename.items():
        if k in x:
            x = x.replace(k, v)

    places = GeoText(x)
    cities = ' '.join(places.cities)
    countries = ' '.join(places.countries)
    if x in london_jobs:
        return "London, United Kingdom"
    elif (len(cities) > 1) and (len(countries) > 1):
        return f"{cities}, {countries}"
    elif (len(cities) > 0) or (len(countries) > 0):
        return f"{cities}{countries}"
    else:
        for location in extra_locations:
            if f" {location}" in x.lower().replace('.', ''):
                return location
        return ''


df = pd.DataFrame(data, columns=['persname', 'date_from', 'date_to', 'seg'])
out = []
for i, row in df.iterrows():
    for seg in row.seg:
        row_out = {'persname': row.persname}
        row_out['born'] = int(row.date_from) if row.date_from != '' else np.nan
        row_out['died'] = int(row.date_to) if row.date_to != '' else np.nan
        row_out['rs'] = seg['rs']
        row_out['date_from'] = seg['date_from']
        row_out['date_to'] = seg['date_to']
        out += [row_out]

df_all = pd.DataFrame(out)
df_all['location'] = df_all.rs.apply(lambda x: extract_location(x))

# Edge cases to be fixed
with open('data/location_edge_cases.txt', 'w') as f:
    f.write("\n".join(df_all[df_all.location == ''].rs.unique()))

# print(df_all[df_all.location == ''].rs.unique())
df_all['len'] = df_all.location.apply(lambda x: len(x))
df_all[df_all['len'] == 3].location.unique()


# Geocode using Google Maps API
# gmaps_conn = googlemaps.Client(key=google_api_key)
# all_locations = df_all.location.unique()
# geocoded_data = {}
# for location in all_locations:
#     if location not in geocoded_data and location != '':
#         print(location)
#         geocoded_data[location] = gmaps_conn.geocode(location)
#         time.sleep(0.5)
# Cache
# with open('data/geocoded_locations.json', 'w') as f:
#     f.write(json.dumps(geocoded_data))

# Use locally cached version
with open('data/geocoded_locations.json', 'r') as f:
    geocoded_data = json.loads(f.read())

# Add geocoded info to df
df_all.loc[df_all.location == '', 'location'] = 'London, United Kingdom'
df_all.loc[df_all.location == 'Mali Niger', 'location'] = 'Mali'


# TODO: This is just embarrassing.

def lat_fn(x):
    if len(geocoded_data[x]) > 0:
        return geocoded_data[x][0]['geometry']['location']['lat']
    else:
        return np.nan


def lon_fn(x):
    if len(geocoded_data[x]) > 0:
        return geocoded_data[x][0]['geometry']['location']['lng']
    else:
        return np.nan


def formatted_location_fn(x):
    if len(geocoded_data[x]) > 0:
        return geocoded_data[x][0]['formatted_address']
    else:
        return np.nan


def country_fn(x):
    if len(geocoded_data[x]) > 0:
        out = [c['long_name'] for c in geocoded_data[x][0]['address_components'] if 'country' in c['types']]
        if len(out) > 0:
            return out[0]
        else:
            out = [c['long_name'] for c in geocoded_data[x][0]['address_components'] if 'continent' in c['types']]
            if len(out) > 0:
                return out[0]
            else:
                return [c['long_name'] for c in geocoded_data[x][0]['address_components']
                        if 'natural_feature' in c['types']][0]
    else:
        return np.nan


def country_code_fn(x):
    if len(geocoded_data[x]) > 0:
        out = [c['short_name'] for c in geocoded_data[x][0]['address_components'] if 'country' in c['types']]
        if len(out) > 0:
            return out[0]
        else:
            out = [c['short_name'] for c in geocoded_data[x][0]['address_components'] if 'continent' in c['types']]
            if len(out) > 0:
                return out[0]
            else:
                return [c['short_name'] for c in geocoded_data[x][0]['address_components']
                        if 'natural_feature' in c['types']][0]
    else:
        return np.nan


df_all['lat'] = df_all.location.apply(lat_fn)
df_all['lon'] = df_all.location.apply(lon_fn)
df_all['formatted_location'] = df_all.location.apply(formatted_location_fn)
df_all['country'] = df_all.location.apply(country_fn)
df_all['country_code'] = df_all.location.apply(country_code_fn)


# Export as JSON
df_all.to_json('data/section_a_locations.json', orient='records')
df_all.to_csv('data/section_a_locations.csv', index=False)
