library(tidyverse)
library(RPostgreSQL)

con <- dbConnect(drv=PostgreSQL(),
                 user="mathcsadmin",
                 password="corgiPower!",
                 host="127.0.0.1",
                 dbname="wikipedia")

articles <- dbGetQuery(con, "SELECT * FROM public.article;")
revisions <- dbGetQuery(con, 'SELECT id,title,num_internal_links,num_external_links,article_length,article_id,flesch,kincaid,num_images,average_sentence_length,date FROM public."revisionHistory";')

vg_articles <- c("1910 Cuba hurricane","American Airlines Flight 11","Baseball uniform","City of Manchester Stadium","Mourning dove","Evolution","Hermann Göring","Gothic architecture","Billy Graham","Hurricane Vince","Ipswich Town F.C.","Jupiter","Dan Kelly","Kingsway tramway subway","Lawrence, Kansas","The Lightning Thief","Commodore Nutt","Portman Road","Powderfinger","Ronald Reagan","Red Hot Chili Peppers","Bobby Robson","Saturn","Le Spectre de la rose","Tropical Depression Ten (2005)","Tropical Storm Barry (2007)","Tropical Storm Gabrielle (2007)")
g_articles <- c("Grand Duchess Anastasia Nikolaevna of Russia", "Fra Angelico", "Bald eagle", "Jean Balukas", "Ludwig van Beethoven", "Bird", "Black hole", "Bloc Party", "Wernher von Braun", "Bridge to Terabithia (2007 movie)", "Oyster Burns", "Carom billiards", "Cassowary", "Chess", "Chopsticks", "Color blindness", "Color of the day (police)", "Common scold", "Jeremy Corbyn", "Crater Lake", "Crich Tramway Village", "Bobby Dodd", "Bobby Fischer", "Geisha", "Gettysburg Address", "Giant panda", "Valéry Giscard d'Estaing", "Goodfellow's tree-kangaroo", "Hurricane Grace (1991)", "Green Day", "Ben Hall", "Hanami", "Hebrew calendar", "History of Kansas", "Hot chocolate", "Hurricane Floyd (1987)", "India", "Tropical Storm Ingrid (2007)", "Hurricane Ismael", "Japanese American internment", "Ned Kelly", "Knut (polar bear)", "Komodo dragon", "Lawrence massacre", "Least weasel", "London Underground 1967 Stock", "London Underground 2009 Stock", "Mimicry", "Monarch butterfly", "Mosque", "Movie Stars", "Neptune", "New York State Route 308", "The Nutcracker", "Alexandria Ocasio-Cortez", "Oxalaia", "Presidents' Trophy", "Fred Rogers", "Ernst Röhm", "Royal Rumble (2009)", "St. Peter's Basilica", "Bernie Sanders", "The Sea of Monsters", "Selena (album)", "Sentō", "Shabbat", "Shipping Forecast", "Singapore", "Skite (album)", "John McDouall Stuart", "Typhoon Tip", "The Titan's Curse", "Tropical Storm Arthur (2020)", "Trouble (Coldplay song)", "Victoria line", "Wheeling Tunnel", "Yellow (song)", "Zinc")

revisions$num_images[revisions$num_images == -1] <- 0
revisions$average_sentence_length[revisions$average_sentence_length == -1] <- 0
revisions$num_internal_links[revisions$num_internal_links == -1] <- 0
revisions$num_external_links[revisions$num_external_links == -1] <- 0

summarized_rev <- revisions %>%
  group_by(article_id) %>%
  summarize(mean_nil = mean(num_internal_links, na.rm=TRUE), 
            mean_nel = mean(num_external_links, na.rm=TRUE),
            mean_len = mean(article_length, na.rm=TRUE),
            mean_flesch = mean(flesch, na.rm=TRUE),
            mean_kincaid = mean(kincaid, na.rm=TRUE),
            mean_num_im = mean(num_images, na.rm=TRUE), 
            mean_asl = mean(average_sentence_length, na.rm=TRUE))

total <- articles %>% 
  left_join(summarized_rev, by = c("id" = "article_id")) %>% 
  mutate(good = ifelse(title %in% g_articles, 1, 0), 
         vgood = ifelse(title %in% vg_articles, 1, 0),
         gvg = good == 1 | vgood == 1)

total.glm.nolog <- glm(gvg ~ num_edits + num_unique_authors + author_diversity + age + currency + mean_nil + mean_nel + mean_len + mean_flesch + mean_kincaid + mean_num_im + mean_asl, data = total, family = "binomial")

total.glm <- glm(gvg ~ log(num_edits) + log(num_unique_authors) + author_diversity + log(age) + log(currency) + log(mean_nil + 1) + log(mean_nel + 1) + log(mean_len + 1) + mean_flesch + mean_kincaid + log(mean_num_im + 1) + log(mean_asl + 1), data = total, family = "binomial")

pdf("1_influence_plot.pdf")
influencePlot(total.glm)
dev.off()

pdf("1_resid.pdf")
plot(total.glm, which = 1)
dev.off()

total.glm.red1 <- update(total.glm, . ~ . - log(num_unique_authors))
anova(total.glm, total.glm.red1, test="Chisq")
summary(total.glm.red1)

total.glm.red2 <- update(total.glm.red1, . ~ . - log(currency))
anova(total.glm.red2, total.glm.red1, test="Chisq")
summary(total.glm.red2)

total.glm.red3 <- update(total.glm.red2, . ~ . - mean_kincaid)
anova(total.glm.red2, total.glm.red3, test="Chisq")
summary(total.glm.red3)

total.glm.red4 <- update(total.glm.red3, . ~ . - log(mean_nil + 1))
anova(total.glm.red4, total.glm.red3, test="Chisq")
summary(total.glm.red4)

total.glm.red5 <- update(total.glm.red4, . ~ . - log(mean_asl + 1))
anova(total.glm.red4, total.glm.red5, test="Chisq")
summary(total.glm.red5)

total.glm.red6 <- update(total.glm.red5, . ~ . - log(num_edits))
anova(total.glm.red6, total.glm.red5, test="Chisq")
summary(total.glm.red6)

total.glm.red7 <- update(total.glm.red6, . ~ . - log(mean_num_im + 1))
anova(total.glm.red6, total.glm.red7, test="Chisq")
summary(total.glm.red7)

pdf("7_influence_plot.pdf")
influencePlot(total.glm.red7)
dev.off()

pdf("7_resid.pdf")
plot(total.glm.red7, which = 1)
dev.off()

# EDA

cor(total)

pdf("hist_num_edits.pdf")
hist(total$num_edits)
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

pdf("hist_mean_nil.pdf")
hist(total$mean_nil)
dev.off()

pdf("hist_mean_nel.pdf")
hist(total$mean_nel)
dev.off()

pdf("hist_mean_len.pdf")
hist(total$mean_len)
dev.off()

pdf("hist_mean_flesch.pdf")
hist(total$mean_flesch)
dev.off()

pdf("hist_mean_kincaid.pdf")
hist(total$mean_kincaid)
dev.off()

pdf("hist_mean_num_im.pdf")
hist(total$mean_num_im)
dev.off()

pdf("hist_mean_asl.pdf")
hist(total$mean_asl)
dev.off()