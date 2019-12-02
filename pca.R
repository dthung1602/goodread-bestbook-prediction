# Title     : PCA
# Created by: hung
# Created on: 02/12/2019

library(dplyr)
library(ggplot2)
library(corrgram)

all_data=read.table("result.csv", sep=",", quote="\"", comment.char = "", header=TRUE)
data_to_be_reduced = all_data %>% select(-book_id,-year,-genre,-vote,-rank,-debut_vote,-debut_rank,-title)
