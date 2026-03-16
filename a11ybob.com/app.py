import math
from flask import Flask, render_template, request, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import Config
from admin import admin_bp

GLOSSARY_PER_PAGE = 20
REVIEWS_PER_PAGE = 10

app = Flask(__name__)
app.config.from_object(Config)

# MongoDB connection
client = MongoClient(
    app.config["MONGO_URI"],
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=10000,
)
db = client[app.config["MONGO_DB"]]
app.config["db"] = db

# Register admin blueprint
app.register_blueprint(admin_bp)


# --- Context processor for nav highlighting ---

@app.context_processor
def nav_context():
    def url_for_page(page_num):
        args = request.args.copy()
        args["page"] = page_num
        return request.path + "?" + "&".join(
            f"{k}={v}" for k, v in args.items(multi=True)
        )

    return {
        "current_path": request.path,
        "is_admin": session.get("admin", False),
        "url_for_page": url_for_page,
    }


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
    page = max(1, request.args.get("page", 1, type=int))

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
        all_terms = list(db.glossary.aggregate(pipeline))
        total = len(all_terms)
        total_pages = math.ceil(total / GLOSSARY_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * GLOSSARY_PER_PAGE
        terms = all_terms[skip : skip + GLOSSARY_PER_PAGE]
    elif category:
        total = db.glossary.count_documents({"category": category})
        total_pages = math.ceil(total / GLOSSARY_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * GLOSSARY_PER_PAGE
        terms = list(
            db.glossary.find({"category": category})
            .sort("term", 1)
            .skip(skip)
            .limit(GLOSSARY_PER_PAGE)
        )
    else:
        total = db.glossary.count_documents({})
        total_pages = math.ceil(total / GLOSSARY_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * GLOSSARY_PER_PAGE
        terms = list(
            db.glossary.find()
            .sort("term", 1)
            .skip(skip)
            .limit(GLOSSARY_PER_PAGE)
        )

    categories = sorted(db.glossary.distinct("category"))
    return render_template(
        "glossary/index.html",
        terms=terms,
        total=total,
        query=q,
        selected_category=category,
        categories=categories,
        page=page,
        total_pages=total_pages,
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
    sort = request.args.get("sort", "newest").strip()
    page = max(1, request.args.get("page", 1, type=int))

    sort_options = {
        "newest": ("_id", -1),
        "year_desc": ("year", -1),
        "year_asc": ("year", 1),
        "title": ("title", 1),
        "author": ("authors", 1),
    }
    sort_field, sort_dir = sort_options.get(sort, ("_id", -1))

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
        if sort != "newest":
            pipeline.append({"$sort": {sort_field: sort_dir}})
        all_reviews = list(db.reviews.aggregate(pipeline))
        total = len(all_reviews)
        total_pages = math.ceil(total / REVIEWS_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * REVIEWS_PER_PAGE
        reviews = all_reviews[skip : skip + REVIEWS_PER_PAGE]
    elif tag:
        total = db.reviews.count_documents({"tags": tag})
        total_pages = math.ceil(total / REVIEWS_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * REVIEWS_PER_PAGE
        reviews = list(
            db.reviews.find({"tags": tag})
            .sort(sort_field, sort_dir)
            .skip(skip)
            .limit(REVIEWS_PER_PAGE)
        )
    else:
        total = db.reviews.count_documents({})
        total_pages = math.ceil(total / REVIEWS_PER_PAGE) or 1
        page = min(page, total_pages)
        skip = (page - 1) * REVIEWS_PER_PAGE
        reviews = list(
            db.reviews.find()
            .sort(sort_field, sort_dir)
            .skip(skip)
            .limit(REVIEWS_PER_PAGE)
        )

    tags = sorted(db.reviews.distinct("tags"))
    return render_template(
        "reviews/index.html",
        reviews=reviews,
        total=total,
        query=q,
        selected_tag=tag,
        selected_sort=sort,
        tags=tags,
        page=page,
        total_pages=total_pages,
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
