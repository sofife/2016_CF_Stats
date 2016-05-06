from bs4 import BeautifulSoup as bs
import urllib.request
import pandas as pd
import numpy as np # for NaN


def makeurl(reg,div=1,num=100,page=1,sort=0,yr=16):
	"""Makes the URL to pull data for each region, currently only pulls frontpage of leaderboard."""
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=5&regional=2&userid=0&competition=0&frontpage=0&expanded=1&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0&"
	# variable items in url
	sort = "sort=" + str(sort) + "&"  # 0-overall, 1-open wk1, 2-open wk2, ...
	division = "division=" + str(div) + "&"  # 1-individual men, 2-ind. women, 3-masters men 45-49, 4-masters women 45-49, ...
	region = "region=" + str(reg) + "&"  # 0-worldwide, 1-africa, 2-asia, 3-australia, 4-canada east, 5-canada west, 6-central east, 7-europe, ...
	year = "year=" + str(yr) + "&"  # 2-digit year "16"
	num_per = "numberperpage=" + str(num) + "&"  # works up to at least 100, number of athletes per leaderboard page
	page = "page=" + str(page)

	tail = sort + division + region + year + num_per + page
	
	return lead + tail

# cfg_url = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&division=1&region=1&regional=2&numberperpage=10&userid=0&competition=0&frontpage=0&expanded=1&year=16&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0"


def get_leaderboard_page(reg,div=1,num=100,page=1,sort=0,yr=16):
	"""Get open data for 1 region of 1 division"""
	cfg_url = makeurl(reg,div,num,page,sort,yr)  # create region leaderboard url

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
					   'Finish':place,
					   'Wk1':wk1,
					   'Wk2':wk2,
					   'Wk3':wk3,
					   'Wk4':wk4,
					   'Wk5':wk5,
					   'Athlete_URL':athlete_url,
					   'User_ID':0,
					   'Age':0,
					   'Height':0,
					   'Weight':0,
					   'Gender':gender})  # initialize dataframe

	return df


def get_regional_page(reg,div=101):
	"""Get regional data for 1 regional of 1 division"""
	
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=0&sort=0&"
	tail = "region=0&numberperpage=100&page=0&competition=1&frontpage=0&expanded=1&full=1&year=16&showtoggles=0&hidedropdowns=0&showathleteac=1&athletename=&fittest=1&fitSelect=undefined&scaled=0&occupation=0"
	division = "division=" + str(div) + "&"
	regional = "regional=" + str(reg)
	cfg_url = lead + division + regional + tail
	print(cfg_url)

	response = urllib.request.urlopen(cfg_url)
	html = response.read()
	page = bs(html, 'html.parser')
	scores_table = page.table  # grab just the table from the html
	rows = str(scores_table).split('<tr class')  # convert bs html to string, split data into athlete blocks

	q_place = [] # initialize temporary lists
	name = []
	status = []
	athlete_url = []

	for r in range(1,len(rows)):
		temp_row = bs(rows[r][5:], 'html.parser')  # strip broken tag off beginning, return to BeautifulSoup object
		lines = temp_row.find_all('td')  # break into individual data
		# for l in lines:
			# print(l.get_text())
		n,q = lines[1].get_text().strip().split("(")
		# print(n, q[:-1])
		# break

		name.append(n)  # athlete name
		q_place.append(q[:-1])  # athlete name
		status.append(lines[2].get_text().strip())  # open wk 1 place
		athlete_url.append(temp_row.find('a').get('href'))  # athlete profile link url

	df = pd.DataFrame({'Athlete':name,
					   'Q_Place':q_place,
					   'Regional':reg,
					   'Status':status,
					   'Athlete_URL':athlete_url,
					   'Division':div})

	return df
	# return None


def get_all_regions(regs,div=1,num=100,pages=1,sort=0,yr=16):
	"""Loop through all regions and append dataframes"""
	
	cfg_data = get_leaderboard_page(regs[0],div,num,1,sort,yr)  # first region	
	for p in range(2, pages+1):  # get all pages of first region
		# print(p)
		temp_df = get_leaderboard_page(regs[0],div,num,p,sort,yr)
		cfg_data = pd.concat([cfg_data,temp_df])  # add to bottom of primary df

	if len(regs) == 1:
		return cfg_data

	for r in regs[1:]:
		for p in range(1, pages+1):
			temp_df = get_leaderboard_page(r,div,num,p,sort,yr)  # next region
			cfg_data = pd.concat([cfg_data,temp_df])  # add to bottom of primary df
	
	return cfg_data


def get_athlete_data(df):
	"""Function to scrape athlete data from profile pages"""
	url_list = list(df['Athlete_URL'])  # list of all athlete profile urls
	# url_list = ["http://games.crossfit.com/athlete/234504"] # test athlete profile with no team or affiliate

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
		trim_start = page_str.find("Athlete Profile")  # trim html
		
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

		trim_end = page_str.find("ATHLETE INFORMATION")  # set ending trim point for html string
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


def get_division(regs,div,num=100,page=1,sort=0,yr=16):
	cfg_df = get_all_regions(regs,div,num,0,16)
	csv_name = "cfg_open_results_" + str(div) + ".csv"
	cfg_df.to_csv(csv_name, index=True)
	# print(cfg_df.head())	
	return None


def convert_weight(weight):
	"""Input weight as a string, determines kg or lb and returns float in lbs."""
	try:  num, unit = weight.split()
	except:  return np.nan

	if unit == "lb":  return round(int(num) * 1.0, 2)
	else:  return round(int(num) * 2.20462, 2)


def convert_time(time):
	"""Input time as a string, return seconds."""
	try:  minutes, seconds = time.split(":")
	except:  return np.nan

	time_in_seconds = int(minutes) * 60 + int(seconds)
	if time_in_seconds == 0:  return np.nan
	else:  return time_in_seconds


def split_score(place_score):
	"""Input a '# (##)' score and return place & score as ints."""
	place, score = place_score.split()
	place = int(place)

	if ":" in score:
		score = convert_time(score[1:-1])  # score is a time, convert to seconds, int
	else:
		score = int(score[1:-1])  # score is reps, convert to int
	
	return place, score


def transform_data(filename, return_df=False):
	"""Open csv, transform dataframe, write csv.  Optional return dataframe with True."""
	df = pd.read_csv(filename)

	# Convert place (score) to 2 columns
	df['Place'] = df['Finish'].apply(lambda x: split_score(x)[0])
	df['Score'] = df['Finish'].apply(lambda x: split_score(x)[1])
	df['Wk1_Place'] = df['Wk1'].apply(lambda x: split_score(x)[0])
	df['Wk1_Score'] = df['Wk1'].apply(lambda x: split_score(x)[1])
	df['Wk2_Place'] = df['Wk2'].apply(lambda x: split_score(x)[0])
	df['Wk2_Score'] = df['Wk2'].apply(lambda x: split_score(x)[1])
	df['Wk3_Place'] = df['Wk3'].apply(lambda x: split_score(x)[0])
	df['Wk3_Score'] = df['Wk3'].apply(lambda x: split_score(x)[1])
	df['Wk4_Place'] = df['Wk4'].apply(lambda x: split_score(x)[0])
	df['Wk4_Score'] = df['Wk4'].apply(lambda x: split_score(x)[1])
	df['Wk5_Place'] = df['Wk5'].apply(lambda x: split_score(x)[0])
	df['Wk5_Score'] = df['Wk5'].apply(lambda x: split_score(x)[1])

	# Convert weights to pounds with no units
	df['Weight'] = df['Weight'].apply(convert_weight)
	df['Clean_And_Jerk'] = df['Clean_And_Jerk'].apply(convert_weight)
	df['Snatch'] = df['Snatch'].apply(convert_weight)
	df['Deadlift'] = df['Deadlift'].apply(convert_weight)
	df['Back_Squat'] = df['Back_Squat'].apply(convert_weight)

	# Convert times to seconds
	df['Fran'] = df['Fran'].apply(convert_time)
	df['Helen'] = df['Helen'].apply(convert_time)
	df['Grace'] = df['Grace'].apply(convert_time)
	df['Filthy_50'] = df['Filthy_50'].apply(convert_time)
	df['Sprint_400'] = df['Sprint_400'].apply(convert_time)
	df['Run_5k'] = df['Run_5k'].apply(convert_time)

	# Convert '--' to NaN
	df.loc[df['Fight_Gone_Bad'] == '--', 'Fight_Gone_Bad'] = np.nan
	df.loc[df['Max_Pullups'] == '--', 'Max_Pullups'] = np.nan

	# Convert / Add other stuff
	df['User_ID'] = df['Athlete_URL'].apply(lambda x: x.split("/")[-1])

	new_filename = filename[:-5] + "c.csv"
	df.to_csv(new_filename, index=False)

	if return_df: return df  # if option is True, return the dataframe
	return None


def add_regional_data(df_file,r_df_file,q_df_file,i_df_file,div):
	"""Add regional data to primary df."""
	# ath_list = list(df['Athlete_URL'])
	df = pd.read_csv(df_file)
	r_df = pd.read_csv(r_df_file)
	q_df = pd.read_csv(q_df_file)
	i_df = pd.read_csv(i_df_file)

	r_df['User_ID'] = r_df['Athlete_URL'].apply(lambda x: x.split("/")[-1])
	i_df['User_ID'] = i_df['Athlete_URL'].apply(lambda x: x.split("/")[-1])


	# from r_df -> Regional Statistics File, Top 300 from each Region
	df['Region'] = df['User_ID'].apply(lambda x: int(r_df.loc[r_df['User_ID'] == str(x), 'Region']))
	df['Reg_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Finish'].values[0]))
	df['Reg_Place'] = df['Reg_Finish'].apply(lambda x: split_score(x)[0])
	df['Reg_Score'] = df['Reg_Finish'].apply(lambda x: split_score(x)[1])
	# df['Reg_Wk1_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Wk1'].values[0]))
	# df['Reg_Wk1_Place'] = df['Reg_Wk1_Finish'].apply(lambda x: split_score(x)[0])
	# df['Reg_Wk2_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Wk1'].values[0]))
	# df['Reg_Wk2_Place'] = df['Reg_Wk2_Finish'].apply(lambda x: split_score(x)[0])
	# df['Reg_Wk3_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Wk1'].values[0]))
	# df['Reg_Wk3_Place'] = df['Reg_Wk3_Finish'].apply(lambda x: split_score(x)[0])
	# df['Reg_Wk4_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Wk1'].values[0]))
	# df['Reg_Wk4_Place'] = df['Reg_Wk4_Finish'].apply(lambda x: split_score(x)[0])
	# df['Reg_Wk4_Finish'] = df['User_ID'].apply(lambda x: str(r_df.loc[r_df['User_ID'] == str(x), 'Wk1'].values[0]))
	# df['Reg_Wk4_Place'] = df['Reg_Wk4_Finish'].apply(lambda x: split_score(x)[0])

	# from q_df -> cutoff by region, and regional data
	df['Regional'] = df['Region'].apply(lambda x: int(q_df.loc[q_df['Region'].astype(int) == x, 'Regional'].values[0]))
	df['Regional_Name'] = df['Region'].apply(lambda x: str(q_df.loc[q_df['Region'].astype(int) == x, 'Regional_Name'].values[0]))
	df['Region_Name'] = df['Region'].apply(lambda x: str(q_df.loc[q_df['Region'].astype(int) == x, 'Region_Name'].values[0]))
	df['Reg_Cutoff'] = df['Region'].apply(lambda x: int(q_df.loc[q_df['Region'].astype(int) == x, 'Qualifiers'].values[0]))
	if div == 1:
		df['Reg_Actual'] = df['Region'].apply(lambda x: int(q_df.loc[q_df['Region'].astype(int) == x, 'Actual_1'].values[0]))
	elif div == 2:
		df['Reg_Actual'] = df['Region'].apply(lambda x: int(q_df.loc[q_df['Region'].astype(int) == x, 'Actual_2'].values[0]))
	else:
		df['Reg_Actual'] = df['Reg_Cutoff']
	df['Reg_Auto_Qualify'] = np.where(df['Reg_Place'] <= df['Reg_Cutoff'], 1, 0)
	df['Reg_Actual_Qualify'] = np.where(df['Reg_Place'] <= df['Reg_Actual'], 1, 0)

	# from i_df -> who was invited and who decline or chose team
	# df['Status'] = df['User_ID'].apply(lambda x: str(i_df.loc[i_df['User_ID'] == str(x), 'Status'].values[0]))
	# df['Status'] = 

# df['color'] = np.where(df['Set']=='Z', 'green', 'red')
# df['color'] = ['red' if x == 'Z' else 'green' for x in df['Set']]

	print("GOOD")
	# print(ath_dict)
	print(df['Region_Name'].head())
	print(df['Regional_Name'].head())
	print(df['Status'].head())
	# print(df['Reg_Cutoff'].head())
	# print(df['Reg_Actual'].head())
	# print(df['Reg_Auto_Qualify'].sum())
	# print(df['Reg_Actual_Qualify'].sum())
	# print(df['Reg_Finish'].head())
	# print(df['Reg_Place'].head())
	# print(df['Reg_Wk1_Place'].head())

	return None


def combine_divisions(df1,df2):
	"""Enter 2 identical dataframes from different divisions and return a combined dataframe."""
	return pd.concat([df1,df2])


def get_ww(reg=0,div=1,num=100,pages=1,sort=0,yr=16):
	"""Get results for specified number of athletes worldwide place and score"""
	cfg_data = get_leaderboard_page(reg,div,num,1,sort,yr)  # first region
	
	# if pages == 1:
	# 	return cfg_data

	for p in range(1, pages+1):
		# print(p)
		temp_df = get_leaderboard_page(reg,div,num,p,sort,yr)  # next region
		cfg_data = pd.concat([cfg_data,temp_df])  # add to bottom of primary df

	return cfg_data


def get_all_regional_data():
	regionals = [1,2,3,4,5,6,7,8]
	divisions = [101,201]

	first = True
	# regional_df = None

	for d in divisions:
		for r in regionals:
			if first:
				regional_df = get_regional_page(r,d)
				first = False
				continue
			temp_df = get_regional_page(r,d)
			regional_df = pd.concat([regional_df,temp_df])

	return regional_df





# get_division(regions,1,100,0,16)

# cfg_1 = pd.read_csv("cfg_open_results_1.csv")
# # print(cfg_1.describe())
# cfg_1 = get_athlete_data(cfg_1)
# # print(cfg_1.head())
# cfg_1.to_csv("cfg_open_results_1b.csv", quoting=None)


# get_division(regions,2,100,0,16)

# cfg_2 = pd.read_csv("cfg_open_results_2.csv")
# cfg_2 = get_athlete_data(cfg_2)
# cfg_2.to_csv("cfg_open_results_2b.csv", quoting=None)

# cfg_1 = pd.read_csv("cfg_open_results_1b.csv")
# cfg_1 = transform_data(cfg_1)

# filename_list = ['cfg_open_results_1b.csv', 'cfg_open_results_2b.csv']

# transform_data(filename_list[0], False)
# transform_data(filename_list[1], False)

# div1 = pd.read_csv('cfg_open_results_1c.csv')
# div2 = pd.read_csv('cfg_open_results_2c.csv')

# all_cfg = combine_divisions(div1, div2)
# print(all_cfg.describe())
# all_cfg.to_csv('cfg_open_all.csv')


# ww_df = get_ww(0,1,100,20,0,16)  # region=0 (worldwide),division=1 (ind. men),number per page=100,pages=1,sort=0 (overall),yr=16 (2016)
# print(ww_df.head())
# ww_df.to_csv("cfo_ww_1.csv", index=False)
# ww_df = pd.read_csv("cfo_ww_1.csv")
# ww_df = get_athlete_data(ww_df)

# ww_df.to_csv("cfo_ww_1b.csv", quoting=None)

# ww_df = pd.read_csv('cfo_ww_1b2.csv')
# print("Load")
# ww_df = transform_data('cfo_ww_1b.csv', True)
# print(ww_df.head())

# reg_df = get_all_regions(regions,div=1,num=100,pages=3,sort=0,yr=16)
# print(reg_df.describe())
# reg_df.to_csv("cfo_reg_300_1.csv", index=False)

# rg_df = get_all_regional_data()
# print(rg_df.describe())
# rg_df.to_csv('cf_regional_invites.csv', index=False)

add_regional_data('cfo_ww_1c.csv', 'cfo_reg_300_1.csv', 'cf_regional_qualifiers.csv', 'cfo_reg_invites.csv',1)