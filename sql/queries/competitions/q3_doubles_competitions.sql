-- Query 3: Find all competitions of type 'doubles'
-- Requirements Ref: REQ-COMP-09 (PDF Page 4)
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
WHERE LOWER(c.type) = 'doubles'
ORDER BY cat.category_name, c.competition_name;
