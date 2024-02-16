library(tidyverse)
library(scales)

TIMEOUT <- 60
breaks <- c(0.3, 1, 3, 10, 30, 60) # TODO: update this and TIMEOUT later
df <- read.csv("results.csv")
df$algorithm[df$algorithm == "bfs"] <- "Crane-BFS" # TODO: make these \textsc{}
df$algorithm[df$algorithm == "greedy"] <- "Crane-Greedy"
df$algorithm[df$algorithm == "forclift"] <- "ForcLift"
algorithms <- sort(unique(df$algorithm))

# Random stuff
# summary(df)
# n <- length(df$inference.time)
# sort(df$inference.time, decreasing = TRUE)

# Functions
scatter <- function(data, x_var, y_var) {
  limits <- c(min(df$compilation.time), TIMEOUT)
  ggplot(data, aes(.data[[x_var]], .data[[y_var]])) +
    geom_count() +
    scale_size_area() +
    geom_abline(slope = 1, intercept = 0, colour = "#989898") +
    scale_x_continuous(trans = log10_trans(), breaks = breaks, labels = breaks,
                       limits = limits) +
    scale_y_continuous(trans = log10_trans(), breaks = breaks, labels = breaks,
                       limits = limits) +
    coord_fixed() +
    annotation_logticks(colour = "#b3b3b3") +
    theme_light(base_size = 9) +
    theme(legend.title=element_blank()) +
    scale_size_continuous(breaks = round)
} # TODO (later): have the same legend for all scatter plots

cumulative_plot <- function(df) {
  times <- vector(mode = "list", length = length(algorithms))
  names(times) <- algorithms
  for (algorithm in algorithms) {
    times[[algorithm]] <- unique(df$time[df$algorithm == algorithm])
  }

  chunks <- vector(mode = "list", length = length(algorithms))
  names(chunks) <- algorithms
  for (algorithm in algorithms) {
    chunks[[algorithm]] <- cbind(times[[algorithm]], algorithm,
                             unlist(times[[algorithm]] %>%
                                      map(function(x)
                                        sum(df$time[df$algorithm == algorithm]
                                            <= x))))
  }

  cumulative <- as.data.frame(do.call(rbind, as.list(chunks)))
  names(cumulative) <- c("time", "algorithm", "count")
  cumulative$algorithm <- as.factor(cumulative$algorithm)
  cumulative$time <- as.numeric(cumulative$time)
  cumulative$count <- as.numeric(cumulative$count)

  ggplot(cumulative, aes(x = time, y = count, color = .data$algorithm)) +
    geom_line(aes(linetype = algorithm)) +
    scale_x_continuous(trans = log10_trans(), breaks = breaks,
                       labels = breaks) +
    scale_y_continuous(breaks = pretty_breaks()) +
    xlab("Compilation time (s)") +
    ylab("Instances solved") +
    annotation_logticks(sides = "b", colour = "#b3b3b3") +
    labs(color = "Algorithm", linetype = "Algorithm") +
    scale_color_brewer(palette = "Dark2") +
    scale_linetype_manual(breaks = sort(algorithms),
                          values = 1:length(algorithms)) +
    theme_light(base_size = 9) +
    theme(legend.title=element_blank())
}

# Preprocessing
df2 <- df %>% expand(algorithm, sequence, domain.size)
df <- df %>% right_join(df2)
df$compilation.time <- df$compilation.time / 1000
df$inference.time <- df$inference.time / 1000
df$compilation.time[is.na(df$compilation.time)] <- TIMEOUT
df$inference.time[is.na(df$inference.time)] <- TIMEOUT
rm(df2)

# Sanity check: do the counts match (should return an empty tibble)?
df %>% group_by(sequence, domain.size) %>%
  filter(min(count, na.rm = TRUE) != max(count, na.rm = TRUE))

# Part 0: success rates per algorithm
# TODO: along with 'total', add 'uniquely' and 'fastest' columns
length(unique(df$sequence))
df[df$compilation.time < TIMEOUT,] %>% group_by(algorithm) %>%
  summarize(total = n_distinct(sequence))

# Part 1: compilation time per algorithm per instance (taking the median for
# ForcLift)
df2 <- df %>% group_by(algorithm, sequence) %>%
  summarize(time = median(compilation.time))
compilation.times <- df2 %>% pivot_wider(names_from = algorithm,
                                         values_from = time)
scatter(compilation.times, "Crane-BFS", "ForcLift")
scatter(compilation.times, "Crane-Greedy", "ForcLift")
scatter(compilation.times, "Crane-Greedy", "Crane-BFS")
cumulative_plot(df2)

# Part 2: inference time per algorithm per instance (taking the largest domain
# size that all algorithms could handle)
# TODO: unfinished, but the experimental data is not complete enough to
# properly test this (do both scatter and cumulative plots like above)
df[!is.na(df$count),] %>% group_by(sequence) %>%
  filter(domain.size == max(domain.size))

# TODO Part 3: for each algorithm and instance, find the degree of the
# polynomial that best matches the increase in inference time (use that
# external package for this) (both cumulative and scatter plots? or something
# else?)