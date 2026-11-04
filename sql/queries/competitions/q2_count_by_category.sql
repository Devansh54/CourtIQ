-- Query 2: Count the number of competitions in each category
-- Requirements Ref: REQ-COMP-08 (PDF Page 3)
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(c.competition_id) AS competition_count
FROM categories cat
LEFT JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY competition_count DESC, cat.category_name ASC;
