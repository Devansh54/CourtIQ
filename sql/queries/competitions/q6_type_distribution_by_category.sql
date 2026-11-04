-- Query 6: Analyze the distribution of competition types by category
-- Requirements Ref: REQ-COMP-12 (PDF Page 4)
SELECT 
    cat.category_name,
    c.type,
    COUNT(c.competition_id) AS competition_count
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name ASC, competition_count DESC;
