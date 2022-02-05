CREATE TABLE author_sum AS
SELECT A.article_id AS article_id, SUM(F.count) AS count
FROM public."revisionHistory" A, public."revisionHistory" B, public."filtered_graph" F
WHERE A.article_id = B.article_id AND 
      A.real_id != B.real_id AND 
      F.autha = A.real_id AND 
      F.authb = B.real_id
GROUP BY A.article_id;

UPDATE article SET author_density = count 
FROM public."author_sum" A
WHERE id = A.article_id;