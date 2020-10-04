# This script scrapes the daily COVID-19 updates posted on the Minnesota Dept.
# of Health website into clean, machine-readable formats

# imports
import requests
import lxml.html as lh
import pandas as pd
from itertools import chain
import re

# set URL to parse, create handle for page, and store contents under doc
url = 'https://www.health.state.mn.us/diseases/coronavirus/situation.html'
page = requests.get(url)
doc = lh.fromstring(page.content)

# define which of the tables from the doc to parse
def parse_table(table_name):
    tr_elements = doc.xpath('//*[@id="'+ table_name +'"]//tr')

    # convert table into list for cleaning
    table=[]
    x = 0
    y = 0

    while x < len(tr_elements):
        t = tr_elements[x]
        data=t.text_content()
        tmp_list = []
        tmp_list.append((data))
        table.append(list(tmp_list))
        x += 1
    return table

# clean unneccessary spacing/characters from dataframe to prepare for dataframe
def clean_data(table_name):
    table = parse_table(table_name)
    y = 0

    while y < len(table):
        if table_name in ['agetable', 'restable', 'hosptable']:
            table[y] = [z.strip().replace('\r\n            ',''', ''').replace('\r\n\t\t\t',''', ''').split(', ') for z in table[y]]
        if table_name == 'ccftable':
            table[y] = [z.strip().replace('\r\n      ',''', ''').replace('\r\n\t\t\t',''', ''').replace('\r\n\t    ',''', ''').replace('\r\n ',''', ''').replace('\r\n   ',''', ''').replace('   ',' ').split(', ') for z in table[y]]
        if table_name == 'maptable':
            table[y] = [z.strip().replace('\r\n            ',''', ''').replace('\r\n\t\t\t',''', ''').replace('\xa0','').split(', ') for z in table[y]]
        if table_name in ['dailycase', 'dailydeathar', 'dailydeathrt']:
            table[y] = [z.strip().replace('\r\n    ',''',''').replace('        ','').replace('\r\n\t\t\t',''',''').replace('\xa0','').split(',') for z in table[y]]
        if table_name in ['deathtable', 'casetable']:
            table[y] = [z.strip().replace('\r\n\    ',''', ''').replace('\r\n  ',''', ''').replace('        ','').replace('\r\n\t\t\t',''', ''').replace('\xa0','').replace('\t','').replace('   ',' ').strip().split(', ') for z in table[y]]
        if table_name == 'labtable':
            table[y] = [z.strip().replace('\r\n            ',''', ''').replace('        ','').replace('\r\n\t\t\t',''', ''').replace('\xa0','').replace('\t','').replace('   ',' ').replace('\r\n  ',', ').strip().split(', ') for z in table[y]]
        y += 1
    return table

# create dataframe from list
def df_create(table_name, filename):
    table = clean_data(table_name)
    table_chain = list(chain.from_iterable(table))
    df = pd.DataFrame(table_chain)
    if table_name == 'hosptable':
        df2 = df.drop(df.index[0]).drop(columns=[5])
        df2.columns = ['Date reported', 'Hospitalized in ICU', 'Hospitalized Not in ICU', 'Total hospitalized', 'Total ICU Hospitalized']
    else:
        df2 = df.rename(columns=df.iloc[0]).drop(df.index[0])
    filepath = r'filepath.csv'
    filepath2 = filepath.replace('placeholder',filename)
    df2.to_csv(filepath2, index=False)

# output files for each category
df_create('agetable','age_range')
df_create('maptable','county_case')
df_create('dailycase','daily_case')
df_create('dailydeathar','daily_death_ar')
df_create('dailydeathrt','daily_death_rt')
df_create('deathtable','deaths')
df_create('hosptable','hospitalized')
df_create('ccftable','ltc_list')
df_create('casetable','positive_cases')
df_create('deathtable','deaths')
df_create('restable', 'res_type')
df_create('labtable', 'testing')
