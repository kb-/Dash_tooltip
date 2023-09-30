import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def tests_selenium(session):
    # Install dependencies:
    session.install("-r", "requirements.txt")

    # Install your package in editable mode:
    session.install("-e", ".")

    # Run pytest with Firefox WebDriver for Selenium tests:
    session.run("pytest", "tests/", "-k", "selenium", "--webdriver", "Firefox")


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def tests_non_selenium(session):
    # Install dependencies:
    session.install("-r", "requirements.txt")

    # Install your package in editable mode:
    session.install("-e", ".")

    # Run pytest for non-Selenium tests:
    session.run("pytest", "tests/", "-k", "not selenium")
