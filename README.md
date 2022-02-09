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

`modules`: The brunt of the code
- `wiki_analysis.py`:
- `wiki_db.py`:
- `wiki_dump.py`:
- `wiki_quotescore.py`:
- `wiki_req.py`:

`stopwords`:
- english: A list of English stopwords (high-frequency, ignorable words).

`words`: 
- en: A list of English words.
- en-basic: A listo of basic English words.