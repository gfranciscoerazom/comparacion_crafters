from typing import Annotated
from fastapi import FastAPI, Form, status
from sqlalchemy import desc, func
import uvicorn
from db.db_connection import db_dependency
from db.schema import Career, Faculty, Skill, User, UserCareer, UserSkill

app = FastAPI()


@app.post(
    "/",
    status_code=status.HTTP_200_OK,
    description="Compare two careers."
)
def compare_careers(
    db: db_dependency,
    career_id_1: Annotated[int, Form(...)],
    career_id_2: Annotated[int, Form(...)]
):
    career_1 = db.query(Career).filter(Career.id == career_id_1).first()
    career_2 = db.query(Career).filter(Career.id == career_id_2).first()

    faculty_1 = db.query(Faculty).filter(
        Faculty.id == career_1.faculty_id).first()
    faculty_2 = db.query(Faculty).filter(
        Faculty.id == career_2.faculty_id).first()

    pursuing_students_1 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_1, UserCareer.status == "cursando").count()
    pursuing_students_2 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_2, UserCareer.status == "cursando").count()

    graduated_students_1 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_1, UserCareer.status == "graduado").count()
    graduated_students_2 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_2, UserCareer.status == "graduado").count()

    expelled_students_1 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_1, UserCareer.status == "expulsado").count()
    expelled_students_2 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_2, UserCareer.status == "expulsado").count()

    resigned_students_1 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_1, UserCareer.status == "dimitido").count()
    resigned_students_2 = db.query(UserCareer).filter(
        UserCareer.career_id == career_id_2, UserCareer.status == "dimitido").count()

    comparison = {
        "name": (career_1.name, "", career_2.name),
        "Facultad": (faculty_1.name, "", faculty_2.name),
        "Descripción": (career_1.description, "", career_2.description),
        "Semestre": (career_1.semesters, career_1.semesters - career_2.semesters, career_2.semesters),
        "Créditos": (career_1.credits, career_1.credits - career_2.credits, career_2.credits),
        "Estudiantes cursando": (pursuing_students_1, pursuing_students_1 - pursuing_students_2, pursuing_students_2),
        "Estudiantes graduados": (graduated_students_1, graduated_students_1 - graduated_students_2, graduated_students_2),
        "Estudiantes expulsados": (expelled_students_1, expelled_students_1 - expelled_students_2, expelled_students_2),
        "Estudiantes dimitidos": (resigned_students_1, resigned_students_1 - resigned_students_2, resigned_students_2)
    }

    return comparison


def get_element(list, index):
    try:
        return list[index]
    except IndexError:
        return 0


def balance_skills(skills_of_students):
    balanced_skills_of_students = []
    for i in range(10):
        skill = get_element(skills_of_students, i)

        if skill == 0:
            break

        skill = list(skill)

        if i < 5:
            skill[2] *= 5 - i
        balanced_skills_of_students.append(skill)
    return balanced_skills_of_students


@app.post(
    "/compare-skills",
    status_code=status.HTTP_200_OK,
    description="Compare two skills.",
)
def compare_skills(
    db: db_dependency,
    user_id: Annotated[str, Form(...)],
    career_id: Annotated[int, Form(...)],
):
    user_skills = db.query(Skill).join(UserSkill).filter(
        UserSkill.user_id == user_id).all()

    all_careers = db.query(Career).all()

    skills_of_pursuing_students = db.query(
        Skill.id,
        Skill.name,
        func.count(Skill.id).label("count")
    ).join(UserSkill).join(User).join(UserCareer).filter(
        UserCareer.career_id == career_id, UserCareer.status == "cursando").group_by(Skill.id).order_by(desc("count")).all()

    skills_of_graduated_students = db.query(
        Skill.id,
        Skill.name,
        func.count(Skill.id).label("count")
    ).join(UserSkill).join(User).join(UserCareer).filter(
        UserCareer.career_id == career_id, UserCareer.status == "graduado").group_by(Skill.id).order_by(desc("count")).all()

    skills_of_expelled_students = db.query(
        Skill.id,
        Skill.name,
        func.count(Skill.id).label("count")
    ).join(UserSkill).join(User).join(UserCareer).filter(
        UserCareer.career_id == career_id, UserCareer.status == "expulsado").group_by(Skill.id).order_by(desc("count")).all()

    skills_of_resigned_students = db.query(
        Skill.id,
        Skill.name,
        func.count(Skill.id).label("count")
    ).join(UserSkill).join(User).join(UserCareer).filter(
        UserCareer.career_id == career_id, UserCareer.status == "dimitido").group_by(Skill.id).order_by(desc("count")).all()

    # Balance de importancia de las habilidades
    balanced_skills_of_pursuing_students = balance_skills(
        skills_of_pursuing_students)

    balanced_skills_of_graduated_students = balance_skills(
        skills_of_graduated_students)

    balanced_skills_of_expelled_students = balance_skills(
        skills_of_expelled_students)

    balanced_skills_of_resigned_students = balance_skills(
        skills_of_resigned_students)

    sum_of_pursuing_students = sum(
        [skill[2] for skill in balanced_skills_of_pursuing_students])

    sum_of_graduated_students = sum(
        [skill[2] for skill in balanced_skills_of_graduated_students])

    sum_of_expelled_students = sum(
        [skill[2] for skill in balanced_skills_of_expelled_students])

    sum_of_resigned_students = sum(
        [skill[2] for skill in balanced_skills_of_resigned_students])

    user_id_skills = [skill.id for skill in user_skills]

    pursuing_user_skills = [
        skill for skill in balanced_skills_of_pursuing_students if skill[0] in user_id_skills]

    graduated_user_skills = [
        skill for skill in balanced_skills_of_graduated_students if skill[0] in user_id_skills]

    expelled_user_skills = [
        skill for skill in balanced_skills_of_expelled_students if skill[0] in user_id_skills]

    resigned_user_skills = [
        skill for skill in balanced_skills_of_resigned_students if skill[0] in user_id_skills]

    sum_of_pursuing_user_skills = sum(
        [skill[2] for skill in pursuing_user_skills])

    sum_of_graduated_user_skills = sum(
        [skill[2] for skill in graduated_user_skills])

    sum_of_expelled_user_skills = sum(
        [skill[2] for skill in expelled_user_skills])

    sum_of_resigned_user_skills = sum(
        [skill[2] for skill in resigned_user_skills])

    try:
        percentage_of_pursuing_user_skills = round(
            (sum_of_pursuing_user_skills / sum_of_pursuing_students) * 100, 2)
    except ZeroDivisionError:
        percentage_of_pursuing_user_skills = 0

    try:
        percentage_of_graduated_user_skills = round(
            (sum_of_graduated_user_skills / sum_of_graduated_students) * 100, 2)
    except ZeroDivisionError:
        percentage_of_graduated_user_skills = 0

    try:
        percentage_of_expelled_user_skills = round(
            (sum_of_expelled_user_skills / sum_of_expelled_students) * 100, 2)
    except ZeroDivisionError:
        percentage_of_expelled_user_skills = 0

    try:
        percentage_of_resigned_user_skills = round(
            (sum_of_resigned_user_skills / sum_of_resigned_students) * 100, 2)
    except ZeroDivisionError:
        percentage_of_resigned_user_skills = 0

    return {
        "user_skills": user_skills,
        "careers": all_careers,
        # "skills_of_pursuing_students": skills_of_pursuing_students,
        # "skills_of_graduated_students": skills_of_graduated_students,
        # "skills_of_expelled_students": skills_of_expelled_students,
        # "skills_of_resigned_students": skills_of_resigned_students,
        "percentage_of_pursuing_user_skills": percentage_of_pursuing_user_skills,
        "percentage_of_graduated_user_skills": percentage_of_graduated_user_skills,
        "percentage_of_expelled_user_skills": percentage_of_expelled_user_skills,
        "percentage_of_resigned_user_skills": percentage_of_resigned_user_skills,
    }


# Entry point for the API
if __name__ == "__main__":
    # Run the application using uvicorn and enable auto-reload
    uvicorn.run("main:app", reload=True)
