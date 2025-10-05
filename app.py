import os
import json
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, session, flash
from flask_dance.contrib.github import make_github_blueprint, github
from github import Github as PyGithub

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "dev-secret"

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

github_bp = make_github_blueprint(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    scope="repo"
)
app.register_blueprint(github_bp, url_prefix="/login")

# ------------------- Helper Functions -------------------

def gather_user_data(pygh_user, username):
    data = {"username": username, "repos": {}, "summary": {}, "mentorship": {}}
    total_repos = 0
    total_reviews_seen = 0
    total_approvals_by_user = 0
    total_changes_by_user = 0
    total_prs_raised = 0

    repos = pygh_user.get_repos()  # Get all user repos

    for repo in repos:
        try:
            repo_name = repo.full_name
        except Exception:
            continue  # skip if repo name not accessible

        approvals = 0
        changes = 0
        comments = 0
        reviews_by_user = 0
        pr_raised = 0

        # ------------------- Pull Requests -------------------
        try:
            pulls = list(repo.get_pulls(state="all"))
        except Exception:
            pulls = []

        for pr in pulls:
            try:
                reviews = list(pr.get_reviews())
            except Exception:
                reviews = []

            pr_raised += 1  # increment PR count

            for review in reviews:
                state_lower = (review.state or "").lower()
                if state_lower == "approved":
                    approvals += 1
                elif state_lower in ("changes_requested", "request_changes"):
                    changes += 1
                else:
                    comments += 1

        total_prs_raised += pr_raised

        # ------------------- Reviews by the user -------------------
        for pr in pulls:
            try:
                reviews = list(pr.get_reviews())
            except Exception:
                reviews = []

            for review in reviews:
                reviewer = getattr(review.user, "login", None)
                state_lower = (review.state or "").lower()

                if reviewer == username:
                    reviews_by_user += 1
                    total_reviews_seen += 1
                    if state_lower == "approved":
                        total_approvals_by_user += 1
                    elif state_lower in ("changes_requested", "request_changes"):
                        total_changes_by_user += 1

                    pr_author = getattr(pr.user, "login", None)
                    if pr_author and pr_author != username:
                        data["mentorship"].setdefault(pr_author, 0)
                        data["mentorship"][pr_author] += 1

        # ------------------- Most Important Issue -------------------
        try:
            issues = list(repo.get_issues(state="open", sort="comments", direction="desc"))
            if issues:
                top_issue = issues[0]
                most_important_issue = {
                    "title": top_issue.title,
                    "url": top_issue.html_url,
                    "comments": top_issue.comments
                }
            else:
                most_important_issue = None
        except Exception:
            most_important_issue = None

        # ------------------- Safe Data Retrieval -------------------
        # Count total issues safely
        try:
            total_issues = len(list(repo.get_issues(state="all")))
        except Exception:
            total_issues = 0

        # Count docs commits safely (skip empty repos)
        try:
            docs_updates = len(list(repo.get_commits(path="docs")))
        except Exception:
            docs_updates = 0  # empty repos cause 409 error, so we skip

        # Mentorship sessions (for this user)
        mentorship_sessions = data["mentorship"].get(username, 0)

        # ------------------- Save Repo Data -------------------
        data["repos"][repo_name] = {
            "repo_name": repo_name,
            "approvals": approvals,
            "changes": changes,
            "comments": comments,
            "pr_raised": pr_raised,
            "reviews_by_user": reviews_by_user,
            "issues_count": total_issues,
            "docs_updates": docs_updates,
            "mentorship_sessions": mentorship_sessions,
            "most_important_issue": most_important_issue
        }

        total_repos += 1

    # ------------------- Summary -------------------
    data["summary"] = {
        "total_repos_count": total_repos,
        "pr_raised": total_prs_raised,
        "total_reviews_seen": total_reviews_seen,
        "total_approvals_by_user": total_approvals_by_user,
        "total_changes_by_user": total_changes_by_user,
        "mentored_users_count": len(data["mentorship"])
    }

    return data


    # ------------------- Summary -------------------
    data["summary"] = {
        "total_repos_count": total_repos,
        "pr_raised": total_prs_raised,
        "total_approvals_by_user": total_approvals_by_user,
        "total_changes_by_user": total_changes_by_user,
        "mentored_users_count": len(data["mentorship"])
    }

    return data

# ------------------- Routes -------------------

@app.route("/")
def index():
    if github.authorized:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not github.authorized:
        return redirect(url_for("github.login"))

    resp = github.get("/user")
    if not resp.ok:
        flash("Failed to fetch user info from GitHub", "error")
        return redirect(url_for("index"))

    user_json = resp.json()
    username = user_json.get("login")

    token = github.token["access_token"]
    pygh = PyGithub(token)

    try:
        pygh_user = pygh.get_user(username)
    except Exception as e:
        flash("Failed to initialize PyGithub user: " + str(e), "error")
        return redirect(url_for("index"))

    payload = gather_user_data(pygh_user, username)
    session["profile_payload"] = payload

    return render_template("dashboard.html", data=payload, base_url=BASE_URL)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ------------------- Run App -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
