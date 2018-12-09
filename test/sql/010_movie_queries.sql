SELECT * FROM movie LIMIT 10;
SELECT * FROM movie m WHERE m.released > 2000 ORDER BY m.released DESC LIMIT 10;
SELECT * FROM movie m WHERE m.title = 'The Matrix';
SELECT * FROM movie m WHERE m.title LIKE '%Matrix%';
SELECT * FROM movie m WHERE m.title ILIKE '%matrix%';
