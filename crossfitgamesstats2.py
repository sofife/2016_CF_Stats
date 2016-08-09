from bs4 import BeautifulSoup as bs
import urllib.request
import pandas as pd
import numpy as np # for NaN
import re


def makeurl(reg=0,regional=0,div=1,num=100,page=1,sort=0,yr=16,comp=0):
	"""Makes the URL to pull data for each region, currently only pulls frontpage of leaderboard."""
	
	lead = "http://games.crossfit.com/scores/leaderboard.php?stage=0&userid=0&frontpage=0&expanded=1&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0&"
	# variable items in url
	sort = "sort=" + str(sort) + "&"  # 0-overall, 1-open wk1, 2-open wk2, ...
	division = "division=" + str(div) + "&"  # 1-individual men, 2-ind. women, 3-masters men 45-49, 4-masters women 45-49, ...
	region = "region=" + str(reg) + "&"  # 0-worldwide, 1-africa, 2-asia, 3-australia, 4-canada east, 5-canada west, 6-central east, 7-europe, ...
	regional = "regional" + str(regional) + "&"
	year = "year=" + str(yr) + "&"  # 2-digit year "16"
	num_per = "numberperpage=" + str(num) + "&"  # works up to at least 100, number of athletes per leaderboard page
	comp = "competition" + str(comp) + "&"
	page = "page=" + str(page)

	tail = sort + division + region + regional + year + num_per + comp + page
	
	return lead + tail


def get_event_score(score, event, yr):
	"""Splits the score format from CFG leaderboard"""
	
	if yr == 15 and event == 9:
		if score[1] == '36T':
			score = ['', '36T', '', '', '8 pts0 lb', '', '', '']
		elif score[1] == '38th':
			score = ['', '38th', '', '', '4 pts0 lb', '', '', '']

	if yr == 14 and event == 2:
		if score[1] == '43rd':
			score = ['', '43rd', '', '', '14 pts0 lb', '', '', '']

	e_place = score[1]
	if e_place[-1] == "T":
		e_place = int(e_place[:-1])
	else:
		e_place = int(e_place[:-2])


	e_pts, e_score = score[4].split(' pts')
	e_pts = int(e_pts)
	# e_time = convert_event_time(e_time, event)

	return e_place, e_pts, e_score


def get_leaderboard_page(reg=0,regional=0,div=1,num=100,page=1,sort=0,yr=16,comp=0,write_to_csv=False):
	"""Get open data for 1 region of 1 division"""
	cfg_url = makeurl(reg,regional,div,num,page,sort,yr,comp)  # create leaderboard url
	output_filename = 'cf_games_results_20' + str(yr) + '.csv'

	response = urllib.request.urlopen(cfg_url)
	html = response.read()
	page = bs(html, 'html.parser')
	scores_table = page.table  # grab just the table from the html
	rows = str(scores_table).split('<tr class')  # convert bs html to string, split data into athlete blocks
	# rows = page.find_all('tr')
	# print(rows[1])
	# print(scores_table.prettify())

	games_place = [] # initialize temporary lists
	name = []

	athlete_url = []

	e_count_by_year = {12:15,13:12,14:13,15:13,16:15}
	e_max = e_count_by_year[yr]
	print(e_max)
	
	event_01 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_02 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_03 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_04 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_05 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_06 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_07 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_08 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_09 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_10 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_11 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_12 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_13 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_14 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}
	event_15 = {'place':[], 'points':[], 'score':[], 'cap_hit':[]}

	event_list = [event_01, event_02, event_03, event_04, event_05, event_06, event_07, event_08, 
				  event_09, event_10, event_11, event_12, event_13, event_14, event_15]

	for r in range(1,len(rows)):  # each loop is 1 athlete

		temp_row = bs(rows[r][5:], 'html.parser')  # strip broken tag off beginning, return to BeautifulSoup object
		lines = temp_row.find_all('td')  # break into individual data
		# print(lines[3].get_text())
		# break
		games_place.append(lines[0].get_text().strip())  # regional place
		name.append(lines[1].get_text().strip())  # athlete name
		athlete_url.append(temp_row.find('a').get('href'))  # athlete profile link url

		for i in range(0,e_max):  # get each event data for 1 athlete, capped by number of events - e_max
			event_place = ''
			event_points = 0
			event_score = ''

			if lines[i+2].get_text().split('\n')[1] == "WD":
				event_place, event_points, event_score = "WD", np.nan, np.nan
			elif lines[i+2].get_text().split('\n')[1] == "CUT":
				event_place, event_points, event_score = "CUT", np.nan, np.nan
			elif lines[i+2].get_text().split('\n')[1] == "--":
				event_place, event_points, event_score = "--", np.nan, np.nan
			else:
				event_place, event_points, event_score = get_event_score(lines[i+2].get_text().split('\n'), i+1, yr)
		
			event_list[i]['place'].append(event_place)
			event_list[i]['points'].append(event_points)
			event_list[i]['score'].append(event_score)
			event_list[i]['cap_hit'].append('')

		for j in range(e_max,15):
			# print(j)
			event_list[j]['place'].append(np.NaN)
			event_list[j]['points'].append(np.NaN)
			event_list[j]['score'].append(np.NaN)
			event_list[j]['cap_hit'].append(np.NaN)

	df = pd.DataFrame({'Athlete':name,
					   'Games_Finish':games_place,
					   'Athlete_URL':athlete_url,
					   'Division':div,
					   'Year':int('20'+str(yr)),
					   'G_01_Place':event_list[0]['place'],
					   'G_02_Place':event_list[1]['place'],
					   'G_03_Place':event_list[2]['place'],
					   'G_04_Place':event_list[3]['place'],
					   'G_05_Place':event_list[4]['place'],
					   'G_06_Place':event_list[5]['place'],
					   'G_07_Place':event_list[6]['place'],
					   'G_08_Place':event_list[7]['place'],
					   'G_09_Place':event_list[8]['place'],
					   'G_10_Place':event_list[9]['place'],
					   'G_11_Place':event_list[10]['place'],
					   'G_12_Place':event_list[11]['place'],
					   'G_13_Place':event_list[12]['place'],
					   'G_14_Place':event_list[13]['place'],
					   'G_15_Place':event_list[14]['place'],
					   'G_01_Points':event_list[0]['points'],
					   'G_02_Points':event_list[1]['points'],
					   'G_03_Points':event_list[2]['points'],
					   'G_04_Points':event_list[3]['points'],
					   'G_05_Points':event_list[4]['points'],
					   'G_06_Points':event_list[5]['points'],
					   'G_07_Points':event_list[6]['points'],
					   'G_08_Points':event_list[7]['points'],
					   'G_09_Points':event_list[8]['points'],
					   'G_10_Points':event_list[9]['points'],
					   'G_11_Points':event_list[10]['points'],
					   'G_12_Points':event_list[11]['points'],
					   'G_13_Points':event_list[12]['points'],
					   'G_14_Points':event_list[13]['points'],
					   'G_15_Points':event_list[14]['points'],
					   'G_01_Raw_Score':event_list[0]['score'],
					   'G_02_Raw_Score':event_list[1]['score'],
					   'G_03_Raw_Score':event_list[2]['score'],
					   'G_04_Raw_Score':event_list[3]['score'],
					   'G_05_Raw_Score':event_list[4]['score'],
					   'G_06_Raw_Score':event_list[5]['score'],
					   'G_07_Raw_Score':event_list[6]['score'],
					   'G_08_Raw_Score':event_list[7]['score'],
					   'G_09_Raw_Score':event_list[8]['score'],
					   'G_10_Raw_Score':event_list[9]['score'],
					   'G_11_Raw_Score':event_list[10]['score'],
					   'G_12_Raw_Score':event_list[11]['score'],
					   'G_13_Raw_Score':event_list[12]['score'],
					   'G_14_Raw_Score':event_list[13]['score'],
					   'G_15_Raw_Score':event_list[14]['score']})

	if write_to_csv:
		df.to_csv(output_filename, index=True)
		return None

	return df


events_raw = ['G_01_Raw_Score', 'G_02_Raw_Score', 'G_03_Raw_Score', 'G_04_Raw_Score', 'G_05_Raw_Score',
			  'G_06_Raw_Score', 'G_07_Raw_Score', 'G_08_Raw_Score', 'G_09_Raw_Score', 'G_10_Raw_Score', 
			  'G_11_Raw_Score', 'G_12_Raw_Score', 'G_13_Raw_Score', 'G_14_Raw_Score', 'G_15_Raw_Score']

events = ['G_01_Score', 'G_02_Score', 'G_03_Score', 'G_04_Score', 'G_05_Score',
		  'G_06_Score', 'G_07_Score', 'G_08_Score', 'G_09_Score', 'G_10_Score', 
		  'G_11_Score', 'G_12_Score', 'G_13_Score', 'G_14_Score', 'G_15_Score']


def convert_non_time(score):
	return re.findall(r'\d{1,3}\.?\d{0,2}', score)[0]


def convert_time(time, event_id, div):
	"""Input time as a string, return seconds."""
	# print(e_df.loc[e_df['Event_ID'] == event_id, 'Cap (sec, m)'])
	# print(event_id, time, div)

	if "CAP" in time:  # could definitely use some refactoring b/c of the womens cap issue
		print(e_df.loc[e_df['Event_ID'] == event_id, 'Cap (sec, m)'])
		if "+" in time:
			s = int(e_df.loc[e_df['Event_ID'] == event_id, 'Cap (sec, m)']) + int(time.split('+')[1].strip())
		else:
			s = int(e_df.loc[e_df['Event_ID'] == event_id, 'Cap (sec, m)'])
		# print(s)
		return float(s)
	elif time:
		if time.count(':') == 2:
			h, m, s = time.split(':')
			return float(h)*3600 + float(m)*60 + float(s.strip())
		elif time.count(':') == 1:
			m, s = time.split(':')
			return float(m)*60 + float(s.strip())
		else:
			s = time
			return float(s.strip())
	else:
		return np.NaN


def convert_score(score, event, year, div):
	event_id = str(year) + "_" + str(event).zfill(2) 
	print(event_id, score, div)

	if score == np.NaN:
		print(1)
		return np.NaN
	print(2)
	if 'lb' in score:
		print(3)
		return convert_non_time(score)
	print(4)
	if 'pt' in score:
		print(5)
		return convert_non_time(score)
	print(6)
	if 'in' in score:
		print(7)
		return convert_non_time(score)
	print(8)
	return convert_time(score, event_id, div)


def transform_df(df):

	for i in range(0,15):
		# print(events[i])
		df['Games_Score'] = df['Games_Finish'].apply(lambda x: x.split(' ')[1][1:-1] if ')' in x else np.NaN)
		# df['Games_Score'] = df['Games_Score'].
		df['Games_Place'] = df['Games_Finish'].apply(lambda x: x.split(' ')[0] if ')' in x else x)
		df[events[i]] = df[events_raw[i]].apply(str)
		df[events[i]] = df.apply(lambda x: convert_score(x[events[i]], i+1, x['Year'], x['Division']), axis=1)

	print(df['G_04_Score'].head(5))
	print(df['G_05_Score'].head(5))
	print(df.head(5))

	return df


def transform_df2(df):

	df['Year'] = df['Year'].apply(lambda x: str(x)[0:4])
	df['Event_#'] = df['Event_#'].apply(lambda x: str(x).split('.')[0])
	df['Event_Raw_Score'] = df['Event_Raw_Score'].apply(str)
	df['Event_Score'] = df.apply(lambda x: convert_score(x['Event_Raw_Score'], x['Event_#'], x['Year'], x['Division']), axis=1)

	return df


def get_all_games(filename=None):
	
	first = True
	for d in range(1,3):
		for y in range(12,17):
			if first:
				g_df = get_leaderboard_page(0,0,d,100,1,0,y,2,False)
				first = False
				continue
			
			g2_df = get_leaderboard_page(0,0,d,100,1,0,y,2,False)
			g_df = pd.concat([g_df, g2_df])

	g_df = transform_df(g_df)

	if filename:
		g_df.to_csv(filename, index=True)
		return None

	return g_df


# get_leaderboard_page(0,0,1,100,1,0,12,2,True)
# get_all_games('cf_games_results_all.csv')
# df = pd.read_csv('cf_games_results_all.csv')
df = pd.read_csv('cf_games_results_all_t2.csv')
e_df = pd.read_csv('cfg_event_data.csv')
# print(e_df.head())
t_df = transform_df2(df)
t_df.to_csv('cf_games_results_all_t3.csv')

