import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm

# Reading preprocessed data
syn_responses = pd.read_csv("processed_data.csv")

# All of the hypothesis testing in this file is based on the method from Brang et al. (2011)
# Source: https://doi.org/10.1016/j.neuropsychologia.2011.01.002

# Function that calculates Pearson correlation with Confidence Intervals
# Modified from: https://zhiyzuo.github.io/Pearson-Correlation-CI-in-Python/
def pearsonr_ci(x,y,alpha=0.05): 
    """calculate Pearson correlation along with the confidence interval using scipy and numpy
    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default
    Returns
    -------
    r : float
      Pearson's correlation coefficient
    r_z : float
      Conversion of a Pearson's correlation to a z score using Fisher's transformation
    pval : float
      The p value corresponding to the Pearson's correlation
    lo, hi : float
      The lower and upper bound of confidence intervals"""

    r, p = stats.pearsonr(x,y)
    r_z = np.arctanh(r)
    se = 1/np.sqrt(x.size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    return r, r_z, p, lo_z, hi_z

no_of_synesthetes = len(syn_responses["id"].unique())

# Frequency RF
# Hypothesis: letters that are most often used will be brighter, while more uncommon letters will have lower luminance
# Calculating mean luminance per stimulus per participant
ids = list(syn_responses.id.unique())
stimuli = list(syn_responses.stimulus.unique())
luminance_per_part = syn_responses[["id","stimulus","L"]].groupby(['stimulus']).agg("mean").reset_index()
luminance_per_part.to_csv("luminance_per_participant.csv",encoding="utf-8")
freq_list = pd.read_csv("letter_freq.csv",sep=";")

freq_dict = {}

for i in ids:
    new_df = luminance_per_part.loc[luminance_per_part["id"] == i, ["stimulus", "L"]]
    new_df = new_df.merge(freq_list,on="stimulus")
    corr = pearsonr_ci(new_df["L"],new_df["freq"])
    int_dict = {}
    int_dict['r'] = corr[0]
    int_dict['r_corr'] = corr[1]
    int_dict['p-value'] = norm(0, 1).cdf(-np.absolute(corr[1])) * 2 
    int_dict['low_z'] = corr[3]
    int_dict['high_z'] = corr[4]
    freq_dict[i] = int_dict

freq_df = pd.DataFrame.from_dict(freq_dict,orient='index')
freq_df.to_csv("ordinal_results.csv",encoding="utf-8")

# Hypothesis testing for frequency RF
print(stats.ttest_1samp(freq_df["r_corr"],0))

# VISUAL SIMILARITY
# Based on data generated by neural network
# Hypothesis: There will be a significant association (see Brang et al. 2010) between visual similarity and colour in CIELuv space
dict_per_id = {}
vis_sim_data = syn_responses[["id","stimulus","L","u","v"]].groupby(['id','stimulus']).mean().reset_index()
combs_list = [str(a) + str(b) for idx, a in enumerate(stimuli) for b in stimuli[idx + 1:]]

# Making distance matrix of synaeshetic colours per participant
for i in ids:
    i_df = vis_sim_data.loc[vis_sim_data["id"] == i,["stimulus","L","u","v"]]
    stimuli = list(i_df.stimulus.unique())
    list_of_diff = {}
    for s in stimuli:
        for t in stimuli:
            if s != t:
                comb = str(s) + str(t)
                if comb in combs_list:
                    a = i_df.loc[i_df["stimulus"] == s,["L","u","v"]].to_numpy()
                    b = i_df.loc[i_df["stimulus"] == t,["L","u","v"]].to_numpy()
                    try:
                        sum_sq = np.sum(np.square(b-a))
                        diff = np.sqrt(sum_sq)
                        list_of_diff[comb] = diff
                    except:
                        print(str(s) + " " + str(a))
                        print(str(b) + " " + str(b))
    dict_per_id[i] = list_of_diff

df_attempt = pd.DataFrame.from_dict(dict_per_id, orient='index')
df_attempt.index.name = 'id'
df_attempt = df_attempt.reset_index()
df_final = pd.melt(df_attempt, id_vars='id', var_name='pair', value_name='distance').dropna()
vis_sim = pd.read_csv("vis_sim_nick.csv",sep=";",encoding="utf-8",usecols=["pair","sim"])
vis_corr_dict = {}

for i in ids:
    new_df = df_final.loc[df_final["id"] == i]
    new_df = new_df.merge(vis_sim,on="pair")
    corr = pearsonr_ci(new_df["distance"],new_df["sim"])
    int_dict = {}
    int_dict['r'] = corr[0]
    int_dict['r_corr'] = corr[1]
    int_dict['p-value'] = norm(0, 1).cdf(-np.absolute(corr[1])) * 2 
    int_dict['low_z'] = corr[3]
    int_dict['high_z'] = corr[4]
    vis_corr_dict[i] = int_dict

vis_df = pd.DataFrame.from_dict(vis_corr_dict,orient='index')
vis_df.to_csv("vis_sim_results.csv",encoding="utf-8")

# Hypothesis testing for the visual similarity RF
print(stats.ttest_1samp(vis_df["r_corr"],0))

# SOUND SIMILARITY RF
sound_sim_data = syn_responses[["id","stimulus","L","u","v"]].groupby(['id','stimulus']).mean().reset_index() 

# Making nested dictionary
for i in ids:
    i_df = sound_sim_data.loc[sound_sim_data["id"] == i,["stimulus","L","u","v"]]
    stimuli = list(i_df.stimulus.unique())
    list_of_diff = {}
    for s in stimuli:
        for t in stimuli:
            if s != t:
                comb = str(s) + str(t)
                if comb in combs_list:
                    a = i_df.loc[i_df["stimulus"] == s,["L","u","v"]].to_numpy()
                    b = i_df.loc[i_df["stimulus"] == t,["L","u","v"]].to_numpy()
                    try:
                        sum_sq = np.sum(np.square(b-a))
                        diff = np.sqrt(sum_sq)
                        list_of_diff[comb] = diff
                    except:
                        print(str(s) + " " + str(a))
                        print(str(b) + " " + str(b))
    dict_per_id[i] = list_of_diff

df_attempt = pd.DataFrame.from_dict(dict_per_id, orient='index')
df_attempt.index.name = 'id'
df_attempt = df_attempt.reset_index()
df_final = pd.melt(df_attempt, id_vars='id', var_name='pair', value_name='distance').dropna()

sound_sim = pd.read_csv("sound_sim.csv",sep=";",encoding="utf-8",usecols=["pair","sim"])
sound_corr_dict = {}

for i in ids:
    new_df = df_final.loc[df_final["id"] == i]
    new_df = new_df.merge(sound_sim,on="pair")
    corr = pearsonr_ci(new_df["distance"],new_df["sim"])
    int_dict = {}
    int_dict['r'] = corr[0]
    int_dict['r_corr'] = corr[1]
    int_dict['p-value'] = corr[2]
    int_dict['low_z'] = corr[3]
    int_dict['high_z'] = corr[4]
    sound_corr_dict[i] = int_dict

sound_df = pd.DataFrame.from_dict(sound_corr_dict,orient='index')
sound_df.to_csv("sound_sim_results.csv",encoding="utf-8")

# Hypothesis testing for sound similarity
print(stats.ttest_1samp(sound_df["r_corr"],0))
