library(tidyverse)
library(RPostgreSQL)
library(car)
library(jtools)

# Set up database connection
con <- dbConnect(drv=PostgreSQL(),
                 user="mathcsadmin",
                 password="corgiPower!",
                 host="127.0.0.1",
                 dbname="wikipedia")

# retrieve all articles and revisions
articles <- dbGetQuery(con, "SELECT * FROM public.article;")
revisions <- dbGetQuery(con, 'SELECT revision_id,title,num_internal_links,num_external_links,article_length,article_id,flesch,kincaid,num_images,average_sentence_length,date FROM public."revisionHistory";')

# zero out missing entries
revisions$num_images[revisions$num_images == -1] <- 0
revisions$average_sentence_length[revisions$average_sentence_length == -1] <- 0
revisions$num_internal_links[revisions$num_internal_links == -1] <- 0
revisions$num_external_links[revisions$num_external_links == -1] <- 0
revisions$age <- as.numeric(difftime(Sys.time(), revisions$date), units = "days")

# filter out any entries that have non-sensical flesch/kincaid scores
# as those entries are usually spam 
summarized_rev_filtered <- revisions %>%
  group_by(article_id) %>%
  mutate(scaled_nil =     num_internal_links * 1 / age,
         scaled_nel =     num_external_links * 1 / age,
         scaled_len =     article_length * 1 / age,
         scaled_flesch =  flesch * 1 / age,
         scaled_kincaid = kincaid * 1 / age,
         scaled_num_im =  num_images * 1 / age,
         scaled_asl =     average_sentence_length * 1 / age) %>%
  summarize(median_nil =     median(scaled_nil, na.rm=TRUE),
            median_nel =     median(scaled_nel, na.rm=TRUE),
            median_len =     median(scaled_len, na.rm=TRUE),
            median_flesch =  median(scaled_flesch, na.rm=TRUE),
            median_kincaid = median(scaled_kincaid, na.rm=TRUE),
            median_num_im =  median(scaled_num_im, na.rm=TRUE), 
            median_asl =     median(scaled_asl, na.rm=TRUE),
            min_nil =        min(scaled_nil, na.rm=TRUE),
            min_nel =        min(scaled_nel, na.rm=TRUE),
            min_len =        min(scaled_len, na.rm=TRUE),
            min_flesch =     min(scaled_flesch, na.rm=TRUE),
            min_kincaid =    min(scaled_kincaid, na.rm=TRUE),
            min_num_im =     min(scaled_num_im, na.rm=TRUE), 
            min_asl =        min(scaled_asl, na.rm=TRUE),
            max_nil =        max(scaled_nil, na.rm=TRUE),
            max_nel =        max(scaled_nel, na.rm=TRUE),
            max_len =        max(scaled_len, na.rm=TRUE),
            max_flesch =     max(scaled_flesch, na.rm=TRUE),
            max_kincaid =    max(scaled_kincaid, na.rm=TRUE),
            max_num_im =     max(scaled_num_im, na.rm=TRUE), 
            max_asl =        max(scaled_asl, na.rm=TRUE))

# combine revision properties with article-level data
total <- articles %>%
  left_join(summarized_rev_filtered, by = c("id" = "article_id")) %>%
  mutate(gvg = as.factor(ifelse(article_quality == 0, 0, 1)),
         article_quality = as.factor(article_quality)) %>%
  drop_na(min_len)

total_no_out <- total[-c(249313,175312, 228643), ] %>%
  mutate(
    lmedian_nil = log(median_nil + 1),
    lmedian_nel = log(median_nel + 1),
    lmedian_len = log(median_len + 1),
    lmedian_kincaid = log(median_kincaid + 1),
    lmedian_num_im = log(median_num_im + 1),
    lmedian_asl = log(median_asl + 1),
    lmin_nil = log(min_nil + 1),
    lmin_nel = log(min_nel + 1),
    lmin_len = log(min_len + 1),
    lmin_kincaid = log(min_kincaid + 1),
    lmin_num_im = log(min_num_im + 1),
    lmin_asl = log(min_asl + 1),
    lmax_nil = log(max_nil + 1),
    lmax_nel = log(max_nel + 1),
    lmax_len = log(max_len + 1),
    lmax_kincaid = log(max_kincaid + 1),
    lmax_num_im = log(max_num_im + 1),
    lmax_asl = log(max_asl + 1),
    lnum_edits = log(num_edits + 1),
    lnum_unique_authors = log(num_unique_authors + 1),
    lage = log(age + 1),
    lcurrency = log(currency + 1),
    lfull_author_density = log(full_author_density + 1),
    author_score,
    median_flesch,
    min_flesch,
    max_flesch,
    author_diversity,
    author_density,
    lquotescore = log(quotescore + 1),
    lnonquotescore = log(nonquotescore + 1)
  )

lform <- gvg ~ lmedian_nil +
               lmedian_nel +
               lmedian_len +
               lmedian_kincaid +
               lmedian_num_im +
               lmedian_asl +
               lmin_nil +
               lmin_nel +
               lmin_len +
               lmin_kincaid +
               lmin_num_im +
               lmin_asl +
               lmax_nil +
               lmax_nel +
               lmax_len +
               lmax_kincaid +
               lmax_num_im +
               lmax_asl +
               lnum_edits +
               lnum_unique_authors +
               lage +
               lcurrency +
               lfull_author_density +
               author_score +
               median_flesch +
               min_flesch +
               max_flesch +
               author_diversity +
               author_density +
               lquotescore +
               lnonquotescore

# generalized linear regression model
total.glm <- glm(lform, data = total_no_out, family = "binomial")
summary(total.glm)

total.glm.red1 <- update(total.glm, . ~ . - lmin_kincaid)
summary(total.glm.red1)

total.glm.red2 <- update(total.glm.red1, . ~ . - lmin_nel - lmin_nil - lmedian_nel)
summary(total.glm.red2)

total.glm.red3 <- update(total.glm.red2, . ~ . - lquotescore)
summary(total.glm.red3)

total.glm.red4 <- update(total.glm.red3, . ~ . - lnum_edits)
summary(total.glm.red4)

total.glm.red5 <- update(total.glm.red4, . ~ . - lmax_num_im)
summary(total.glm.red5)

total.glm.red6 <- update(total.glm.red5, . ~ . - lfull_author_density)
summary(total.glm.red6)

total.glm.red7 <- update(total.glm.red6, . ~ . - lnonquotescore)
summary(total.glm.red7)

total.glm.red8 <- update(total.glm.red7, . ~ . - lmin_len)
summary(total.glm.red8)

total.glm.red9 <- update(total.glm.red8, . ~ . - lmin_asl)
summary(total.glm.red9)

total.glm.red10 <- update(total.glm.red9, . ~ . - lmin_num_im - lmedian_num_im)
summary(total.glm.red10)

total.glm.red11 <- update(total.glm.red10, . ~ . - lmedian_len) 
summary(total.glm.red11)

pdf("resids1.pdf")
par(mfrow = c(2, 2))
plot(total.glm.red11)
dev.off()

total_no_out <- total_no_out %>% 
  mutate(model_score = log(fitted.values(total.glm.red11)))

model_scores <- total_no_out %>% pull(model_score) %>% as.numeric()
ids <- total_no_out %>% pull(id) %>% as.integer()

for (i in 1:nrow(total_no_out)) {
  statement = paste0("UPDATE public.article SET model_score = ", format(model_scores[i], digits = 10), " WHERE id = ", ids[i])
  dbExecute(con, statement)
}

library(caret)
pdf("varimp.pdf")
rownames_to_column(as.data.frame(varImp(total.glm.red11)), "metric") %>%
  mutate(metric =
  c("(Log) Median No. of Internal Links",
    "(Log) Median Kincaid",
    "(Log) Median Average\n Sentence Length",
    "(Log) Min No. of\n Internal Links",
    "(Log) Max No. of\n External Links",
    "(Log) Max Length",
    "(Log) Max Kincaid",
    "(Log) Max Average\n Sentence Length",
    "(Log) No. Unique Authors",
    "(Log) Age",
    "(Log) Currency",
    "Author Score",
    "Median Flesch",
    "Min Flesch",
    "Max Flesch",
    "Author Diversity",
    "Author Density")) %>%
  slice_max(Overall, n=5) %>%
  ggplot() +
  geom_col(aes(x = Overall, y = reorder(metric, Overall)), fill="darkgoldenrod1", width = 0.6) + 
  xlab("Importance") +
  ylab("") +
  theme(axis.ticks.y = element_blank(),
        panel.background = element_rect(fill = "white"),
        panel.grid.major.y = element_blank(),
        panel.grid.minor.y = element_blank(),
        panel.grid.major.x = element_line(color = "lightgray"),
        panel.grid.minor.x = element_blank(),
        axis.line.x = element_line(color = "darkgray")) +
  theme(axis.text.y = element_text()) +
  scale_x_continuous(breaks = seq(0, 11, 2))
dev.off()
