-- Query 5: Identify parent competitions and their sub-competitions
-- Requirements Ref: REQ-COMP-11 (PDF Page 4)
SELECT 
    p.competition_id AS parent_id,
    p.competition_name AS parent_name,
    s.competition_id AS sub_competition_id,
    s.competition_name AS sub_competition_name,
    s.type AS sub_type,
    s.gender AS sub_gender,
    cat.category_name
FROM competitions s
JOIN competitions p ON s.parent_id = p.competition_id
JOIN categories cat ON s.category_id = cat.category_id
ORDER BY p.competition_name, s.competition_name;
