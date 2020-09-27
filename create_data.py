import json

from app import Teacher, db, Goal, Day
from data import teachers, days, goals


for key, value in days.items():
    day = Day(day_key_en = key, day_value_ru = value)
    db.session.add(day)
db.session.commit()

for key, value in goals.items():
    goal = Goal(goal_key_en = key, goal_value_ru = value)
    db.session.add(goal)
db.session.commit()

for teacher in teachers:
    teacher_record = Teacher(id = teacher['id'], name = teacher['name'], about = teacher['about'], rating = teacher['rating'], picture = teacher['picture'], price = teacher['price'], free = json.dumps(teacher['free']))
    for goal in teacher['goals']:
        goal_record = db.session.query(Goal).filter(Goal.goal_key_en == goal).first()
        teacher_record.goals.append(goal_record)
        db.session.add(teacher_record)


db.session.commit()



