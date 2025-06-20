library(tidyverse)
library(scales)
library(tikzDevice)
library(ggpubr)
library(RColorBrewer)

options(tikzLatexPackages = c(getOption("tikzLatexPackages"),
                              "\\usepackage{siunitx}",
                              "\\sisetup{group-separator = {,}}"))

# df <- read.csv("../results/processed/results_with_counts.csv")
# df$count <- NULL
# write.csv(df, "../results/processed/results.csv")

df <- read.csv("../results/processed/results.csv")
df$compilation.time <- df$compilation.time / 1000
df$inference.time <- df$inference.time / 1000
df$time <- df$compilation.time + df$inference.time
df$algorithm[df$algorithm == "bfs"] <- "\\textsc{Crane2-BFS}"
df$algorithm[df$algorithm == "greedy"] <- "\\textsc{Crane2-Greedy}"
df$algorithm[df$algorithm == "fastwfomc"] <- "\\textsc{FastWFOMC}"
df$algorithm[df$algorithm == "forclift"] <- "\\textsc{ForcLift}"
df$sequence[df$sequence == "bijections"] <- "Bijections"
df$sequence[df$sequence == "friends"] <- "Friends \\& Smokers"
df$sequence[df$sequence == "functions"] <- "Functions"
df <- df[df$domain.size > 1,]
dark2_colors <- brewer.pal(8, "Dark2")

# df %>% group_by(algorithm, sequence) %>%
#   summarize(compilation.time = max(compilation.time))

# Sanity check: differences between max and min counts as a percentage of the
# min count
# differences <- df %>% group_by(sequence, domain.size) %>%
#   summarise(diff = 100 * (max(count) - min(count)) / min(count))

tikz(file = "../doc/paper/plot.tex", width = 5, height = 2,
     standAlone = TRUE)
ggplot(df, aes(domain.size, time, color = algorithm, linetype = algorithm,
               shape = algorithm)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(trans = log2_trans(),
                     breaks = c(32, 4096, 524288, 67108864),
                     labels = c("$2^{5}$", "$2^{12}$", "$2^{19}$",
                                "$2^{26}$")) +
  scale_y_continuous(trans = log2_trans()) +
  annotation_logticks(sides = "bl", colour = "#b3b3b3", base = 2) +
  ylab("Total runtime (s)") +
  xlab("Domain size") +
  labs(color = "", linetype = "", shape = "") +
  theme_grey(base_size = 9) +
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  facet_wrap(vars(sequence))
dev.off()

tikz(file = "../doc/talk/bijections.tex",
     width = 4.25, height = 3, standAlone = TRUE)
ggplot(df[df$sequence == "Bijections",],
       aes(domain.size, time, color = algorithm, linetype = algorithm,
           shape = algorithm)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(trans = log2_trans(), breaks = c(8, 64, 512, 4096),
                     labels = c("$2^{3}$", "$2^{6}$", "$2^{9}$", "$2^{12}$")) +
  scale_y_continuous(trans = log2_trans()) +
  annotation_logticks(sides = "bl", colour = "#b3b3b3", base = 2) +
  ylab("Total runtime (s)") +
  xlab("Domain size") +
  labs(color = "", linetype = "", shape = "") +
  theme_bw(base_size = 9) +
  theme(legend.position = "bottom") +
  scale_color_manual(values = c(dark2_colors[1], dark2_colors[3])) +
  scale_linetype_manual(values = c(1, 5)) +
  scale_shape_manual(values = c(16, 15)) +
  geom_segment(aes(x = 64, xend = 4096, y = 88, yend = 88),
               colour = "darkgray", arrow = arrow(ends = "both"),
               show.legend = FALSE) +
  geom_label(aes(label = str_wrap("$64 \\times$"), x = 512, y = 88),
             colour = "darkgray")
dev.off()

tikz(file = "../doc/talk/friends.tex",
     width = 4.25, height = 3, standAlone = TRUE)
ggplot(df[df$sequence == "Friends \\& Smokers",],
       aes(domain.size, time, color = algorithm, linetype = algorithm,
           shape = algorithm)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(trans = log2_trans(), breaks = c(8, 64, 512, 4096),
                     labels = c("$2^{3}$", "$2^{6}$", "$2^{9}$", "$2^{12}$")) +
  scale_y_continuous(trans = log2_trans()) +
  annotation_logticks(sides = "bl", colour = "#b3b3b3", base = 2) +
  ylab("Total runtime (s)") +
  xlab("Domain size") +
  labs(color = "", linetype = "", shape = "") +
  theme_bw(base_size = 9) +
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  geom_segment(aes(x = 1024, xend = 8192, y = 1794, yend = 1794),
               colour = "darkgray", arrow = arrow(ends = "both"),
               show.legend = FALSE) +
  geom_label(aes(label = str_wrap("$8 \\times$"), x = 2896, y = 1794),
             colour = "darkgray")
dev.off()

tikz(file = "../doc/talk/functions.tex",
     width = 4.25, height = 3, standAlone = TRUE)
ggplot(df[df$sequence == "Functions",],
       aes(domain.size, time, color = algorithm, linetype = algorithm,
           shape = algorithm)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(trans = log2_trans(),
                     breaks = c(8, 64, 512, 4096, 32768, 262144, 2097152,
                                16777216, 134217728),
                     labels = c("$2^{3}$", "$2^{6}$", "$2^{9}$", "$2^{12}$",
                                "$2^{15}$", "$2^{18}$", "$2^{21}$", "$2^{24}$",
                                "$2^{27}$")) +
  scale_y_continuous(trans = log2_trans()) +
  annotation_logticks(sides = "bl", colour = "#b3b3b3", base = 2) +
  ylab("Total runtime (s)") +
  xlab("Domain size") +
  labs(color = "", linetype = "", shape = "") +
  theme_bw(base_size = 9) +
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  geom_segment(aes(x = 128, xend = 67108864, y = 222.261, yend = 222.261),
               colour = "darkgray", arrow = arrow(ends = "both"),
               show.legend = FALSE) +
  geom_label(aes(label = str_wrap("$> \\num{500000} \\times$"), x = 92682,
                 y = 222.261),
             colour = "darkgray")
dev.off()

# ============== DEGREE FINDING (not doing this right now) ================

K <- 5
degree <- 10

df1 <- df[df$algorithm == "\\textsc{FastWFOMC}" & df$sequence == "bijections",]
df1 <- df[df$algorithm == "\\textsc{FastWFOMC}" & df$sequence == "functions",]

df.shuffled <- df1[sample(nrow(df1)),]
folds <- cut(seq(1,nrow(df.shuffled)),breaks=K,labels=FALSE)
mse <- matrix(data=NA,nrow=K,ncol=degree)
for(i in 1:K){
  testIndexes <- which(folds==i,arr.ind=TRUE)
  testData <- df.shuffled[testIndexes, ]
  trainData <- df.shuffled[-testIndexes, ]
  for (j in 1:degree){
    fit.train = lm(time ~ poly(domain.size,j), data=trainData)
    fit.test = predict(fit.train, newdata=testData)
    mse[i,j] = mean((fit.test-testData$time)^2)
  }
}
means <- colMeans(mse)
means

best <- lm(time ~ poly(domain.size, 3), data = df1)
summary(best)

linear <- lm(time ~ n, data = head(df1, TRAINING_N))

#cubic <- lm(time ~ poly(n, 3), data = head(df, TRAINING_N))
#exponential <- lm(log(time) ~ n, data = df)
#summary(exponential)
#exponential.df <- data.frame(n = df$n, time = exp(fitted(exponential)))

colours <- c("#1b9e77", "#d95f02")
for_labels <- data.frame(x = max(df$n),
                         y = c(predict(best, data.frame(n = max(df$n))),
                               predict(linear, data.frame(n = max(df$n)))),
                         label = c(NAME, "Linear"))
tikz(file = "../../doc/paper/plot.tex", width = 3.31, height = 2.05,
     standAlone = TRUE)
ggplot(df, aes(x = n, y = time)) +
  geom_point() +
  stat_smooth(method = 'lm', se = FALSE, formula = y ~ poly(x, BEST_DEGREE),
              aes(color = NAME), fill = colours[2]) +
  stat_smooth(method = 'lm', formula = y ~ x, data = head(df, TRAINING_N),
              se = FALSE, fullrange = TRUE, aes(color = "Linear")) +
  xlab('Domain size') +
  ylab('Runtime (s)') +
  theme_set(theme_gray(base_size = 9)) +
  theme_minimal() +
  scale_color_manual(name = "Model fit", values = colours, guide = FALSE) +
  geom_label_repel(data = for_labels, aes(x = x, y = y, label = label,
                                          color = label),
                   min.segment.length = Inf)
dev.off()

tikz(file = "../../doc/talks/3_long/plot.tex", width = 2.13, height = 1.32,
     standAlone = TRUE)
ggplot(df, aes(x = n, y = time)) +
  geom_point() +
  stat_smooth(method = 'lm', se = FALSE, formula = y ~ poly(x, BEST_DEGREE),
              aes(color = NAME), fill = colours[2]) +
  xlab('Domain size') +
  ylab('Runtime (s)') +
  theme_set(theme_gray(base_size = 9)) +
  theme_minimal() +
  scale_color_manual(name = "Model fit", values = colours, guide = FALSE)
dev.off()
