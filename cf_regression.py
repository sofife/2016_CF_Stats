import pandas as pd
import numpy as np # for NaN
# from sklearn.linear_model import LinearRegression # Import the linear regression class
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(context="paper", font="monospace")


def combine_all():
	df_o = pd.read_csv('cf_open_final.csv')
	df_r = pd.read_csv('cf_regional_final.csv')
	df_g = pd.read_csv('cf_games_final.csv')

	df_g = df_g[df_g['Year'] == 2016]
	games_athletes = df_g['Athlete'].tolist()

	df_r.rename(columns={'Norm_E1':'R_01n','Norm_E2':'R_02n','Norm_E3':'R_03n','Norm_E4':'R_04n',
					     'Norm_E5':'R_05n','Norm_E6':'R_06n','Norm_E7':'R_07n','Norm_Overall':'R_Ov_n',
					     'Overall_Z-Score':'R_Z','Normalized_Overall_Regional_Place':'R_Ov_n_Place',
					     'Regional_Place':'R_Place','Overall_Regional_Place':'R_OpenPlace','Total_Score':'R_OpenScore',
					     'E1 Rank':'R_01_Place','E2 Rank':'R_02_Place','E3 Rank':'R_03_Place','E4 Rank':'R_04_Place',
					     'E5 Rank':'R_05_Place','E6 Rank':'R_06_Place','E7 Rank':'R_07_Place'}, inplace=True)

	df_o.rename(columns={'Place':'O_Place','Score':'O_OpenScore','Open Z-Score':'O_Z',
						 # 'N.Wk1':'O_01n','N.Wk2':'O_02n','N.Wk3':'O_03n','N.Wk4':'O_04n',
						 # 'N.Wk5':'O_05n','N.Total':'O_Ov_n',
						 'Wk1_Place':'O_01_Place','Wk2_Place':'O_02_Place','Wk3_Place':'O_03_Place',
						 'Wk4_Place':'O_04_Place','Wk5_Place':'O_05_Place'}, inplace=True)

	# FIX OPEN NORMALIZED SCORES, errors in min/max scores in original analysis
	o_stats = {1:{1:[df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk1_Score'].max(),
					 df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk1_Score'].min()],
			      2:[df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk1_Score'].max(),
			         df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk1_Score'].min()]},
			   2:{1:[df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk2_Score'].max(),
					 df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk2_Score'].min()],
				  2:[df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk2_Score'].max(),
					 df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk2_Score'].min()]},
			   3:{1:[df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk3_Score'].max(),
					 df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk3_Score'].min()],
				  2:[df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk3_Score'].max(),
				     df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk3_Score'].min()]},
			   4:{1:[df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk4_Score'].max(),
			   		 df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk4_Score'].min()],
				  2:[df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk4_Score'].max(),
				  	 df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk4_Score'].min()]},			 
			   5:{1:[df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk5_Score'].max(),
			   		 df_o.loc[(df_o['Division'] == 1) & (df_o['Status_Code'] == 1), 'Wk5_Score'].min()],
				  2:[df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk5_Score'].max(),
				  	 df_o.loc[(df_o['Division'] == 2) & (df_o['Status_Code'] == 1), 'Wk5_Score'].min()]}}

	df_o['O_01n'] = df_o.apply(lambda x: (x['Wk1_Score'] - o_stats[1][x['Division']][1]) / (o_stats[1][x['Division']][0] - o_stats[1][x['Division']][1]), axis=1)
	df_o['O_02n'] = df_o.apply(lambda x: (x['Wk2_Score'] - o_stats[2][x['Division']][1]) / (o_stats[2][x['Division']][0] - o_stats[2][x['Division']][1]), axis=1)
	df_o['O_03n'] = df_o.apply(lambda x: (x['Wk3_Score'] - o_stats[3][x['Division']][1]) / (o_stats[3][x['Division']][0] - o_stats[3][x['Division']][1]), axis=1)
	df_o['O_04n'] = df_o.apply(lambda x: (x['Wk4_Score'] - o_stats[4][x['Division']][1]) / (o_stats[4][x['Division']][0] - o_stats[4][x['Division']][1]), axis=1)
	df_o['O_05n'] = df_o.apply(lambda x: (x['Wk5_Score'] - o_stats[5][x['Division']][0]) / (o_stats[5][x['Division']][1] - o_stats[5][x['Division']][0]), axis=1)
	df_o['O_Ov_n'] = (df_o['O_01n'] + df_o['O_02n'] + df_o['O_03n'] + df_o['O_04n'] + df_o['O_05n']) / 5 * 100

	# print(df_o[['O_01n','O_02n','O_03n','O_04n','O_05n','O_Ov_n']].head())
	df_o['O_Top40'] = df_o['Athlete'].apply(lambda x: 1 if x in games_athletes else 0)
	df_o['O_Top40'] = df_o.groupby(['Division','O_Top40'])['O_OpenScore'].rank(method='first')
	df_o['O_Top40'] = df_o.apply(lambda x: np.NaN if x['Athlete'] not in games_athletes else x['O_Top40'], axis=1)
	# df_o['O_Top40'] = 
	# print(df_o['O_Top40'].head(50))

	df_r[df_r['R_OpenScore'] == 'WD'] = np.NaN
	df_r['R_Top40'] = df_r['Athlete'].apply(lambda x: 1 if x in games_athletes else 0)
	df_r['R_Top40'] = df_r.groupby(['Division','R_Top40'])['R_OpenScore'].rank(method='min')
	df_r['R_Top40'] = df_r.apply(lambda x: np.NaN if x['Athlete'] not in games_athletes else x['R_Top40'], axis=1)


	# print(df_r['R_Top40'].head(50))

	o_list = ['Athlete_URL','Height','Weight','Affiliate','O_Top40',
			  'O_01n','O_02n','O_03n','O_04n','O_05n','O_Ov_n','O_Z',
			  'O_01_Place','O_02_Place','O_03_Place','O_04_Place','O_05_Place']

	r_list = ['Athlete_URL','R_Place','Regional','R_OpenScore','R_OpenPlace','R_01n','R_02n','R_03n','R_04n','R_05n',
			  'R_06n','R_07n','R_Ov_n','R_Ov_n_Place','R_Z','R_01_Place','R_02_Place','R_03_Place','R_04_Place',
			  'R_05_Place','R_06_Place','R_07_Place','Fran','Helen','Grace','Filthy_50','Fight_Gone_Bad','Sprint_400',
			  'Run_5k','Clean_And_Jerk','Snatch','Deadlift','Back_Squat','Max_Pullups','WC_Qualify','R_Top40']

	# NORMALIZE GAMES EVENT SCORES 'G_01n'

	games_event_order = [1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1]
	games_event_wt = [1,1,1,1,1,1,1,1,1,.5,.5,.5,1,1,1]

	df_g['G_Ov_n'] = 0
	df_g['G_OpenScore'] = 0

	for e in range(1,16):

		e_name = "G_%02dn" % (e)
		score = "G_%02d_Score" % (e)
		place = "G_%02d_Place" % (e)
		to_drop = "G_%02d_Raw_Score" % (e)
		d = 'Division'
		# print(e_name, score)
		if games_event_order[e-1] == 1:
			df_g[e_name] = df_g.apply(lambda x: x[score] - df_g.loc[df_g[d] == x[d], score].max(), axis=1)
			df_g[e_name] = df_g.apply(lambda x: x[e_name]/(df_g.loc[df_g[d] == x[d], score].min() - df_g.loc[df_g[d] == x[d], score].max()), axis=1)
		else:
			df_g[e_name] = df_g.apply(lambda x: x[score] - df_g.loc[df_g[d] == x[d], score].min(), axis=1)
			df_g[e_name] = df_g.apply(lambda x: x[e_name]/(df_g.loc[df_g[d] == x[d], score].max() - df_g.loc[df_g[d] == x[d], score].min()), axis=1)
		
		df_g.drop(to_drop, axis=1, inplace=True)
		
		df_g['G_Ov_n'] = df_g['G_Ov_n'] + df_g[e_name] * games_event_wt[e-1]

		df_g[df_g[place] == 'WD'] = np.NaN
		df_g['G_OpenScore'] = df_g['G_OpenScore'] + df_g[place].astype(float)

	df_g['G_Ov_n'] = df_g['G_Ov_n'] / sum(games_event_wt) * 100
	df_g['G_OpenPlace'] = 0
	df_g['G_OpenPlace'] = df_g.groupby('Division')['G_OpenScore'].rank(method='first')
	df_g['G_Top40'] = df_g['Games_Place']
	df_g['G_Ranch'] = df_g['G_01_Points'] + df_g['G_02_Points'] + df_g['G_03_Points']
	df_g['G_Beach'] = df_g['G_04_Points']
	df_g['G_Special'] = df_g['G_01_Points'] + df_g['G_02_Points'] + df_g['G_03_Points'] + df_g['G_04_Points']
	df_g['G_Soccer'] = df_g['G_03_Points'] + df_g['G_08_Points'] + df_g['G_11_Points'] + df_g['G_12_Points'] + df_g['G_13_Points']
	df_g['G_Tennis'] = df_g['G_06_Points'] + df_g['G_07_Points'] + df_g['G_09_Points'] + df_g['G_10_Points'] + df_g['G_14_Points'] + df_g['G_15_Points']
	# df_g[df_g['Division'] == 1]['G_OpenPlace'] = df_g.apply(lambda x: df_g.loc[df_g['Division'] == x['Division'],'G_OpenScore'].rank(), axis=1)
	# print(df_g[['G_Ranch','G_Beach']].head(10))
	# print(df_g[['G_01n','G_Ov_n','Athlete']].head())


	# DROP UNEEDED GAMES DF COLUMNS
	# NORMALIZED OVERALL SCORE VS REGULAR SCORING (PER EVENT PTS)

	# df = df_g[df_g['Year'] == 2016]
	# df = pd.merge(df_g[df_g['Year'] == 2016], df_r, left_on='Athlete_URL', right_on='Athlete_URL', how='left')

	df_all = pd.merge(df_g, df_r[r_list], left_on='Athlete_URL', right_on='Athlete_URL', how='left')
	df_all = pd.merge(df_all, df_o[o_list], left_on='Athlete_URL', right_on='Athlete_URL', how='left')

	# df_o = pd.merge(df_o, df_r[['R_Top40','Athlete_URL']], left_on='Athlete_URL', right_on='Athlete_URL', how='left')

	# ADD OPEN/REG NORMALIZED PLACE 1-40 -> THINK IT THROUGH
	# OR ADD OPEN/REG OVERALL PLACE 1-40 -> THINK IT THROUGH, DO BOTH AND COMPARE

	# print(df_all.head())
	df_all.to_csv('cf_combined_all.csv')
	# b = pd.merge(df_pairs, data_df, left_on='city2', right_on='city', how='left').set_index(['city1', 'city2'])
	return None


def heatmap():
	df_all = pd.read_csv('cf_combined_all.csv')
	df_all = df_all[df_all['Division'] == 1]
	# print(df_all.head())
	pts_list = ['Games_Place','Games_Score',
				'O_01n','O_02n','O_03n','O_04n','O_05n',
				'R_01n','R_02n','R_03n','R_04n','R_05n','R_06n','R_07n',
				'G_01n','G_02n','G_03n','G_04n','G_05n','G_06n','G_07n','G_08n','G_09n','G_10n','G_11n','G_12n','G_13n','G_14n','G_15n'
				]

	plc_list = ['Games_Place',
				# 'Games_Score',
				# 'O_01_Place','O_02_Place','O_03_Place','O_04_Place','O_05_Place',
				# 'R_01_Place','R_02_Place','R_03_Place','R_04_Place','R_05_Place','R_06_Place','R_07_Place',
				# 'G_01_Place','G_02_Place','G_03_Place','G_04_Place','G_05_Place','G_06_Place','G_07_Place','G_08_Place',
				# 'G_09_Place','G_10_Place','G_11_Place','G_12_Place','G_13_Place','G_14_Place','G_15_Place'
				]

	oth_list = ['Games_Score','G_Ranch','G_Beach','G_Tennis','G_Soccer']

	df_pts = df_all[pts_list]
	df_plc = df_all[plc_list]
	df_oth = df_all[oth_list]	

	# print(1)
	# df_corr = sns.load_dataset(df_pts)
	# print(df.columns.values)
	# df.drop('Unnamed',axis=1,inplace=True)
	# print(df.head())
	# df_corr = df_pts.corr()
	df_corr = df_plc.corr()
	print(df_corr.head(1))
	# df_corr = df_oth.corr()
	# df_corr = df_corr.abs()
	# print(df_corr.head())
	# df_corr[df_corr == 1] = np.NaN
	# df_corr[df_corr.abs() != df_corr.abs().max()] = np.NaN
	# print(df_corr.max())
	# print(df_corr['G_07n'])
	f, ax = plt.subplots(figsize=(12, 9))
	sns.heatmap(df_corr, vmax=.8, square=True)
	plt.yticks(rotation=0)
	plt.xticks(rotation=80)
	# networks = df_corr.columns.get_level_values("network")
	# for i, network in enumerate(networks):
	#     if i and network != networks[i - 1]:
	#         ax.axhline(len(networks) - i, c="w")
	#         ax.axvline(i, c="w")
	f.tight_layout()
	plt.show()


def all_events():
	df_all = pd.read_csv('cf_combined_all.csv')
	df_all['Ultra_Score'] = (df_all['O_Ov_n'] * 5 + df_all['R_Ov_n'] * 7 + df_all['G_Ov_n'] * 13.5) / 25.5
	# print(df_all[['Athlete','O_Ov_n','R_Ov_n','G_Ov_n','Ultra_Score']])
	df_all['Ultra_Place'] = df_all.groupby(['Division'])['Ultra_Score'].rank(method='first',ascending=False)
	print(df_all.loc[df_all['Division'] == 2, ['Athlete','Ultra_Score','Ultra_Place']])
	df_all.to_csv('cf_combined_all.csv')


def modality():
	df_all = pd.read_csv('cf_combined_all.csv')
	df_all['G_SingleModal'] = df_all['G_02_Points'] + df_all['G_04_Points'] + df_all['G_06_Points'] + df_all['G_11_Points'] + df_all['G_12_Points'] + df_all['G_13_Points']
	df_all['G_MultiModal'] = df_all['Games_Score'] - df_all['G_SingleModal']
	df_all['G_Ranch_Place'] = df_all.groupby(['Division'])['G_Ranch'].rank(method='first',ascending=False)
	df_all['G_Beach_Place'] = df_all.groupby(['Division'])['G_Beach'].rank(method='first',ascending=False)
	df_all['G_Soccer_Place'] = df_all.groupby(['Division'])['G_Soccer'].rank(method='first',ascending=False)
	df_all['G_Tennis_Place'] = df_all.groupby(['Division'])['G_Tennis'].rank(method='first',ascending=False)
	df_all['G_Special_Place'] = df_all.groupby(['Division'])['G_Special'].rank(method='first',ascending=False)
	print(df_all.loc[df_all['Division'] == 1, ['Athlete','G_Ranch','G_Ranch_Place']])
	df_all.to_csv('cf_combined_all.csv')



# combine_all()
# heatmap()
all_events()
modality()