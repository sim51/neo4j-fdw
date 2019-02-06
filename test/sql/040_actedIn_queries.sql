\a
SELECT * FROM actedIn ORDER BY id DESC LIMIT 10;
SELECT * FROM actedIn WHERE movie_id = 0;
SELECT * FROM actedInWithCustomWhere1 WHERE movie = 'The Matrix' AND actor = 'Keanu Reeves';
SELECT * FROM actedInWithCustomWhere2 WHERE movie = 'The Matrix' AND actor = 'Keanu Reeves';
SELECT * FROM actedInWithCustomWheres WHERE movie = 'The Matrix' AND actor = 'Keanu Reeves';