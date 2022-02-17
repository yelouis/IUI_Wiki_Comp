CREATE TABLE complete_article_quality AS
SELECT A.title,  
    CASE WHEN Q.score is NULL THEN 0 ELSE Q.score END AS score 
FROM public."article" A LEFT OUTER JOIN public."article_quality" Q  
ON A.title = Q.name;

CREATE TABLE author_scores AS
SELECT rev.real_id, SUM(A.article_quality), COUNT(*)
FROM public."revisionHistory" rev, public."article" A
WHERE rev.article_id = A.id
GROUP BY rev.real_id;

CREATE TABLE article_author_scores AS 
SELECT rev.article_id, (SUM(Q.sum) - rev.article_quality) / SUM(Q.count) as score
FROM public."revisionHistory" rev, author_scores Q
WHERE rev.real_id = Q.real_id
GROUP BY rev.article_id, rev.article_quality;

ALTER TABLE article ADD author_score = REAL;

UPDATE article SET author_score = score
FROM public."article_author_scores" S
WHERE id = s.article_id;

UPDATE article SET article_quality = score
FROM public."article_quality" Q
WHERE title = Q.name;