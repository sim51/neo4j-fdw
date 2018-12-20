\a
SELECT * FROM movie LIMIT 10;
SELECT * FROM movie m WHERE m.released > 2000 ORDER BY m.released DESC LIMIT 10;
SELECT * FROM movie m WHERE m.title = 'The Matrix';
SELECT * FROM movie m WHERE m.title LIKE '%Matrix%';
SELECT * FROM movie m WHERE m.title ILIKE '%matrix%';
SELECT count(*) FROM movie m WHERE m.released > 2000;
SELECT avg(released) FROM movie m WHERE m.title like '%Matrix%';
SELECT title, released, tagline FROM movie m WHERE m.title IN ('The Matrix', 'Top Gun') AND m.released > 1980;
