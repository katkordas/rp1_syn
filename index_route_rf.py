import pandas as pd
from scipy.stats import binomtest

df = pd.read_csv("processed_data.csv")
syn_responses = df[["id","stimulus","color_bk"]].groupby(["id","stimulus"]).agg(pd.Series.mode).reset_index()

n = syn_responses.shape[0]
n_part = len(syn_responses["id"].unique())

# Taking care of multiple modes
# If there are three modes, we are just taking the first choice
colors = []
for index, row in syn_responses.iterrows():
    if isinstance(row['color_bk'], str):
        colors.append(row['color_bk'])
    else:
        colors.append(row['color_bk'][0])

syn_responses["color"] = colors

syn_responses = syn_responses.value_counts(["stimulus","color"]).to_frame().sort_index().reset_index()
syn_responses = syn_responses.rename(columns={0:'count'})

# Making lists for name-colour name pairings
index_df = pd.read_csv("index_route_nick_preds_PL.csv",encoding="utf-8",sep=",",usecols=["stimulus","color_bk","p_color"])
index_df = index_df.loc[index_df.stimulus.str.len() == 1] 
syn_responses = syn_responses[~syn_responses.stimulus.isin(["X","V","Q","Ą","Ę","Ń"])]# Excluding Ą, Ę and Ń (as well as the non-Polish letters) from the analysis
index_df = index_df.sort_values(['stimulus','p_color'],ascending=False).groupby('stimulus').head(2).drop(columns='p_color') # Getting top 2 colors based on p_color and then dropping it

from itertools import cycle

dummies = cycle(['color_1','color_2'])
index_df['dummy'] = [next(dummies) for i in range(len(index_df))]

index_df = index_df.pivot(index = 'stimulus',  columns = 'dummy', values = 'color_bk').reset_index()

# This is when I found out a rogue "fioletowy" somehow got caught up with the other English-language color terms...
index_df = index_df.replace("fioletowy", "purple")
print(index_df)

index_dict = index_df.set_index('stimulus').T.to_dict('list')
# Adding conditional column to dataframe
rf_column = []
for index, row in syn_responses.iterrows():
    k = str(row['color']).lower()
    i = str(row['stimulus'])
    if k == index_dict[i][0] or k == index_dict[i][1]:
        rf_column.append("TRUE")
    else:
        rf_column.append("FALSE")

syn_responses["indexroute_rf"] = rf_column

# Making list of index route pairings
index_df = pd.read_csv("index_route_nick_preds_PL.csv",sep=",",usecols=["stimulus","color_bk","p_color"])
index_df = index_df.loc[(index_df.stimulus.str.len() == 1)]
index_df = index_df.replace("fioletowy","purple")
indexroute_dict = {}

for i in index_df["stimulus"].unique():
    small_index_df = index_df.loc[(index_df["stimulus"] == i)].sort_values("p_color",ascending=False)[:2]
    indexroute_dict[i] = list(small_index_df["color_bk"].unique())

# Calculating Index Route RF based on instructions from Nick Root
# See: https://www.sciencedirect.com/science/article/pii/S1053810021001185
matches_obs = syn_responses.loc[syn_responses["indexroute_rf"] == "TRUE", "count"].sum()
graphemes_with_matches = syn_responses.loc[syn_responses["indexroute_rf"] == "TRUE",["stimulus","color","count","indexroute_rf"]]
could_match = syn_responses.loc[syn_responses["stimulus"].isin(list(graphemes_with_matches["stimulus"].unique())),["stimulus","color","count","indexroute_rf"]]
matches_possible = could_match["count"].sum()
# Let's calculate the pseudo R2 value!
obs_r2 = matches_obs/matches_possible
print("The observed R2 is: " + str(obs_r2))
# Now let's calculate the other statistic
# Starting with the total number of associations in the data, multiplied by the proportion of associations that are the grapheme g,3 multiplied by the proportion of associations that are the color c
p_total = 0
for i in indexroute_dict.keys():
    for j in indexroute_dict[i]:
        p_i = (syn_responses.loc[syn_responses["stimulus"] == i,"count"].sum())/n
        p_j = (syn_responses.loc[syn_responses["color"] == j.capitalize(),"count"].sum())/n
        p_total += (p_i * p_j)

exp_r2=(n*p_total)/matches_possible
print("The expected R2 is: " + str(exp_r2))

# Binomial test of the hypothesis:
# Expected proportion: exp_r2!
p = obs_r2
q = 1 - p
x = int(exp_r2 * n)

print(binomtest(x,n,p,alternative="less"))