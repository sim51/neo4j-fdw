\a
SELECT * FROM person LIMIT 10;
SELECT * FROM person p WHERE p.born > 1980 ORDER BY p.born DESC LIMIT 10;
SELECT * FROM person p WHERE p.name = 'Keanu Reeves';
SELECT * FROM person p WHERE p.name LIKE '%Keanu%';
SELECT * FROM person p WHERE p.name ILIKE '%keanu%';
