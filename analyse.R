df <- read.csv("results.csv")
summary(df)

n <- length(df$inference.time)
sort(df$inference.time, decreasing = TRUE)
