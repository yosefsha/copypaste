from flask import Flask, Response, current_app, jsonify, make_response, redirect, render_template, url_for
from flask_wtf import CSRFProtect
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from copypaste import db
from copypaste.config import Config
from copypaste.forms import CreatePasteForm


def _highlight(paste: db.Paste) -> str | None:
    if not paste.language or paste.language == "text":
        return None
    try:
        lexer = get_lexer_by_name(paste.language)
    except ClassNotFound:
        return None
    return highlight(paste.content, lexer, HtmlFormatter(nowrap=False))


def create_app(table=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if table is None:
        resource = db.get_resource()
        table = db.create_table(resource)
    app.config["PASTE_TABLE"] = table

    CSRFProtect(app)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/")
    def create_form():
        return render_template("create.html", form=CreatePasteForm())

    @app.post("/")
    def create_paste():
        form = CreatePasteForm()
        if not form.validate_on_submit():
            return render_template("create.html", form=form), 400

        expires_in_seconds = int(form.expiration.data) if form.expiration.data else None
        try:
            paste_id = db.put_paste(
                current_app.config["PASTE_TABLE"],
                form.content.data,
                title=form.title.data,
                expires_in_seconds=expires_in_seconds,
                language=form.language.data,
            )
        except db.PasteTooLargeError:
            max_kb = db.MAX_PASTE_SIZE_BYTES // 1024
            form.content.errors.append(f"Paste is too large (max {max_kb}KB).")
            return render_template("create.html", form=form), 400

        return redirect(url_for("view_paste", paste_id=paste_id))

    @app.get("/raw/<paste_id>")
    def raw_paste(paste_id):
        paste = db.get_paste(current_app.config["PASTE_TABLE"], paste_id)
        if paste is None:
            return render_template("404.html"), 404

        response = Response(paste.content, mimetype="text/plain")
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    @app.get("/<paste_id>")
    def view_paste(paste_id):
        paste = db.get_paste(current_app.config["PASTE_TABLE"], paste_id)
        if paste is None:
            return render_template("404.html"), 404

        highlighted = _highlight(paste)
        response = make_response(
            render_template("view.html", paste=paste, paste_id=paste_id, highlighted=highlighted)
        )
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    return app
