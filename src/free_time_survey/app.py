from os import getenv

import flask
from dotenv import load_dotenv

from connection import PostgresDBConnectionManager

load_dotenv()
app = flask.Flask(__name__)


@app.get("/")
def form():
    with PostgresDBConnectionManager(getenv("DATABASE_URL")) as cursor:
        cursor.execute("select id, name from activities order by id")
        activities = cursor.fetchall()
        cursor.execute("select id, name from companions order by id")
        companions = cursor.fetchall()
    return flask.render_template(
        "index.html.jinja", activities=activities, companions=companions
    )


@app.post("/submit")
def submit():
    age = flask.request.form["age"]
    grade = flask.request.form["grade"]
    free_day = flask.request.form["free_day"]
    activity_id = flask.request.form["activity_id"]
    companion_id = flask.request.form["companion_id"]
    hours_per_day = flask.request.form["hours_per_day"]
    satisfaction = flask.request.form["satisfaction"]
    with PostgresDBConnectionManager(getenv("DATABASE_URL")) as cursor:
        cursor.execute(
            """
                insert into 
                    responses (age, grade, free_day, activity_id, companion_id, hours_per_day, satisfaction)
                values
                    (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                age,
                grade,
                free_day,
                activity_id,
                companion_id,
                hours_per_day,
                satisfaction,
            ),
        )
    return flask.redirect("/completed")


@app.get("/completed")
def completed():
    return flask.render_template("completed.html.jinja")


if __name__ == "__main__":
    app.run()
