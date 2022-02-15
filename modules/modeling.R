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
  summarize(scaled_nil = median(num_internal_links * 1 / log(age), na.rm=TRUE),
            scaled_nel = median(num_external_links * 1 / log(age), na.rm=TRUE),
            scaled_len = median(article_length * 1 / log(age), na.rm=TRUE),
            scaled_flesch = median(flesch * 1 / log(age), na.rm=TRUE),
            scaled_kincaid = median(kincaid * 1 / log(age), na.rm=TRUE),
            scaled_num_im = median(num_images * 1 / log(age), na.rm=TRUE), 
            scaled_asl = median(average_sentence_length * 1 / log(age), na.rm=TRUE))

# combine revision properties with article-level data
total <- articles %>% 
  left_join(summarized_rev_filtered, by = c("id" = "article_id")) %>%
  mutate(gvg = as.factor(ifelse(article_quality == 0, 0, 1)),
         article_quality = as.factor(article_quality)) %>%
  drop_na(scaled_kincaid)

log_form <- gvg ~ log(num_edits) +  
                  log(num_unique_authors) + 
                  author_diversity + 
                  log(age) + 
                  log(currency) + 
                  log(scaled_nil + 1) + 
                  log(scaled_nel + 1) + 
                  log(scaled_len + 1) + 
                  scaled_flesch + 
                  scaled_kincaid + 
                  log(scaled_num_im + 1) + 
                  log(scaled_asl + 1) + 
                  log(author_density + 1) + 
                  log(author_score + 1) +
                  quotescore +
                  nonquotescore

pdf("test1.pdf")
total %>% ggplot() +
  geom_density(aes(x = nonquotescore, fill = article_quality), alpha = 0.5)
dev.off()


# generalized linear regression model
total.glm <- glm(log_form, data = total, family = "binomial")
total.glm.red1 <- update(total.glm, . ~ . - log(currency))
total.glm.red2 <- update(total.glm.red1, . ~ . - log(scaled_nil + 1))
total.glm.red3 <- update(total.glm.red2, . ~ . - log(num_edits))
total.glm.red4 <- update(total.glm.red3, . ~ . - log(scaled_num_im + 1))
total.glm.red5 <- update(total.glm.red4, . ~ . - log(num_unique_authors))
total.glm.red6 <- update(total.glm.red5, . ~ . - quotescore)

total <- total %>% 
  mutate(score = log(fitted.values(total.glm.red6)))

scores <- total %>% pull(score) %>% as.numeric()
ids <- total %>% pull(id) %>% as.integer()

for (i in 1:nrow(total)) {
  statement = paste0("UPDATE public.article SET model_score = ", format(scores[i], digits = 10), " WHERE id = ", ids[i])
  dbExecute(con, statement)
}


