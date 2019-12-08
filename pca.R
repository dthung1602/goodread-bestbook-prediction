library(dplyr)
library(ggplot2)
library(corrgram)
library(xgboost)

# read data
all_data <- read.table("result.csv", sep = ",", quote = "\"", comment.char = "", header = TRUE)

# vote has exponential distribution -> convert to log(vote)
all_data$vote = log(all_data$vote)

# split data to 2019 and pre-2019
data_before_2019 <-  all_data %>%
  select(-book_id, -genre, -rank, -title) %>%
  filter(year != 2019) %>%
  select(-year)

# view corelation of features
corrgram(data_before_2019[, 1:10], lower.panel = panel.cor, upper.panel = panel.pie, cor.method = "pearson")
corrgram(data_before_2019[, 10:20], lower.panel = panel.cor, upper.panel = panel.pie, cor.method = "pearson")

# view corelation of features to vote
cor_matrix <- cor(data_before_2019, data_before_2019, method = "pearson")
column_count <- ncol(cor_matrix)
vote_cor <- data.frame(cor = cor_matrix[2:column_count, 1], varn = names(cor_matrix[2:column_count, 1]))
sorted_vote_cor <- vote_cor %>%
  mutate(cor_abs = abs(cor)) %>%
  arrange(desc(cor_abs))
plot(sorted_vote_cor$cor_abs, type = "l")

# perform pca
xv <- all_data %>%
  select(-book_id, -genre, -rank, -title, -vote, -year)
pca <- prcomp(xv, scale. = T, center = T)
cumulative_proportion <- summary(pca)$importance[3,]
plot(cumulative_proportion, type = 'l', col = 'darkblue')

# select features: 124 -> 85%, 134 -> 90%, 190 -> 100%
new_pc <- data.frame(pca$x[, 1:134])
# to use orignal data (i.e. skip pca), uncomment the following line
# new_pc <-  data.frame(xv)

# view corelations of new components
new_pc_cor_matrix <- cor(new_pc, new_pc, method = 'pearson')
corrgram(new_pc[, 1:10], lower.panel = panel.cor, upper.panel = panel.pie, cor.method = "pearson")
corrgram(new_pc[, 10:20], lower.panel = panel.cor, upper.panel = panel.pie, cor.method = "pearson")

# split data to 2019 and before 2019
new_pc$vote <- all_data$vote
new_pc$year <- all_data$year
data_before_2019 <- new_pc %>% filter(year != 2019) %>% select(-year)
data_2019 <- new_pc %>% filter(year == 2019) %>% select(-year, -vote)

# rondomly shuffle rows in data before 2019
set.seed(123456)
row <- sample(nrow(data_before_2019))
data_before_2019 <- data_before_2019[row,]

# split data to training data and testing data
row_count <- nrow(data_before_2019)
smp_size <- floor(0.8 * row_count)
train_data <- data_before_2019[1:smp_size, ] %>% select(-vote)
train_data_vote <- data_before_2019[1:smp_size, ] %>% select(vote)
test_data <- data_before_2019[(smp_size + 1):row_count, ]%>% select(-vote)
test_data_vote <- data_before_2019[(smp_size + 1):row_count, ]%>% select(vote)

# train xgboost model
total_time <- 0
for (i in c(0, 1, 2, 3)) {
  start_time <- Sys.time()
  model <- xgboost(data = as.matrix(train_data),
                   label = as.matrix(train_data_vote),
                   nfold = 15,
                   eta = 0.01,
                   nrounds = 7500,
                   gamma = 7.5,
                   max_depth = 6,
                   subsample = 0.7,
                   colsample_bytree = 0.7,
                   seed = 123,
                   verbose = FALSE,
                   nthread = 4)
  elapsed_time <- Sys.time() - start_time
  print(elapsed_time)
  if (i > 0)
    total_time <- total_time + elapsed_time
}
print("TOTAL: ")
print(total_time)

# use xgboost model to predict
predicted_vote <- predict(model, newdata = as.matrix(test_data))

# calculate root mean square error (RMSE)
pv <- as.data.frame(predicted_vote)
d <- pv$predicted_vote - test_data_vote
d <- d * d
sqrt(mean(d$vote))

# predict 2019 result
vote_predict_2019 <- predict(model, newdata = as.matrix(data_2019))
result_2019 <- all_data %>%
  filter(year == 2019) %>%
  select(genre, book_id, title) %>%
  mutate(predicted_vote = exp(vote_predict_2019)) %>%
  group_by(genre) %>%
  mutate(rank = order(order(predicted_vote, decreasing = TRUE))) %>%
  arrange(genre, rank)

write.csv(result_2019, "predict_result_2019.csv", quote = TRUE, sep = ",")
