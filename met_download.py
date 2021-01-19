import requests
from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import pandas as pd

met_csv_file = "MetObjects.csv"
img_dir = "paintings"
dest_csv = 'paintings_descrs.csv'

met = pd.read_csv('MetObjects.csv')
public = met[met['Is Public Domain']]
paintings = public[ public['Classification'].map(lambda x: 'painting' in str(x).lower()) ]
paintings.to_csv('paintings.csv')

if not os.path.exists(img_dir):
	os.makedirs(img_dir)

descrs = []
errors = []
for obj_id in tqdm(paintings['Object ID']):
	try:
		URL = 'https://www.metmuseum.org/art/collection/search/{}'.format(obj_id)
		page = requests.get(URL)
		soup = BeautifulSoup(page.content)
		img_link = soup.find(class_='artwork__interaction artwork__interaction--download').a['href']
		img_link = 'https://' + urllib.parse.quote(img_link[8:])
		descr = soup.find(class_='artwork__intro__desc').p.get_text()
		urllib.request.urlretrieve(img_link, os.path.join(img_dir, str(obj_id)+'.jpg'))
	except Exception as e:
		print(e)
		print('error on', obj_id)
		errors.append(obj_id)
		descr = None
	if descr != None:
		descrs.append(descr)

paintings_descrs = paintings.copy()
for obj_id in errors:
	paintings_descrs = paintings_descrs[ paintings_descrs['Object ID'] != obj_id ]

print(len(errors), 'URL errors')

paintings_descrs['Description Paragraph'] = descrs

paintings_descrs.to_csv(dest_csv)