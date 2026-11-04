-- Query 1: List all competitions along with their category name
-- Requirements Ref: REQ-COMP-07 (PDF Page 3)
SELECT 
    c.competition_id,
    c.competition_name,
    c.parent_id,
    c.type,
    c.gender,
    c.category_id,
    cat.category_name
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
ORDER BY cat.category_name, c.competition_name;
