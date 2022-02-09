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

log_form <- gvg ~ log(num_edits) + log(num_unique_authors) + author_diversity + log(age) + log(currency) + log(median_nil + 1) + log(median_nel + 1) + log(median_len + 1) + median_flesch + median_kincaid + log(median_num_im + 1) + log(median_asl + 1) + log(author_density + 1) + log(author_score + 1)

total.glm <- glm(log_form, data = total, family = "binomial")
total.glm.red1 <- update(total.glm, . ~ . - median_flesch)
total.glm.red2 <- update(total.glm.red1, . ~ . - log(currency))
total.glm.red3 <- update(total.glm.red2, . ~ . - log(num_edits))
total.glm.red4 <- update(total.glm.red3, . ~ . - log(num_unique_authors))