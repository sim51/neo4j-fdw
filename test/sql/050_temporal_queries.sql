\a
SET IntervalStyle to postgres_verbose;
/* Date comparisons */
SELECT * FROM temporal WHERE temporal.my_date > (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_date < (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_date = (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_date < (DATE '1983-03-27');
SELECT * FROM temporal WHERE temporal.my_date > (TIMESTAMP '1983-03-26 12:45:30');
SELECT * FROM temporal WHERE temporal.my_date < (TIMESTAMP '1983-03-26 12:45:30');
SELECT * FROM temporal WHERE temporal.my_date < (TIMESTAMP '1983-03-27 12:45:30');
SELECT * FROM temporal WHERE temporal.my_date > (TIMESTAMPTZ '1983-03-26 12:45:30+01');
SELECT * FROM temporal WHERE temporal.my_date < (TIMESTAMPTZ '1983-03-26 12:45:30+01');
SELECT * FROM temporal WHERE temporal.my_date < (TIMESTAMPTZ '1983-03-27 12:45:30+01');
SELECT * FROM temporal WHERE temporal.my_date < (TIMESTAMPTZ '1983-03-26 20:45:30-05');

/* Datetime without TZ comparisons */
SELECT * FROM temporal WHERE temporal.my_localdatetime > (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_localdatetime < (DATE '1983-03-27');
SELECT * FROM temporal WHERE temporal.my_localdatetime < now();
SELECT * FROM temporal WHERE temporal.my_localdatetime < (TIMESTAMP '1983-03-26 12:45:30');
SELECT * FROM temporal WHERE temporal.my_localdatetime < (TIMESTAMP '1983-03-26 12:45:31');
SELECT * FROM temporal WHERE temporal.my_localdatetime < (TIMESTAMPTZ '1983-03-26 12:45:30+01');
SELECT * FROM temporal WHERE temporal.my_localdatetime < (TIMESTAMPTZ '1983-03-26 12:45:31-01');

/* Datetime with TZ comparisons */
SELECT * FROM temporal WHERE temporal.my_datetime > (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_datetime < (DATE '1983-03-26');
SELECT * FROM temporal WHERE temporal.my_datetime < now();
SELECT * FROM temporal WHERE temporal.my_datetime < (TIMESTAMP '1983-03-26 12:45:30');
SELECT * FROM temporal WHERE temporal.my_datetime < (TIMESTAMPTZ '1983-03-26 12:45:30+01');

/* Time with TZ comparisons */
SELECT * FROM temporal WHERE temporal.my_localtime = (TIME '12:45:30.25');
SELECT * FROM temporal WHERE temporal.my_localtime < (TIME '12:45:30.25');
SELECT * FROM temporal WHERE temporal.my_localtime < (TIMETZ '12:45:30.25+01');
SELECT * FROM temporal WHERE temporal.my_localtime < (TIMETZ '12:45:30.25-01');

/* Time without TZ comparisons */
SELECT * FROM temporal WHERE temporal.my_time = (TIME '12:45:30.25');
SELECT * FROM temporal WHERE temporal.my_time < (TIME '12:46:30.25');
SELECT * FROM temporal WHERE temporal.my_time < (TIMETZ '12:45:30.25+01');
SELECT * FROM temporal WHERE temporal.my_time < (TIMETZ '13:46:30.25+01');
