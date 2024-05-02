import pandas as pd
import numpy as np
from scipy.stats import binomtest

df = pd.read_csv("processed_data.csv")
syn_responses = df[["id","stimulus","color_bk"]].groupby(["id","stimulus"]).agg(pd.Series.mode).reset_index()

n = syn_responses.shape[0]
n_part = len(syn_responses["id"].unique())
print("N synesthetes: "  + str(n_part))

# Taking care of multiple modes
# If there are three modes, we are just taking the first choice
colors = []
for index, row in syn_responses.iterrows():
    if isinstance(row['color_bk'], str):
        colors.append(row['color_bk'])
    else:
        colors.append(row['color_bk'][0])

syn_responses["color"] = colors

syn_responses = syn_responses.value_counts(subset=["stimulus","color"]).to_frame().sort_index().reset_index()
syn_responses = syn_responses.rename(columns={0:'count'})

# Making lists for name-colour name pairings
colorterm_dict = {"B" : ["White","Brown"], "C" : ["Black","Red"], "F" : "Purple", "N" : "Blue", "P" : "Orange", "R" : "Pink", "S" : "Grey", "Z" : "Green", "Ż" : "Yellow"}

# Adding conditional column to dataframe
rf_column = []
for index, row in syn_responses.iterrows():
    if row['stimulus'] in colorterm_dict.keys():
        if row['stimulus'] == "B" or row['stimulus'] == "C":
            if row['color'] == colorterm_dict["B"][0] or row['color'] == colorterm_dict["B"][1]:
                rf_column.append("TRUE")
            elif row['color'] == colorterm_dict["C"][0] or row['color'] == colorterm_dict["C"][1]:
                rf_column.append("TRUE")
            else:
                rf_column.append("FALSE")
        else:
            i = str(row['stimulus'])
            if row['color'] == colorterm_dict[i]:
                rf_column.append("TRUE")
            else:
                rf_column.append("FALSE")
    else:
        rf_column.append("FALSE")

syn_responses["colorname_rf"] = rf_column

# Calculating CT RF based on instructions from Nick Root
# See: https://www.sciencedirect.com/science/article/pii/S1053810021001185#s0025
# Step 1: matches_observed = with( syn_counts , sum(n_assocs[colorname_rf==TRUE]) )
matches_obs = syn_responses.loc[syn_responses["colorname_rf"] == "TRUE", "count"].sum()
# Step 2: graphemes_with_matches = filter( syn_counts , colorname_rf==TRUE )
graphemes_with_matches = syn_responses.loc[syn_responses["colorname_rf"] == "TRUE",["stimulus","color","count","colorname_rf"]]
# Step 3: could_match = filter( syn_counts , grapheme %in% graphemes_with_matches)
could_match = syn_responses.loc[syn_responses["stimulus"].isin(list(graphemes_with_matches["stimulus"].unique())),["stimulus","color","count","colorname_rf"]]
# Step 4: 
matches_possible = could_match["count"].sum()
# Let's calculate the pseudo R2 value!
obs_r2 = matches_obs/matches_possible
print("The observed R2 is: " + str(obs_r2))
# Now let's calculate the other statistic
# Starting with the total number of associations in the data, multiplied by the proportion of associations that are the grapheme g,3 multiplied by the proportion of associations that are the color c

p_total = 0
for i in colorterm_dict.keys():
    if isinstance(colorterm_dict[i], str):
        p_i = (syn_responses.loc[syn_responses["stimulus"] == i,"count"].sum())/n
        p_j = (syn_responses.loc[syn_responses["color"] == colorterm_dict[i],"count"].sum())/n
        p_total += (p_i * p_j)
    else:
        for j in colorterm_dict[i]:
            p_i = (syn_responses.loc[syn_responses["stimulus"] == i,"count"].sum())/n
            p_j = (syn_responses.loc[syn_responses["color"] == j,"count"].sum())/n
            p_total += (p_i * p_j)

exp_r2=(n*p_total)/matches_possible
print("The expected R2 is: " + str(exp_r2))

# Binomial test of the hypothesis:
# Expected proportion: exp_r2!
p = obs_r2
q = 1 - p
x = int(exp_r2 * n)

result = binomtest(x,n,p,alternative="less")
print(result.pvalue)
print(result.proportion_ci(confidence_level=0.95))
print(result.proportion_estimate)
