import numpy as np
import seaborn as sns
import pandas as pd
# import matplotlib
# matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
# from scipy.optimize import linprog
from scipy.optimize import LinearConstraint
from scipy.optimize import milp


def get_best_monotone_utility(df_util, df_count, name_conf="dm_conf", name_prob="joint_prob", name_conf_numeric="dm_conf_numeric"):
    dm_conf_dict = {"very low": 0, "low":1 , "high":2, "very high":3}
    df_util[name_conf_numeric] = df_util.apply(lambda x: dm_conf_dict[x[name_conf]], axis=1)
    AI_conf = (np.arange(0,13)/13*100).round(0).astype(int)

    mono_constraints = []
    unique_choice =[]
    for i, row_i in df_util.iterrows():
        choice = np.zeros(2*df_util.shape[0]) 
        choice[i] = 1 
        choice[df_util.shape[0]+i] = 1 
        unique_choice += [choice]

        for j, row_j in df_util.iterrows():
            if (row_i[name_conf_numeric]<= row_j[name_conf_numeric]) & (row_i["AI_conf"]<= row_j["AI_conf"]):
                constraint = np.zeros(2*df_util.shape[0]) 
                constraint[i] = 1
                constraint[j] = -1
                mono_constraints += [constraint]
    

    A = np.array(unique_choice+mono_constraints)
    b_lb = np.concatenate((np.ones(len(unique_choice)), -np.ones(len(mono_constraints))))
    b_ub = np.concatenate((np.ones(len(unique_choice)), np.zeros(len(mono_constraints))))
    
    constraints = LinearConstraint(A=A, lb=b_lb, ub=b_ub)
    # print(df_util[name_prob])
    # print(df_count["count"]/df_count["count"].sum())
    # print(df_util[name_prob]*df_count["count"])
    c =  np.concatenate((df_util[name_prob]*(df_count["count"]/df_count["count"].sum()), (100-df_util[name_prob])*(df_count["count"]/df_count["count"].sum()) ))

    solve = milp(c=-c, constraints=constraints, integrality=np.ones_like(c))
    # solve=linprog(-c, A_eq= A_eq, b_eq=b_eq, A_ub=A_ub, b_ub = b_ub, bounds=(0,2))
    
    print("Get best monotone policy successful: ", solve.success)
    df_util["best_monotone_decision"]= solve.x[0:df_util.shape[0]]
    # print(solve.x)
    # print(df_util)
    return df_util



def compute_utility(df_utility, center=True): 

    df_helper = df_utility.pivot_table(
                        columns=["dm_conf",'AI_conf'], aggfunc='mean', values="true_prob",dropna=True).unstack().reset_index().fillna(value=0).rename(columns={0:'joint_prob'})
    #drop column level_2
    df_helper.drop("level_2", inplace=True, axis=1)
    # print(df_humanAI)
    df_count = df_utility.pivot_table(
                        columns=["dm_conf",'AI_conf'], aggfunc='count', values="true_prob",dropna=True).unstack().reset_index().fillna(value=0).rename(columns={0:'count'})
    #drop column level_2
    df_count.drop("level_2", inplace=True, axis=1)
        
    df_helper = get_best_monotone_utility(df_helper, df_count, name_conf="dm_conf", name_prob="joint_prob", name_conf_numeric="dm_conf_numeric")


    df_utility = df_utility.join(df_helper.set_index(["dm_conf","AI_conf"]), on=["dm_conf","AI_conf"])
    
    df_utility["best_joint_decision"] = (df_utility["joint_prob"]>=50).astype('int')
    df_utility["best_joint_utility"] = df_utility["best_joint_decision"]*df_utility["true_prob"] + (1-df_utility["best_joint_decision"])*(100-df_utility["true_prob"])
    df_utility["best_monotone_utility"] = df_utility["best_monotone_decision"]*df_utility["true_prob"] + (1-df_utility["best_monotone_decision"])*(100-df_utility["true_prob"])

    if center==False:
        return df_utility[["best_joint_decision","best_monotone_decision", "best_joint_utility", "best_monotone_utility"]]

    df_helper_center = df_utility.pivot_table(
                        columns=["shown_conf",'AI_conf'], aggfunc='mean', values="true_prob",dropna=True).unstack().reset_index().fillna(value=0).rename(columns={0:'joint_shown_prob'})
    #drop column level_2
    df_helper_center.drop("level_2", inplace=True, axis=1)
    # print(df_humanAI)

    df_center_count = df_utility.pivot_table(
                        columns=["shown_conf",'AI_conf'], aggfunc='count', values="true_prob",dropna=True).unstack().reset_index().fillna(value=0).rename(columns={0:'count'})
    #drop column level_2
    df_center_count.drop("level_2", inplace=True, axis=1)
        
    df_helper_center = get_best_monotone_utility(df_helper_center, df_center_count, name_conf="shown_conf", name_prob="joint_shown_prob", name_conf_numeric="shown_conf_numeric")
    df_helper_center.rename(columns={"best_monotone_decision":"best_monotone_center_decision"}, inplace=True)

    df_utility = df_utility.join(df_helper_center.set_index(["shown_conf","AI_conf"]), on=["shown_conf","AI_conf"])

    df_utility["best_joint_center_decision"] = df_utility["joint_shown_prob"]>=50
        
    df_utility["best_joint_center_utility"] = df_utility["best_joint_center_decision"]*df_utility["true_prob"] + (1-df_utility["best_joint_center_decision"])*(100-df_utility["true_prob"])
    df_utility["best_monotone_center_utility"] = df_utility["best_monotone_center_decision"]*df_utility["true_prob"] + (1-df_utility["best_monotone_center_decision"])*(100-df_utility["true_prob"])

    # df_utility["best_joint_utility"] = df_utility["best_joint_decision"]*(-100+2*df_utility["true_prob"]) + (1-df_utility["best_joint_decision"])*(100-2*df_utility["true_prob"])
    # df_utility["best_monotone_utility"] = df_utility["best_monotone_decision"]*(-100+2*df_utility["true_prob"]) + (1-df_utility["best_monotone_decision"])*(100-2*df_utility["true_prob"])
    
    # df_utility["best_joint_center_utility"] = df_utility["best_joint_center_decision"]*(-100+2*df_utility["true_prob"]) + (1-df_utility["best_joint_center_decision"])*(100-2*df_utility["true_prob"])
    # df_utility["best_monotone_center_utility"] = df_utility["best_monotone_center_decision"]*(-100+2*df_utility["true_prob"]) + (1-df_utility["best_monotone_center_decision"])*(100-2*df_utility["true_prob"])


    return df_utility[["best_joint_decision","best_monotone_decision", "best_joint_utility", "best_monotone_utility","best_joint_center_decision","best_monotone_center_decision","best_joint_center_utility","best_monotone_center_utility"]]

def alignment_plot(df_center_responses_level, conf_levels):
    fig, ax = plt.subplots(figsize=(15, 4))
    df_count = df_center_responses_level.pivot_table(#index='dm_conf', 
                        columns=['dm_conf','AI_conf'], aggfunc='count', fill_value=0, values="true_prob",dropna=False).unstack().reset_index().fillna(value=0).rename(columns={0:'count'})
    # print(df_count)
    ax= sns.barplot(x='AI_conf', y='true_prob', hue='dm_conf', estimator=np.nanmean, errorbar=('ci', 90), err_kws={'linewidth': 0.2}, capsize=.12, hue_order=conf_levels, data=df_center_responses_level, palette="husl")
    for container, conf in zip(ax.containers, conf_levels):
        # print(df_count[df_count["dm_conf"]==conf]["count"])
        ax.bar_label(container, labels=df_count[(df_count["dm_conf"]==conf) & (df_count["count"]!=0)]["count"], fmt='%.1f')
    ax.axhline(y=50, color='r', linestyle='dotted')

    # set legend title to "DM confidence" and 
    #display legend on the left upper corner inside the plot
    ax.legend(loc='upper left', title="DM confidence")
    ax.set_xlabel("AI confidence")
    ax.set_ylabel("True probability")
    plt.show()

#computes expected and average alignment error
def check_alignment(data, min_datapoints=15):
        #compute max and average alignment violations
        max_aligment = 0.0
        sum_aligment = 0.0
        num_summants = 0.0
        disaligned_cells = set({})


        df_cell_prob = data.pivot_table(index='dm_conf_numeric', 
                        columns=['AI_conf'], aggfunc='mean', fill_value=0, values="true_prob",dropna=False)#.unstack()#.reset_index().fillna(value=0).rename(columns={0:'count'})
        df_cell_prob = df_cell_prob/100
        # print(df_cell_prob)

        df_cell_mass = data.pivot_table(index='dm_conf_numeric', 
                        columns=['AI_conf'], aggfunc='count', fill_value=0, values="true_prob",dropna=False)#.unstack()#.reset_index().fillna(value=0).rename(columns={0:'count'})
        # print(df_cell_mass)

        for h in range(df_cell_prob.columns.shape[0]):
            for b in range(df_cell_prob.index.shape[0]):
                for h1 in range(h+1):
                    for b1 in range(b+1):
                        # check misalignment of the pair of cells if enough datapoints in each cells
                        if (df_cell_mass.iat[b,h]>=min_datapoints) & (df_cell_mass.iat[b1,h1]>=min_datapoints):
                            alignment = max(0.0, df_cell_prob.iat[b1,h1] - df_cell_prob.iat[b,h] )
                            max_aligment = max(max_aligment, alignment)
                            num_summants +=1
                            if alignment > 0.0:
                                sum_aligment += alignment
                                disaligned_cells |= {(df_cell_prob.index[b],df_cell_prob.columns[h]),(df_cell_prob.index[b1],df_cell_prob.columns[h1])}
                                
        if num_summants > 0: 
            avg_alignment = sum_aligment / num_summants
        else:
            avg_alignment = 0.0 
        
        mae = max_aligment 
        eae = avg_alignment

        return(round(eae,5), round(mae,2))

#computes expected and maximum calibration error
def check_calibration(data):

        df_cell_prob = data.pivot_table(index='dm_conf_numeric', 
                        columns=['AI_conf'], aggfunc='mean', fill_value=0, values="true_prob",dropna=False).unstack().reset_index().fillna(value=0).rename(columns={0:'mean'})
        df_cell_prob[["mean","AI_conf"]] = df_cell_prob[["mean","AI_conf"]]/100
        # print(df_cell_prob)

        df_cell_mass = data.pivot_table(index='dm_conf_numeric', 
                        columns=['AI_conf'], aggfunc='count', fill_value=0, values="true_prob",dropna=False).unstack().reset_index().fillna(value=0).rename(columns={0:'count'})
        # print(df_cell_mass)

        total_mass= df_cell_mass["count"].sum()

        ece = df_cell_mass["count"]/total_mass * abs(df_cell_prob["mean"]-df_cell_prob["AI_conf"])
        ece = ece.sum(axis=0)

        print(ece)

        # prob_true, prob_pred = calibration_curve(self.task_data['y'], self.task_data['b'], n_bins=self.b_bins)
        # abs_diff = pd.DataFrame(data={'b_mass': prob_true-prob_pred})
        # abs_diff['b_mass'] = abs_diff['b_mass'].abs()

        # #compute maximum calibration error (MCE)
        # mce = abs_diff['b_mass'].max()

        # #compute expected calibration error (ECE)
        # df_density = self.df_cell_mass / self.df_cell_mass.sum().sum()
        # b_bin_mass = df_density.sum(axis=1)

        # ece = b_bin_mass * abs(prob_true-prob_pred)
        # ece = ece.sum(axis=0)

        # return(ece, mce)