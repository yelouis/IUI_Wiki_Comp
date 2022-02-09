ALTER TABLE article ADD full_author_density bigint;

CREATE TABLE complete_author_sum AS
SELECT A.article_id AS article_id, SUM(F.count) AS count
FROM public."revisionHistory" A, public."revisionHistory" B, public."connectivity_graph" F
WHERE A.article_id = B.article_id AND 
      A.real_id != B.real_id AND 
      F.autha = A.real_id AND 
      F.authb = B.real_id
GROUP BY A.article_id;

UPDATE article SET full_author_density = 0;

UPDATE article SET full_author_density = count 
FROM public."complete_author_sum" A
WHERE id = A.article_id;