from bs4 import BeautifulSoup as bs
import urllib.request
import pandas as pd


def makeurl(reg, div=1, yr=16):
	"""Makes the URL to pull data for each region"""
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&regional=2&numberperpage=10&userid=0&competition=0&frontpage=0&expanded=1&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0&"
	division = "division=" + str(div) + "&"
	region = "region=" + str(reg) + "&"
	year = "year=" + str(yr)
	tail = division + region + year
	return lead + tail

# cfg_url = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&division=1&region=1&regional=2&numberperpage=10&userid=0&competition=0&frontpage=0&expanded=1&year=16&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0"


def get_region(reg, div=1, yr=16):
	"""Get open data for 1 region of 1 division"""
	cfg_url = makeurl(reg,div,yr)

	response = urllib.request.urlopen(cfg_url)
	html = response.read()
	page = bs(html, 'html.parser')
	scores_table = page.table
	rows = str(scores_table).split('<tr class')

	if div in (1,3,5,7,9,12,14,16):  # male divisions
		gender = 1 # male
	else:
		gender = 0 # female

	place = [] # initialize temporary lists
	name = []
	wk1 = []
	wk2 = []
	wk3 = []
	wk4 = []
	wk5 = []
	athlete_url = []

	for r in range(1,len(rows)):
		temp_row = bs(rows[r][5:], 'html.parser') # strip broken tag off beginning, return to BeautifulSoup object
		lines = temp_row.find_all('td') # break into individual data

		place.append(lines[0].get_text().strip())
		name.append(lines[1].get_text().strip())
		wk1.append(lines[2].get_text().strip())
		wk2.append(lines[3].get_text().strip())
		wk3.append(lines[4].get_text().strip())
		wk4.append(lines[5].get_text().strip())
		wk5.append(lines[6].get_text().strip())
		athlete_url.append(temp_row.find('a').get('href'))

	df = pd.DataFrame({'Athlete':name,
					   'Year':yr,
					   'Region':reg,
					   'Reg_Place':place,
					   'Reg_Score':0,
					   'Wk1':wk1,
					   'Wk2':wk2,
					   'Wk3':wk3,
					   'Wk4':wk4,
					   'Wk5':wk5,
					   'Athlete_URL':athlete_url,
					   'Age':0,
					   'Height':0,
					   'Weight':0,
					   'Gender':gender}) 

	return df


def get_all_regions(div=1, yr=16):
	"""Loop through all regions and append dataframes"""
	cfg_data = get_region(regions[0],div,yr)
	
	for r in regions[1:]:
		# print(r)
		temp_df = get_region(r,div,yr)
		cfg_data = pd.concat([cfg_data,temp_df])

	# print(cfg_data.head())
	print(cfg_data.describe())


	return cfg_data


divisions = (1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17) # Division 11 is Teams
regions = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17)

cfg_df = get_all_regions(1,16)
csv_name = "cfg_open_results_" + str(divisions[0]) + ".csv"
cfg_df.to_csv(csv_name, index=True)

