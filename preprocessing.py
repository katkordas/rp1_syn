import pandas as pd

df = pd.read_csv("raw_data.csv",encoding="utf-8",sep=",")

# Discarding non-synesthetes based on test-retest consistency cut-off value of <135, based on Rothen et al. (2013)
# Source: https://doi.org/10.1016/j.jneumeth.2013.02.009
# Removing responses for digraphs and trigraphs
syn_responses = df.loc[(df["rothdist"] <= 135) & (df.stimulus.str.len() == 1), ["id","stimulus","rep", "L","u","v", "color_bk"]]

# Removing responses for letters that are not used in the Polish alphabet
syn_responses = syn_responses[~syn_responses.stimulus.isin(["X","V","Q"])]

# Removing outliers using method from Root et al. (2021)
# Source: https://doi.org/10.1016/j.concog.2021.103192 
# We calculate the average CIELuv coordinates for each letter for each participant
# If trial is more than 45 units away from the mean, the trial is removed

ids = list(syn_responses.id.unique())
stimuli = list(syn_responses.stimulus.unique())
reps = list(syn_responses.rep.unique())

for i in ids:
    for s in stimuli:
        avg_L = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s), "L"].mean()
        avg_u = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s), "u"].mean()
        avg_v = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s), "v"].mean()
        for r in reps:
            L_rep = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s) & (syn_responses["rep"] == r), "L"].values[0]
            u_rep = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s) & (syn_responses["rep"] == r), "u"].values[0]
            v_rep = syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s) & (syn_responses["rep"] == r), "v"].values[0]
            # Removing outliers
            if (abs(L_rep - avg_L) >= 45) or abs(u_rep - avg_u) >= 45 or abs(v_rep - avg_v) >= 45:
                syn_responses.drop(syn_responses.loc[(syn_responses["id"] == i) & (syn_responses["stimulus"] == s) & (syn_responses["rep"] == r)].index, inplace=True)

# Saving the preprocessed data
syn_responses.to_csv("syn_no_out.csv")
