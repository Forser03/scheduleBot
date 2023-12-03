SELECT timetable.day, timetable.week_is_even, subjects.name, timetable.room_numb, timetable.start_time, teachers.full_name
FROM timetable, subjects, teachers
WHERE timetable.subject=subjects.id AND (timetable.subject=teachers.subject1 OR timetable.subject=teachers.subject2);