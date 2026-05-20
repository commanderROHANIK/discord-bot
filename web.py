from flask import Flask, render_template_string, request, redirect
import json
import feedparser

app = Flask(__name__)
KEYWORDS_FILE = "keywords.json"
FEEDS_FILE = "feeds.json"

def load_keywords():
    with open(KEYWORDS_FILE) as f:
        return json.load(f)

def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)

def save_feeds(feeds):
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds, f)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bot Manager</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
        h2 { margin-top: 40px; }
        input[type=text] { padding: 8px; font-size: 1em; width: 60%; }
        button[type=submit] { padding: 8px 16px; font-size: 1em; }
        ul { list-style: none; padding: 0; }
        li { display: flex; justify-content: space-between; align-items: center;
             padding: 8px; border-bottom: 1px solid #eee; }
        .delete { color: red; background: none; border: none; cursor: pointer; font-size: 1.2em; }
        .error { color: red; font-size: 0.9em; margin-top: 8px; }
        .url { font-size: 0.8em; color: #888; margin-left: 8px; }
    </style>
</head>
<body>
    <h1>🤖 Bot Manager</h1>

    <h2>📰 Keywords</h2>
    <form method="POST" action="/add_keyword">
        <input name="keyword" placeholder="Add keyword..." required>
        <button type="submit">Add</button>
    </form>
    <ul>
        {% for kw in keywords %}
        <li>
            {{ kw }}
            <form method="POST" action="/delete_keyword" style="margin:0">
                <input type="hidden" name="keyword" value="{{ kw }}">
                <button class="delete" type="submit">✕</button>
            </form>
        </li>
        {% endfor %}
    </ul>

    <h2>🌐 News Sites</h2>
    <form method="POST" action="/add_feed">
        <input name="name" placeholder="Name (e.g. Index)" required style="width:25%">
        <input name="url" placeholder="RSS URL" required style="width:55%">
        <button type="submit">Add</button>
    </form>
    {% if feed_error %}
    <p class="error">{{ feed_error }}</p>
    {% endif %}
    <ul>
        {% for name, url in feeds.items() %}
        <li>
            <span>{{ name }}<span class="url">{{ url }}</span></span>
            <form method="POST" action="/delete_feed" style="margin:0">
                <input type="hidden" name="name" value="{{ name }}">
                <button class="delete" type="submit">✕</button>
            </form>
        </li>
        {% endfor %}
    </ul>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML,
        keywords=load_keywords(),
        feeds=load_feeds(),
        feed_error=request.args.get("error")
    )

@app.route("/add_keyword", methods=["POST"])
def add_keyword():
    kw = request.form["keyword"].strip()
    keywords = load_keywords()
    if kw and kw not in keywords:
        keywords.append(kw)
        save_keywords(keywords)
    return redirect("/")

@app.route("/delete_keyword", methods=["POST"])
def delete_keyword():
    kw = request.form["keyword"]
    keywords = [k for k in load_keywords() if k != kw]
    save_keywords(keywords)
    return redirect("/")

@app.route("/add_feed", methods=["POST"])
def add_feed():
    name = request.form["name"].strip()
    url = request.form["url"].strip()

    # validate it's actually an RSS feed
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        return redirect("/?error=Could+not+parse+RSS+feed,+check+the+URL")

    feeds = load_feeds()
    feeds[name] = url
    save_feeds(feeds)
    return redirect("/")

@app.route("/delete_feed", methods=["POST"])
def delete_feed():
    name = request.form["name"]
    feeds = load_feeds()
    feeds.pop(name, None)
    save_feeds(feeds)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)