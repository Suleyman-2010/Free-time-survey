from os import getenv
from re import findall

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
from psycopg2.sql import SQL, Identifier

from connection import PostgresDBConnectionManager as ConnectionManager

load_dotenv()
app: Flask = Flask(__name__)


@app.get("/")
def form():
    cstr_columns = ["age", "grade", "hours_per_day", "satisfaction"]
    with ConnectionManager(getenv("DATABASE_URL")) as cursor:
        option_tables = ["activities", "companions"]
        options = {table: [] for table in option_tables}
        for table in option_tables:
            cursor.execute(
                SQL("select id, name from {} order by id").format(Identifier(table))
            )
            options[table] = cursor.fetchall()

        with open("./get_constraint.sql") as file:
            get_cstr: str = file.read()

            cstr_strings: list[str] = []
            for column in cstr_columns:
                cursor.execute(get_cstr, (column,))
                cstr_strings.append(cursor.fetchone()[0])

    cstrs_list: list[tuple[list, list]] = []
    for string in cstr_strings:
        regex: list[str] = findall(r"([<>]=?|\d+(?:\.\d+)?)", string)
        cstrs_list.append((regex[0:2], regex[2:4]))

    cstrs_dict: dict[str, dict[str, int]] = {column: {} for column in cstr_columns}
    for index, pair in enumerate(cstrs_list):
        for operator, value in pair:
            match operator:
                case "<":
                    cstrs_dict[cstr_columns[index]]["max"] = int(value) - 1
                case "<=":
                    cstrs_dict[cstr_columns[index]]["max"] = int(value)
                case ">":
                    cstrs_dict[cstr_columns[index]]["min"] = int(value) - 1
                case ">=":
                    cstrs_dict[cstr_columns[index]]["min"] = int(value)

    return render_template(
        "index.html.jinja",
        activities=options["activities"],
        companions=options["companions"],
        age_cstrs=cstrs_dict["age"],
        grade_cstrs=cstrs_dict["grade"],
        hpd_cstrs=cstrs_dict["hours_per_day"],
        sat_cstrs=cstrs_dict["satisfaction"],
    )


@app.post("/submit")
def submit():
    columns = [
        "age",
        "grade",
        "free_day",
        "activity_id",
        "companion_id",
        "hours_per_day",
        "satisfaction",
    ]
    data = [request.form[column] for column in columns]

    with ConnectionManager(getenv("DATABASE_URL")) as cursor:
        with open("send_data.sql") as file:
            query = file.read()
        cursor.execute(query, data)
    return redirect("/completed")


@app.get("/completed")
def completed():
    return render_template("completed.html.jinja")
