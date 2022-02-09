CREATE TABLE connectivity_graph AS SELECT A.real_id as authA, B.real_id as authB, COUNT(*)
FROM public."revisionHistory" A, public."revisionHistory" B
WHERE A.article_id = B.article_id AND A.real_id != B.real_id
GROUP BY autha, authb
ORDER BY autha;