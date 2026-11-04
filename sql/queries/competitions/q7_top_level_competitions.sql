-- Query 7: List all competitions with no parent (top-level competitions)
-- Requirements Ref: REQ-COMP-13 (PDF Page 4)
SELECT 
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    c.category_id,
    cat.category_name
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
WHERE c.parent_id IS NULL OR TRIM(c.parent_id) = ''
ORDER BY cat.category_name ASC, c.competition_name ASC;
