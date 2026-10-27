
import os
from flask import Flask, request, redirect, url_for, render_template_string
from supabase import create_client

app = Flask(__name__)

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
db = create_client(url, key)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>College Library Management</title>
    <style>
        body { font-family: Arial; margin: 35px; background: #f2f5f9; }
        h1, h2 { color: #183153; }
        .box { background: white; padding: 20px; margin-bottom: 20px; }
        input, button { padding: 9px; margin: 5px; }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        button { cursor: pointer; }
    </style>
</head>
<body>
<h1>College Library Management System</h1>

<div class="box">
<h2>Add a Book</h2>
<form method="post" action="/add">
    <input name="title" placeholder="Book title" required>
    <input name="author" placeholder="Author" required>
    <input name="isbn" placeholder="ISBN">
    <label><input type="checkbox" name="available" checked> Available</label>
    <button type="submit">Add Book</button>
</form>
</div>

<div class="box">
<h2>Book Records</h2>
<table>
<tr><th>ID</th><th>Title</th><th>Author</th><th>ISBN</th>
<th>Availability</th><th>Actions</th></tr>
{% for b in books %}
<tr>
<td>{{ b.id }}</td><td>{{ b.title }}</td><td>{{ b.author }}</td>
<td>{{ b.isbn or '-' }}</td>
<td>{{ 'Available' if b.available else 'Issued' }}</td>
<td>
<a href="/edit/{{ b.id }}">Edit</a>
<form method="post" action="/delete/{{ b.id }}" style="display:inline"
      onsubmit="return confirm('Delete this book?')">
<button type="submit">Delete</button>
</form>
</td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    result = db.table("books").select("*").order("id").execute()
    return render_template_string(HTML, books=result.data)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    isbn = request.form.get("isbn", "").strip()

    if not title or not author:
        return "Title and author are required.", 400

    db.table("books").insert({
        "title": title,
        "author": author,
        "isbn": isbn or None,
        "available": "available" in request.form
    }).execute()
    return redirect(url_for("home"))

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit(book_id):
    result = db.table("books").select("*").eq("id", book_id).execute()
    if not result.data:
        return "Book not found", 404

    book = result.data[0]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()

        if not title or not author:
            return "Title and author are required.", 400

        db.table("books").update({
            "title": title,
            "author": author,
            "isbn": isbn or None,
            "available": "available" in request.form
        }).eq("id", book_id).execute()

        return redirect(url_for("home"))

    return render_template_string("""
    <h1>Update Book</h1>
    <form method="post">
        <input name="title" value="{{ book.title }}" required>
        <input name="author" value="{{ book.author }}" required>
        <input name="isbn" value="{{ book.isbn or '' }}">
        <label><input type="checkbox" name="available"
        {% if book.available %}checked{% endif %}> Available</label>
        <button type="submit">Save Changes</button>
    </form>
    """, book=book)

@app.route("/delete/<int:book_id>", methods=["POST"])
def delete(book_id):
    db.table("books").delete().eq("id", book_id).execute()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
