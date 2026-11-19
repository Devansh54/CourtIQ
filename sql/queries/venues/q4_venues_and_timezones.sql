
-- Q4: Display all venues with their respective timezones.

SELECT
    venue_id,
    venue_name,
    city_name,
    country_name,
    timezone
FROM venues
ORDER BY
    timezone,
    country_name,
    city_name;
