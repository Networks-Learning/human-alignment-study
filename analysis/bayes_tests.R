
library(brms)
library(tidyverse)
library(tidybayes)
library(broom)
library(broom.mixed)
library(ggplot2)
library(rstanarm)
library(bayesplot)
library(reshape2)
library(latex2exp)
library(tikzDevice)



options(dplyr.summarise.inform = F)

# Path for results and figures
result_path <- "~/Desktop/Code/HAC_experiments_git/analysis/figures/"
output_path <- "~/Desktop/Code/HAC_experiments_git/analysis/outputs/"

# Read the experiment data
data_match <- read.csv("~/Desktop/Code/HAC_experiments_git/analysis/data/df_brms_match.csv")
# ###### TEST 1 ######
# # test whether the effect of alignment is positive on the conditional matching rate

#filter data_match to only include groups A, B and C
data_test1 <- data_match %>% filter(level_name %in% c("level_B", "level_A", "level_C")) %>% 
  mutate(level_name = factor(level_name, levels = c("level_B", "level_A", "level_C")))

Prior <- set_prior("normal(0,1)", class = "b")

binomial_model1 <- brm(data = data_test1, 
                            family = binomial,
                            final_matchsum | trials(final_matchcount) ~ 0 + level_name * initial_match + (1 | participant_id) ,
                            prior = Prior,
                            sample_prior = TRUE,
                            refresh = 0,
                            seed = 42,
                            iter = 5000,
                            file = "analysis/models/bayes_test1_logit_noIntercept")

# sample from posterior
post <- as_draws_df(binomial_model1, variable = "^b_", regex = TRUE)
# rename columns
post <- post %>% rename_at(vars(contains(":")), ~ gsub(":", "", .))
# inverse logit transformation
post %>% 
  mutate(p_B = exp(b_level_namelevel_B) / (1 + exp(b_level_namelevel_B)),
         p_A = exp(b_level_namelevel_A) / (1 + exp(b_level_namelevel_A)),
         p_C = exp(b_level_namelevel_C) / (1 + exp(b_level_namelevel_C))) -> post
post %>% 
  mutate(p_B_1 = exp(b_level_namelevel_B + b_initial_match) / (1 + exp(b_level_namelevel_B + b_initial_match)),
         p_A_1 = exp( b_level_namelevel_A + b_initial_match + b_level_namelevel_Ainitial_match) / (1 + exp( b_level_namelevel_A + b_initial_match + b_level_namelevel_Ainitial_match)),
         p_C_1 = exp( b_level_namelevel_C + b_initial_match + b_level_namelevel_Cinitial_match) / (1 + exp( b_level_namelevel_C + b_initial_match + b_level_namelevel_Cinitial_match))) -> post

# melt and plot the posterior of the binomial parameters
post_melt <- melt(post) 
tikz(file=paste(result_path, "bayes_ABC_initialmatch_0.tex", sep=""),  width=10, height=5 )
ggplot(post_melt %>% filter(variable %in% c("p_B", "p_A", "p_C")), aes(value, fill = variable)) + geom_density(alpha = 0.25)+xlab("$P( Q'_i=1\\, |\\, Q_i=0)$")+ylab("Density")+scale_fill_discrete(labels=c('Level B', 'Level A', 'Level C'))+ theme_minimal(base_size = 30)+theme(legend.title = element_blank(),legend.position=c(.85,.75))
dev.off()

tikz(file=paste(result_path, "bayes_ABC_initialmatch_1.tex", sep=""),  width=10, height=5 )
ggplot(post_melt %>% filter(variable %in% c("p_B_1", "p_A_1", "p_C_1")), aes(value, fill = variable)) + geom_density(alpha = 0.25)+xlab("$P( Q'_i=1\\, |\\, Q_i=1)$")+ylab("Density")+scale_fill_discrete(labels=c('Level B', 'Level A', 'Level C'))+ theme_minimal(base_size = 30)+theme(legend.title = element_blank(),legend.position=c(.15,.75))
dev.off()

# check the model
tikz(file=paste(result_path, "pp_check_logit1.tex", sep=""),  width=10, height=5 )
pp_check(binomial_model1)
dev.off()

# loo and model summary
sink(paste(output_path, "test1_ABC_results.txt", sep=""))
summary(binomial_model1)
get_prior(binomial_model1, data = data_test1)
loo(binomial_model1)
h1 <- hypothesis(binomial_model1, c("exp(level_namelevel_A) / (1 + exp(level_namelevel_A))>exp(level_namelevel_B) / (1 + exp(level_namelevel_B))",
                                  "exp(level_namelevel_A+initial_match+level_namelevel_A:initial_match) / (1 + exp(level_namelevel_A+initial_match+level_namelevel_A:initial_match))>exp(level_namelevel_B+initial_match) / (1 + exp(level_namelevel_B+initial_match))",
                                  "exp(level_namelevel_C) / (1 + exp(level_namelevel_C))>exp(level_namelevel_B) / (1 + exp(level_namelevel_B))",
                                  "exp(level_namelevel_C+initial_match+level_namelevel_C:initial_match) / (1 + exp(level_namelevel_C+initial_match+level_namelevel_C:initial_match))>exp(level_namelevel_B+initial_match) / (1 + exp(level_namelevel_B+initial_match))"))
h1
sink()  

###### TEST 2 ######
# test whether the effect of alignment through post-orocessing is positive on the conditional matching rate

#filter data_match to only include groups B and BP
data_test2 <- data_match %>% filter(level_name %in% c("level_B", "level_BP")) %>% 
  mutate(level_name = factor(level_name, levels = c("level_B", "level_BP")))


Prior <- set_prior("normal(0,1)", class = "b")

binomial_model2 <- brm(data = data_test2, 
                            family = binomial,
                            final_matchsum | trials(final_matchcount) ~ 0 + level_name * initial_match + (1 | participant_id) ,
                            prior = Prior,
                            sample_prior = TRUE,
                            refresh = 0,
                            seed = 42,
                            control = list(max_treedepth = 15, adapt_delta = 0.99),
                            iter = 5000,
                            file = "analysis/models/bayes_test2_logit_noIntercept")                        

# sample from posterior
post <- as_draws_df(binomial_model2, variable = "^b_", regex = TRUE)
# rename columns
post <- post %>% rename_at(vars(contains(":")), ~ gsub(":", "", .))
# inverse logit transformation
post %>% 
  mutate(p_B = exp(b_level_namelevel_B) / (1 + exp(b_level_namelevel_B)),
         p_BP = exp(b_level_namelevel_BP) / (1 + exp(b_level_namelevel_BP))) -> post
post %>% 
  mutate(p_B_1 = exp(b_level_namelevel_B + b_initial_match) / (1 + exp(b_level_namelevel_B + b_initial_match)),
         p_BP_1 = exp( b_level_namelevel_BP + b_initial_match + b_level_namelevel_BPinitial_match) / (1 + exp( b_level_namelevel_BP + b_initial_match + b_level_namelevel_BPinitial_match))) -> post


# melt and plot the posterior of the binomial parameters

post_melt <- melt(post) 

tikz(file=paste(result_path, "bayes_BBP_initialmatch_0.tex", sep=""), width=10, height=5 )
ggplot(post_melt %>% filter(variable %in% c("p_B", "p_BP")), aes(value, fill = variable)) + geom_density(alpha = 0.25)+xlab("$P( Q'_i=1\\, |\\, Q_i=0)$")+ylab("Density")+scale_fill_discrete(labels=c('Level B', 'Level BP'))+ theme_minimal(base_size = 30)+theme(legend.title = element_blank(),legend.position=c(.85,.75))
dev.off()

tikz(file=paste(result_path, "bayes_BBP_initialmatch_1.tex", sep=""),  width=10, height=5 )
ggplot(post_melt %>% filter(variable %in% c("p_B_1", "p_BP_1")), aes(value, fill = variable)) + geom_density(alpha = 0.25)+xlab("$P( Q'_i=1\\, |\\, Q_i=1)$")+ylab("Density")+scale_fill_discrete(labels=c('Level B', 'Level BP'))+ theme_minimal(base_size = 30)+theme(legend.title = element_blank(),legend.position=c(.15,.75))
dev.off()

# check the model
tikz(file=paste(result_path, "pp_check_logit2.tex", sep=""),  width=10, height=5 )
pp_check(binomial_model2)
dev.off()

# loo and model summary
sink(paste(output_path, "test2_BBP_results.txt", sep=""))
summary(binomial_model2)
get_prior(binomial_model2, data = data_test2)
loo(binomial_model2)
h1 <- hypothesis(binomial_model2, c("exp(level_namelevel_BP) / (1 + exp(level_namelevel_BP))>exp(level_namelevel_B) / (1 + exp(level_namelevel_B))","exp(level_namelevel_BP+initial_match+level_namelevel_BP:initial_match) / (1 + exp(level_namelevel_BP+initial_match+level_namelevel_BP:initial_match))>exp(level_namelevel_B+initial_match) / (1 + exp(level_namelevel_B+initial_match))"))
h1
sink()
