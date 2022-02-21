ALTER TABLE article ADD author_density BIGINT;

CREATE TABLE filtered_graph AS
SELECT * FROM connectivity_graph F
WHERE F.count > 1 AND
      F.autha NOT LIKE '%Bot' AND
      F.autha NOT LIKE '%bot' AND
      F.authb NOT LIKE '%Bot' AND
      F.authb NOT LIKE '%bot';

CREATE TABLE author_sum AS
SELECT A.article_id AS article_id, SUM(F.count) AS count
FROM public."filtered_graph" F, public."revisionHistory" A, public."revisionHistory" B
WHERE F.autha = A.real_id AND 
      F.authb = B.real_id AND
      A.article_id = B.article_id AND 
      A.real_id != B.real_id 
GROUP BY A.article_id;

UPDATE article SET author_density = 0;

UPDATE article SET author_density = count 
FROM public."author_sum" A
WHERE id = A.article_id;