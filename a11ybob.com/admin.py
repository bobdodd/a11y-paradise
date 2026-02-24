import secrets
from functools import wraps
from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)
from bson.objectid import ObjectId

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            flash("Please log in to access the admin area.", "error")
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)

    return decorated


def get_db():
    return current_app.config["db"]


def parse_lines(text):
    """Split textarea value into a list, one item per line."""
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# --- Auth ---


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        admin_pw = current_app.config["ADMIN_PASSWORD"]
        if admin_pw and secrets.compare_digest(password, admin_pw):
            session["admin"] = True
            next_url = request.args.get("next", url_for("admin.dashboard"))
            flash("Logged in successfully.", "success")
            return redirect(next_url)
        else:
            flash("Incorrect password.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))


# --- Dashboard ---


@admin_bp.route("/")
@admin_required
def dashboard():
    db = get_db()
    return render_template(
        "admin/dashboard.html",
        glossary_count=db.glossary.count_documents({}),
        review_count=db.reviews.count_documents({}),
    )


# --- Glossary CRUD ---


@admin_bp.route("/glossary")
@admin_required
def glossary_list():
    db = get_db()
    terms = list(db.glossary.find().sort("term", 1))
    return render_template("admin/glossary_list.html", terms=terms)


@admin_bp.route("/glossary/add", methods=["GET", "POST"])
@admin_required
def glossary_add():
    db = get_db()
    if request.method == "POST":
        term, errors = _validate_glossary(request.form)
        if errors:
            return render_template(
                "admin/glossary_form.html",
                errors=errors,
                form=request.form,
                editing=False,
            )
        term["created"] = today()
        term["updated"] = today()
        db.glossary.insert_one(term)
        flash(f"Glossary term \u2018{term['term']}\u2019 added.", "success")
        return redirect(url_for("admin.glossary_list"))
    return render_template(
        "admin/glossary_form.html", errors=[], form={}, editing=False
    )


@admin_bp.route("/glossary/edit/<term_id>", methods=["GET", "POST"])
@admin_required
def glossary_edit(term_id):
    db = get_db()
    existing = db.glossary.find_one({"_id": ObjectId(term_id)})
    if not existing:
        flash("Term not found.", "error")
        return redirect(url_for("admin.glossary_list"))

    if request.method == "POST":
        doc, errors = _validate_glossary(request.form)
        if errors:
            return render_template(
                "admin/glossary_form.html",
                errors=errors,
                form=request.form,
                editing=True,
                term=existing,
            )
        doc["updated"] = today()
        db.glossary.update_one({"_id": ObjectId(term_id)}, {"$set": doc})
        flash(f"Glossary term \u2018{doc['term']}\u2019 updated.", "success")
        return redirect(url_for("admin.glossary_list"))

    return render_template(
        "admin/glossary_form.html", errors=[], form={}, editing=True, term=existing
    )


@admin_bp.route("/glossary/delete/<term_id>", methods=["GET", "POST"])
@admin_required
def glossary_delete(term_id):
    db = get_db()
    term = db.glossary.find_one({"_id": ObjectId(term_id)})
    if not term:
        flash("Term not found.", "error")
        return redirect(url_for("admin.glossary_list"))

    if request.method == "POST":
        db.glossary.delete_one({"_id": ObjectId(term_id)})
        flash(f"Glossary term \u2018{term['term']}\u2019 deleted.", "success")
        return redirect(url_for("admin.glossary_list"))

    return render_template(
        "admin/confirm_delete.html",
        item_type="glossary term",
        item_name=term["term"],
        delete_url=url_for("admin.glossary_delete", term_id=term_id),
        cancel_url=url_for("admin.glossary_list"),
    )


def _validate_glossary(form):
    errors = []
    term = form.get("term", "").strip()
    if not term:
        errors.append("Term is required.")
    definition = form.get("definition", "").strip()
    if not definition:
        errors.append("Definition is required.")

    doc = {
        "term": term,
        "definition": definition,
        "aka": parse_lines(form.get("aka", "")),
        "category": parse_lines(form.get("category", "")),
        "related_terms": parse_lines(form.get("related_terms", "")),
        "sources": parse_lines(form.get("sources", "")),
    }
    return doc, errors


# --- Reviews CRUD ---


@admin_bp.route("/reviews")
@admin_required
def reviews_list():
    db = get_db()
    reviews = list(db.reviews.find().sort("year", -1))
    return render_template("admin/reviews_list.html", reviews=reviews)


@admin_bp.route("/reviews/add", methods=["GET", "POST"])
@admin_required
def reviews_add():
    db = get_db()
    if request.method == "POST":
        doc, errors = _validate_review(request.form)
        if errors:
            return render_template(
                "admin/reviews_form.html",
                errors=errors,
                form=request.form,
                editing=False,
            )
        doc["created"] = today()
        doc["updated"] = today()
        db.reviews.insert_one(doc)
        flash(f"Review \u2018{doc['title']}\u2019 added.", "success")
        return redirect(url_for("admin.reviews_list"))
    return render_template(
        "admin/reviews_form.html", errors=[], form={}, editing=False
    )


@admin_bp.route("/reviews/edit/<review_id>", methods=["GET", "POST"])
@admin_required
def reviews_edit(review_id):
    db = get_db()
    existing = db.reviews.find_one({"_id": ObjectId(review_id)})
    if not existing:
        flash("Review not found.", "error")
        return redirect(url_for("admin.reviews_list"))

    if request.method == "POST":
        doc, errors = _validate_review(request.form)
        if errors:
            return render_template(
                "admin/reviews_form.html",
                errors=errors,
                form=request.form,
                editing=True,
                review=existing,
            )
        doc["updated"] = today()
        db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": doc})
        flash(f"Review \u2018{doc['title']}\u2019 updated.", "success")
        return redirect(url_for("admin.reviews_list"))

    return render_template(
        "admin/reviews_form.html", errors=[], form={}, editing=True, review=existing
    )


@admin_bp.route("/reviews/delete/<review_id>", methods=["GET", "POST"])
@admin_required
def reviews_delete(review_id):
    db = get_db()
    review = db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        flash("Review not found.", "error")
        return redirect(url_for("admin.reviews_list"))

    if request.method == "POST":
        db.reviews.delete_one({"_id": ObjectId(review_id)})
        flash(f"Review \u2018{review['title']}\u2019 deleted.", "success")
        return redirect(url_for("admin.reviews_list"))

    return render_template(
        "admin/confirm_delete.html",
        item_type="review",
        item_name=review["title"],
        delete_url=url_for("admin.reviews_delete", review_id=review_id),
        cancel_url=url_for("admin.reviews_list"),
    )


def _validate_review(form):
    errors = []
    title = form.get("title", "").strip()
    if not title:
        errors.append("Title is required.")
    authors = parse_lines(form.get("authors", ""))
    if not authors:
        errors.append("At least one author is required.")

    year_str = form.get("year", "").strip()
    year = None
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            errors.append("Year must be a number.")

    rating_str = form.get("rating", "").strip()
    rating = None
    if rating_str:
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                errors.append("Rating must be between 1 and 5.")
        except ValueError:
            errors.append("Rating must be a number.")

    doc = {
        "title": title,
        "authors": authors,
        "year": year,
        "publication": form.get("publication", "").strip(),
        "doi": form.get("doi", "").strip(),
        "tags": parse_lines(form.get("tags", "")),
        "standards_referenced": parse_lines(form.get("standards_referenced", "")),
        "summary": form.get("summary", "").strip(),
        "key_findings": form.get("key_findings", "").strip(),
        "relevance": form.get("relevance", "").strip(),
        "rating": rating,
    }
    return doc, errors
