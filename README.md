# Wikiscore
## Auto-Evaluation of (Simple) Wikipedia Articles

<p>
<em>Wikipedia</em><sup><a href="https://www.wikipedia.org/">[1]</a></sup> is a well known and widely used source of information. Wikipedia is massive<sup><a href="https://en.wikipedia.org/wiki/Wikipedia:Size_comparisons#:~:text=Currently%2C%20the%20English%20Wikipedia%20alone,million%20articles%20in%20309%20languages.">[2]</a></sup>,
and its information is largely crowdsourced. As a result it is impossible<sup><a>[citation needed]</a></sup> to manually evaluate the continuously growing number of articles. Even so, Wikipedia users should be able to check the
quality/credibility of the articles that they are using. Thus, we propose <strong>Wikiscore</strong>: an automated version of the evaluation process that will give users a quality score and a confidence score for each article they
want to use.
</p>
<br/>
<p>
In order to make the problem tractable for our timeframe, we won't be retrieving articles from Wikipedia itself. The main, English version of Wikipedia sports over 6 million articles<sup><a href="https://en.wikipedia.org/wiki/Wikipedia:Size_comparisons#:~:text=Currently%2C%20the%20English%20Wikipedia%20alone,million%20articles%20in%20309%20languages.">[2]</a></sup>.
To reduce computing time, we will instead use the Simple English Wikipedia, a condensed and simplified version of Wikipedia, that contains just over 200,000 articles<sup><a href="https://en.wikipedia.org/wiki/Simple_English_Wikipedia">[3]</a></sup>.
</p>

## Documentation

`comps_website`: Anything related to the actual comps website.

`modules`: The brunt of the code
- `modeling.R`: Backward elimination construction of a generalized linear regression model to predict the likelihood that an article is good.
- `wiki_analysis.py`: Data structures for holding data and metadata for articles and revisions as we process them from the dump
- `wiki_db.py`: Initializing the database and populating it with data from the dump.
- `wiki_dump.py`: Data structure and methods for iteratively parsing, processing and storing the XML Wikipedia data. 
- `wiki_quotescore.py`: Methods for obtaining a quote score for a piece of text.
- `wiki_req.py`: Methods for accessing the Wikipedia API for pulling data. 

`sql`: Any `psql` scripts used to populate database entries.
- `complete_author_sum.sql`: Produce a score per article counting the number of times authors that have worked on the article have worked on other articles together.
- `filtered_author_sum.sql`: Produce a score per article counting the number of times authors that have worked on the article have worked on other articles together *ignoring authors that have only worked together once*.
- `get_article_densities.sql`: Create a table that stores the number of times a given pair of authors have worked together.
- `get_author_scores.sql`: Produce a score per article that counts the scores of all the articles that this article's authors have worked on.

`stopwords`:
- english: A list of English stopwords (high-frequency, ignorable words).

`words`: 
- en: A list of English words.
- en-basic: A listo of basic English words.