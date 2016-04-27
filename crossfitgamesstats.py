from bs4 import BeautifulSoup as bs
import urllib.request
import pandas as pd
import numpy as np # for NaN


def makeurl(reg, div=1, num=100, sort=0, yr=16):
	"""Makes the URL to pull data for each region, currently only pulls frontpage of leaderboard."""
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=5&regional=2&userid=0&competition=0&frontpage=0&expanded=1&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0&"
	# variable items in url
	sort = "sort=" + str(sort) + "&"  # 0-overall, 1-open wk1, 2-open wk2, ...
	division = "division=" + str(div) + "&"  # 1-individual men, 2-ind. women, 3-masters men 45-49, 4-masters women 45-49, ...
	region = "region=" + str(reg) + "&"  # 0-worldwide, 1-africa, 2-asia, 3-australia, 4-canada east, 5-canada west, 6-central east, 7-europe, ...
	year = "year=" + str(yr) + "&"  # 2-digit year "16"
	num_per = "numberperpage=" + str(num)  # works up to at least 100, number of athletes per leaderboard page

	tail = sort + division + region + year + num_per
	
	return lead + tail

# cfg_url = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&division=1&region=1&regional=2&numberperpage=10&userid=0&competition=0&frontpage=0&expanded=1&year=16&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0"


def get_region(reg,div=1,num=100,sort=0,yr=16):
	"""Get open data for 1 region of 1 division"""
	cfg_url = makeurl(reg,div,num,sort,yr)  # create region leaderboard url

	response = urllib.request.urlopen(cfg_url)
	html = response.read()
	page = bs(html, 'html.parser')
	scores_table = page.table  # grab just the table from the html
	rows = str(scores_table).split('<tr class')  # convert bs html to string, split data into athlete blocks

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
		temp_row = bs(rows[r][5:], 'html.parser')  # strip broken tag off beginning, return to BeautifulSoup object
		lines = temp_row.find_all('td')  # break into individual data

		place.append(lines[0].get_text().strip())  # regional place
		name.append(lines[1].get_text().strip())  # athlete name
		wk1.append(lines[2].get_text().strip())  # open wk 1 place
		wk2.append(lines[3].get_text().strip())
		wk3.append(lines[4].get_text().strip())
		wk4.append(lines[5].get_text().strip())
		wk5.append(lines[6].get_text().strip())
		athlete_url.append(temp_row.find('a').get('href'))  # athlete profile link url

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
					   'Gender':gender})  # initialize dataframe

	return df


def get_all_regions(regs,div=1,num=100,sort=0,yr=16):
	"""Loop through all regions and append dataframes"""
	cfg_data = get_region(regs[0],div,num,sort,yr)  # first region
	
	if len(regs) == 1:
		return cfg_data

	for r in regs[1:]:
		temp_df = get_region(r,div,num,sort,yr)  # next region
		cfg_data = pd.concat([cfg_data,temp_df])  # add to bottom of primary df

	return cfg_data


def get_athlete_data(df):
	"""Function to scrape athlete data from profile pages"""
	url_list = list(df['Athlete_URL'])  # list of all athlete profile urls
	# url_list = ["http://games.crossfit.com/athlete/10822"] # test athlete profile with no team or affiliate

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
		print(i, u)  # for trackiing error profiles
		i += 1

		response = urllib.request.urlopen(u)
		html = response.read()
		page = bs(html, 'html.parser')
		page_str = str(page)  # change bs html object to string
		trim_start = page_str.find("Athlete Profile") + 453  # trim html
		
		if "ATHLETE INFORMATION" not in page_str:  # if no athlete profile, set all to NaN
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

		trim_end = page_str.find("ATHLETE INFORMATION") - 277  # set ending trim point for html string
		page_bs = bs(page_str[trim_start:trim_end], 'html.parser')  # trim html and convert back to bs object
		dimensions = page_bs.find_all("dt")  # category names
		stats = page_bs.find_all("dd")  # category data

		a_dict = {}  # initialize dictionary to hold stats
		for j in range(0, len(dimensions)):
			a_dict[dimensions[j].get_text().strip()[:-1]] = stats[j].get_text().strip()  # strip ":" off category name, set equal to text of the stat

		try:
			region.append(a_dict["Region"])  # solve key error if no region listed
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
			if a_dict["Height"][-2:] == "cm":  # account for the royale with cheese
				# print("metric system")
				cms = a_dict["Height"].split()[0]
				# print(cms)
				temp_height = round(int(cms) / 2.54, 2)
				# print("sup")
				# print(temp_height)
			else:
				feet, inches = a_dict["Height"].split("'")  # imperial measure was messing up to_csv, so converting all heights to inches
				# print(feet, inches)
				temp_height = round(((int(feet) * 12) + int(inches[:-1])) * 1.0, 2)  # convert to float
			height.append(temp_height)
		except:
			height.append(np.nan)
		try:
			weight.append(a_dict["Weight"])
		except:
			weight.append(np.nan)

		workouts = page_bs.find_all("td")  # grab all benchmark scores, all non-null profiles should have at least placeholder text

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

	df["Team"] = team  # add new columns to df
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


def get_division(regs,div,num=100,sort=0,yr=16):
	cfg_df = get_all_regions(regs,div,num,0,16)
	csv_name = "cfg_open_results_" + str(div) + ".csv"
	cfg_df.to_csv(csv_name, index=True)
	# print(cfg_df.head())	
	return None


# get_division(regions,1,100,0,16)

cfg_1 = pd.read_csv("cfg_open_results_1.csv")
# print(cfg_1.describe())
cfg_1 = get_athlete_data(cfg_1)
# print(cfg_1.head())
cfg_1.to_csv("cfg_open_results_1b.csv", quoting=None)