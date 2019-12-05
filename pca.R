# Title     : PCA
# Created by: hung
# Created on: 02/12/2019

library(dplyr)
library(ggplot2)
library(corrgram)

all_data <- read.table("result.csv", sep = ",", quote = "\"", comment.char = "", header = TRUE)
reduced_data <- all_data %>%
  select(-book_id, -genre, -rank, -title)

data_2019 <- reduced_data %>%
  filter(year == 2019) %>%
  select(-year)
data_before_2019 <- reduced_data %>%
  filter(year != 2019) %>%
  select(-year)

cor_matrix <- cor(data_before_2019, data_before_2019, method = "pearson")
column_count <- ncol(cor_matrix)
vote_cor <- data.frame(cor = cor_matrix[2:column_count, 1], varn = names(cor_matrix[2:column_count, 1]))
sorted_vote_cor <- vote_cor %>%
  mutate(cor_abs = abs(cor)) %>%
  arrange(desc(cor_abs))
plot(sorted_vote_cor$cor_abs, type = "l")

xv <- data_before_2019 %>% select(-vote)
pca <- prcomp(xv, scale. = T, center = T)
plot(pca, type = "l")

new_pc <- data.frame(pca$x)[1:7]
new_pc$vote <- data_before_2019$vote

smp_size <- floor(0.8 * nrow(new_pc))
set.seed(123456)
train_ind <- sample(seq_len(nrow(new_pc)), size = smp_size)

train_data <- new_pc[1:smp_size,]
test_data <- new_pc[(smp_size + 1):nrow(new_pc),]

model <- lm(vote ~ ., train_data)
vote_predict <- predict(model, newdata = test_data)
vp <- as.data.frame(vote_predict)

d <- vp$vote_predic - test_data$vote
df <- mean(d * d)


