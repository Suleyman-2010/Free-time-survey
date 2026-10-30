from .app import app


def main():
    app.run("localhost", 5000, True)
