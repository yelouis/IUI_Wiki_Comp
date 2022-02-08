library(tidyverse)
library(RPostgreSQL)
library(car)
library(jtools)

con <- dbConnect(drv=PostgreSQL(),
                 user="mathcsadmin",
                 password="corgiPower!",
                 host="127.0.0.1",
                 dbname="wikipedia")

articles <- dbGetQuery(con, "SELECT * FROM public.article;")
revisions <- dbGetQuery(con, 'SELECT revision_id,title,num_internal_links,num_external_links,article_length,article_id,flesch,kincaid,num_images,average_sentence_length,date FROM public."revisionHistory";')

revisions$num_images[revisions$num_images == -1] <- 0
revisions$average_sentence_length[revisions$average_sentence_length == -1] <- 0
revisions$num_internal_links[revisions$num_internal_links == -1] <- 0
revisions$num_external_links[revisions$num_external_links == -1] <- 0

summarized_rev <- revisions %>%
  group_by(article_id) %>%
  summarize(median_nil = median(num_internal_links, na.rm=TRUE),
            median_nel = median(num_external_links, na.rm=TRUE),
            median_len = median(article_length, na.rm=TRUE),
            median_flesch = median(flesch, na.rm=TRUE),
            median_kincaid = median(kincaid, na.rm=TRUE),
            median_num_im = median(num_images, na.rm=TRUE), 
            median_asl = median(average_sentence_length, na.rm=TRUE))

summarized_rev_filtered <- revisions %>%
  group_by(article_id) %>%
  filter(flesch > 0, flesch < 100, kincaid > -3.4, kincaid < 20) %>%
  summarize(median_nil = median(num_internal_links, na.rm=TRUE),
            median_nel = median(num_external_links, na.rm=TRUE),
            median_len = median(article_length, na.rm=TRUE),
            median_flesch = median(flesch, na.rm=TRUE),
            median_kincaid = median(kincaid, na.rm=TRUE),
            median_num_im = median(num_images, na.rm=TRUE), 
            median_asl = median(average_sentence_length, na.rm=TRUE))

total <- articles %>% 
  left_join(summarized_rev_filtered, by = c("id" = "article_id")) %>%
  mutate(gvg = as.factor(ifelse(article_quality == 0, 0, 1)),
         article_quality = as.factor(article_quality)) %>%
  drop_na()

nolog_form <- gvg ~ num_edits + num_unique_authors + author_diversity + age + currency + median_nil + median_nel + median_len + median_flesch + median_kincaid + median_num_im + median_asl + author_density + author_score

log_form <- gvg ~ log(num_edits) + log(num_unique_authors) + author_diversity + log(age) + log(currency) + log(median_nil + 1) + log(median_nel + 1) + log(median_len + 1) + median_flesch + median_kincaid + log(median_num_im + 1) + log(median_asl + 1) + log(author_density + 1) + log(author_score + 1)

total.glm.nolog <- glm(nolog_form, data = total, family = "binomial")

total.glm <- glm(log_form, data = total, family = "binomial")

summary(total.glm)
summary(total.glm.nolog)

total.glm.red1 <- update(total.glm, . ~ . - median_flesch)
anova(total.glm, total.glm.red1, test="Chisq")
summary(total.glm.red1)

total.glm.red2 <- update(total.glm.red1, . ~ . - log(currency))
anova(total.glm.red2, total.glm.red1, test="Chisq")
summary(total.glm.red2)

total.glm.red3 <- update(total.glm.red2, . ~ . - log(num_edits))
anova(total.glm.red3, total.glm.red2, test="Chisq")
summary(total.glm.red3)

total.glm.red4 <- update(total.glm.red3, . ~ . - log(num_unique_authors))
anova(total.glm.red4, total.glm.red3, test="Chisq")
summary(total.glm.red4)

pdf("influence_plot.pdf")
influencePlot(total.glm.red4)
dev.off()

pdf("resid.pdf")
plot(total.glm.red4, which = 1)
dev.off()

pdf("coefs.pdf")
plot_coefs(total.glm.red4)
dev.off()

summary_data <- total %>% 
  mutate(log_num_edits = log(num_edits),
         log_age = log(age),
         log_median_nil = log(median_nil + 1),
         log_median_nel = log(median_nel + 1),
         log_median_len = log(median_len + 1),
         log_median_num_im = log(median_num_im + 1)) %>%
  select(log_num_edits, author_diversity, log_age, log_median_nil,
         log_median_nel, log_median_len, median_flesch, log_median_num_im)

summary_df <- as.data.frame(summary_data)

library(psych)

describe(summary_df, fast=TRUE)

# prediction

total$prediction <- predict(total.glm.red4, newdata = total, type = "response")

hist(total$prediction)

hist(log(total$prediction) - min(log(total$prediction), na.rm=TRUE))

# EDA

cor(total)

pdf("hist_num_edits.pdf")
hist(total$num_edits)
hist(log(total$num_edits))
dev.off()

pdf("hist_num_unique_authors.pdf")
hist(total$num_unique_authors)
dev.off()

pdf("hist_author_diversity.pdf")
hist(total$author_diversity)
dev.off()

pdf("hist_age.pdf")
hist(total$age)
dev.off()

pdf("hist_currency.pdf")
hist(total$currency)
dev.off()

pdf("hist_median_nil.pdf")
hist(total$median_nil)
dev.off()

pdf("hist_median_nel.pdf")
hist(total$median_nel)
dev.off()

pdf("hist_median_len.pdf")
hist(total$median_len)
dev.off()

pdf("hist_median_flesch.pdf")
hist(total$median_flesch)
dev.off()

pdf("hist_median_kincaid.pdf")
hist(total$median_kincaid)
dev.off()

pdf("hist_median_num_im.pdf")
hist(total$median_num_im)
dev.off()

pdf("hist_median_asl.pdf")
hist(total$median_asl)
dev.off()