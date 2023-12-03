CREATE TABLE subjects(id SERIAL PRIMARY KEY,
					 name VARCHAR NOT NULL UNIQUE);

CREATE TABLE teachers(id SERIAL PRIMARY KEY, 
					 full_name VARCHAR NOT NULL UNIQUE,
					 subject1 INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
					 subject2 INT REFERENCES subjects(id) ON DELETE CASCADE);
							
CREATE TABLE timetable(id SERIAL PRIMARY KEY,
					 day VARCHAR NOT NULL,
					 week_is_even BOOLEAN NOT NULL,
					 subject INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
					 room_numb VARCHAR NOT NULL,
					 start_time VARCHAR NOT NULL);
