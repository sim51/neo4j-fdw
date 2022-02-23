\a
SELECT * FROM movie ORDER BY id ASC LIMIT 10;
SELECT * FROM movie m WHERE m.released > 2000 ORDER BY m.released DESC, m.id DESC LIMIT 10;
SELECT * FROM movie m WHERE m.title = 'The Matrix' ORDER BY m.id ASC;
SELECT * FROM movie m WHERE m.title LIKE '%Matrix%' ORDER BY m.id ASC;
SELECT * FROM movie m WHERE m.title ILIKE '%matrix%' ORDER BY m.id ASC;
SELECT count(*) FROM movie m;
SELECT count(*) FROM movie m WHERE m.released > 2000;
SELECT avg(released) FROM movie m WHERE m.title like '%Matrix%';
SELECT title, released, tagline FROM movie m WHERE m.title IN ('The Matrix', 'Top Gun') AND m.released > 1980 ORDER BY m.id ASC;
SELECT title, released, tagline FROM movie m WHERE NOT m.title IN ('The Matrix', 'Top Gun') AND m.released > 1980 ORDER BY m.id ASC;
