from bs4 import BeautifulSoup as bs
import urllib.request
import pandas as pd
import numpy as np # for NaN


def makeurl(reg, div=1, yr=16, num=100):
	"""Makes the URL to pull data for each region"""
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&regional=2&userid=0&competition=0&frontpage=0&expanded=1&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0&"
	division = "division=" + str(div) + "&"
	region = "region=" + str(reg) + "&"
	year = "year=" + str(yr) + "&"
	num_per = "numberperpage=" + str(num)
	tail = division + region + year + num_per
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
	
	if len(regions) == 1:
		return cfg_data

	for r in regions[1:]:
		# print(r)
		temp_df = get_region(r,div,yr)
		cfg_data = pd.concat([cfg_data,temp_df])

	# print(cfg_data.head())
	# print(cfg_data.describe())

	return cfg_data


def get_athlete_data(df):

	url_list = list(df['Athlete_URL'])
	# url_list = ["http://games.crossfit.com/athlete/10822"] # test athlete profile with no team or affiliate

	# print(len(url_list))

	region = []
	team = []
	affiliate = []
	gender = []
	age = []
	height = []
	weight = []
	fran = []
	helen = []
	grace = []
	filthy50 = []
	fgb = []
	sprint400 = []
	run5k = []
	candj = []
	snatch = []
	deadlift = []
	squat = []
	pullups = []

	i = 0
	for u in url_list:
		print(i, u)
		i += 1

		response = urllib.request.urlopen(u)
		html = response.read()
		page = bs(html, 'html.parser')
		page_str = str(page)
		trim_start = page_str.find("Athlete Profile") + 453
		
		if "ATHLETE INFORMATION" not in page_str:
			region.append(np.nan)
			team.append(np.nan)
			affiliate.append(np.nan)
			gender.append(np.nan)
			age.append(np.nan)
			height.append(np.nan)
			weight.append(np.nan)
			fran.append(np.nan)
			helen.append(np.nan)
			grace.append(np.nan)
			filthy50.append(np.nan)
			fgb.append(np.nan)
			sprint400.append(np.nan)
			run5k.append(np.nan)
			candj.append(np.nan)
			snatch.append(np.nan)
			deadlift.append(np.nan)
			squat.append(np.nan)
			pullups.append(np.nan)
			print("Profile Missing")
			continue

		trim_end = page_str.find("ATHLETE INFORMATION") - 277
		page_bs = bs(page_str[trim_start:trim_end], 'html.parser')
		dimensions = page_bs.find_all("dt")
		stats = page_bs.find_all("dd")

		a_dict = {}
		for j in range(0, len(dimensions)):
			a_dict[dimensions[j].get_text().strip()[:-1]] = stats[j].get_text().strip()

		try:
			region.append(a_dict["Region"])
		except:
			region.append(np.nan)
		try:
			team.append(a_dict["Team"])
		except:
			team.append(np.nan)
		try:
			affiliate.append(a_dict["Affiliate"])
		except:
			affiliate.append(np.nan)
		try:
			gender.append(a_dict["Gender"])
		except:
			gender.append(np.nan)
		try:
			age.append(a_dict["Age"])
		except:
			age.append(np.nan)
		try:
			if a_dict["Height"][-2:] == "cm":
				cms = a_dict["Height"].split()[0]
				temp_height = cms / 2.54
			else:
				feet, inches = a_dict["Height"].split("'")
				# print(feet, inches)
				temp_height = ((int(feet) * 12) + int(inches[:-1])) * 1.0
			height.append(temp_height)
		except:
			height.append(np.nan)
		try:
			weight.append(a_dict["Weight"])
		except:
			weight.append(np.nan)

		workouts = page_bs.find_all("td")

		fran.append(workouts[1].get_text().strip())
		helen.append(workouts[3].get_text().strip())
		grace.append(workouts[5].get_text().strip())
		filthy50.append(workouts[7].get_text().strip())
		fgb.append(workouts[9].get_text().strip())
		sprint400.append(workouts[11].get_text().strip())
		run5k.append(workouts[13].get_text().strip())
		candj.append(workouts[15].get_text().strip())
		snatch.append(workouts[17].get_text().strip())
		deadlift.append(workouts[19].get_text().strip())
		squat.append(workouts[21].get_text().strip())
		pullups.append(workouts[23].get_text().strip())

	# print(team) 
	# print(len(df['Athlete']), len(team))

	df["Team"] = team
	df["Affiliate"] = affiliate
	df["Age"] = age
	df["Height"] = height
	df["Weight"] = weight
	df["Fran"] = fran
	df["Helen"] = helen
	df["Grace"] = grace
	df["Filthy_50"] = filthy50
	df["Fight_Gone_Bad"] = fgb
	df["Sprint_400"] = sprint400
	df["Run_5k"] = run5k
	df["Clean_And_Jerk"] = candj
	df["Snatch"] = snatch
	df["Deadlift"] = deadlift
	df["Back_Squat"] = squat
	df["Max_Pullups"] = pullups

	return df


divisions = (1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17) # Division 11 is Teams
regions = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17)
# regions = [17]

cfg_df = get_all_regions(1,16)
csv_name = "cfg_open_results_" + str(divisions[0]) + ".csv"
cfg_df.to_csv(csv_name, index=True)
print(cfg_df.head())

cfg_1 = pd.read_csv("cfg_open_results_1.csv")
# print(cfg_1.describe())
cfg_1 = get_athlete_data(cfg_1)
print(cfg_1.head())
cfg_1.to_csv("cfg_open_results_1b.csv", quoting=None)