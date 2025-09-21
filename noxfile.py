import nox


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    session.install("ruff", "black", "isort", "bandit")
    session.run("ruff", "check", "codehealthanalyzer")
    session.run("isort", "--profile", "black", "--check-only", "codehealthanalyzer")
    session.run("black", "--check", "codehealthanalyzer")
    session.run("bandit", "-q", "-r", "codehealthanalyzer")


@nox.session(reuse_venv=True)
def format(session: nox.Session) -> None:
    session.install("ruff", "black", "isort")
    session.run("isort", "--profile", "black", ".")
    session.run("black", ".")
    session.run(
        "ruff", "check", ".", "--fix", "--exit-non-zero-on-fix", "--unsafe-fixes"
    )


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.install("pytest", "pytest-cov")
    session.install("-e", ".[web,dev]")
    session.run("pytest", "-q")
