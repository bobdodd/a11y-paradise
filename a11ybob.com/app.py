from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# MongoDB connection
client = MongoClient(app.config["MONGO_URI"])
db = client[app.config["MONGO_DB"]]


# --- Context processor for nav highlighting ---

@app.context_processor
def nav_context():
    return {"current_path": request.path}


# --- Static pages ---

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


# --- Glossary ---

@app.route("/glossary")
def glossary_index():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    if q:
        # Atlas Search full-text query
        pipeline = [
            {
                "$search": {
                    "index": "glossary_search",
                    "text": {
                        "query": q,
                        "path": ["term", "aka", "definition", "category"],
                        "fuzzy": {"maxEdits": 1},
                    },
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
        ]
        if category:
            pipeline.append({"$match": {"category": category}})
        terms = list(db.glossary.aggregate(pipeline))
    elif category:
        terms = list(db.glossary.find({"category": category}).sort("term", 1))
    else:
        terms = list(db.glossary.find().sort("term", 1))

    categories = sorted(db.glossary.distinct("category"))
    return render_template(
        "glossary/index.html",
        terms=terms,
        query=q,
        selected_category=category,
        categories=categories,
    )


@app.route("/glossary/<term_id>")
def glossary_term(term_id):
    term = db.glossary.find_one({"_id": ObjectId(term_id)})
    if not term:
        return render_template("404.html"), 404

    # Fetch related terms
    related = []
    if term.get("related_terms"):
        related = list(
            db.glossary.find({"term": {"$in": term["related_terms"]}}).sort("term", 1)
        )

    return render_template("glossary/term.html", term=term, related=related)


# --- Literature Reviews ---

@app.route("/reviews")
def reviews_index():
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

    if q:
        pipeline = [
            {
                "$search": {
                    "index": "reviews_search",
                    "text": {
                        "query": q,
                        "path": [
                            "title",
                            "authors",
                            "summary",
                            "key_findings",
                            "tags",
                            "standards_referenced",
                        ],
                        "fuzzy": {"maxEdits": 1},
                    },
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
        ]
        if tag:
            pipeline.append({"$match": {"tags": tag}})
        reviews = list(db.reviews.aggregate(pipeline))
    elif tag:
        reviews = list(db.reviews.find({"tags": tag}).sort("year", -1))
    else:
        reviews = list(db.reviews.find().sort("year", -1))

    tags = sorted(db.reviews.distinct("tags"))
    return render_template(
        "reviews/index.html",
        reviews=reviews,
        query=q,
        selected_tag=tag,
        tags=tags,
    )


@app.route("/reviews/<review_id>")
def review_detail(review_id):
    review = db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        return render_template("404.html"), 404
    return render_template("reviews/review.html", review=review)


# --- Error handlers ---

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
