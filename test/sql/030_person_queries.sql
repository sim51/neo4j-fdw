\a
SELECT * FROM person ORDER BY id LIMIT 10;
SELECT * FROM person p WHERE p.born > 1980 ORDER BY p.born DESC LIMIT 10;
SELECT * FROM person p WHERE p.name = 'Keanu Reeves' ORDER BY p.id ASC;
SELECT * FROM person p WHERE p.name LIKE '%Keanu%' ORDER BY p.id ASC;
SELECT * FROM person p WHERE p.name ILIKE '%keanu%' ORDER BY p.id ASC;
