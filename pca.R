# Title     : PCA
# Created by: hung
# Created on: 02/12/2019

library(dplyr)
library(ggplot2)
library(corrgram)

all_data <- read.table("result.csv", sep = ",", quote = "\"", comment.char = "", header = TRUE)
data_to_be_reduced <- all_data %>%
  select(-book_id, -year, -genre, -rank, -debut_vote, -debut_rank, -title)

cor_matrix <- cor(data_to_be_reduced, data_to_be_reduced, method = "pearson")
column_count <- ncol(cor_matrix)
vote_cor <- data.frame(cor = cor_matrix[2:column_count, 1], varn = names(cor_matrix[2:column_count, 1]))
sorted_vote_cor <- vote_cor %>%
  mutate(cor_abs = abs(cor)) %>%
  arrange(desc(cor_abs))
plot(sorted_vote_cor$cor_abs, type = "l")

xv <- data_to_be_reduced %>% select(-vote)
pca <- prcomp(xv, scale. = T, center = T)
plot(pca, type = "l")

data.frame(pca$x)
