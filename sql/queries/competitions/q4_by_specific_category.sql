-- Query 4: Get competitions that belong to a specific category (e.g., 'ITF Men')
-- Requirements Ref: REQ-COMP-10 (PDF Page 4)
-- Parameter :category_target binds to either category_name or category_id
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
WHERE LOWER(cat.category_name) = LOWER(?) OR cat.category_id = ?
ORDER BY c.competition_name;
