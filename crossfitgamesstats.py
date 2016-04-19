from bs4 import BeautifulSoup as bs
import urllib.request

cfg_url = "http://games.crossfit.com/scores/leaderboard.php?stage=5&sort=0&division=1&region=1&regional=2&numberperpage=10&userid=0&competition=0&frontpage=0&expanded=1&year=16&full=0&showtoggles=0&hidedropdowns=1&showathleteac=0&athletename=&scaled=0"

response = urllib.request.urlopen(cfg_url)
html = response.read()

page = bs(html, 'html.parser')

# print(page.get_text())
scores_table = page.table
# print(scores_table)

rows = str(scores_table).split('<tr class')

for r in range(1,len(rows)):
	temp_row = bs(rows[r][5:], 'html.parser') # strip broken tag off beginning, return to BeautifulSoup object
	# print(temp_row.get_text())
	# temp_row2 = temp_row.get_text()
	# temp_row2 = temp_row2.replace('\n', "")
	# print(temp_row2)
	# print(temp_row.find_all('td')[0].get_text())

	lines = temp_row.find_all('td')

	# print(len(lines))
	place = lines[0].get_text().strip()
	name = lines[1].get_text().strip()
	wk1 = lines[2].get_text().strip()
	wk2 = lines[3].get_text().strip()
	wk3 = lines[4].get_text().strip()
	wk4 = lines[5].get_text().strip()
	wk5 = lines[6].get_text().strip()
	athlete_url = temp_row.find('a').get('href')

	# print(name+', '+place)
	# print(wk1, wk2, wk3, wk4, wk5)
	# print(url)

	break

# rows = scores_table.find_all('tr')

# print(rows[1])
# print(len(rows))


# scores_list = scores_table.split('<tr class="">')
# print(scores_list)


# print(page.table.get_text())

