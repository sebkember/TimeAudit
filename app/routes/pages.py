from flask import make_response, render_template

from ..utils.auth import get_authenticated_user

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route("/privacy-policy", methods = ["GET"])
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/terms-of-service", methods = ["GET"])
def terms_of_service():
    return render_template("terms.html")

@app.route("/robots.txt", methods= ["GET"])
def robots_txt():
    # Create a response object
    response = make_response("User-agent: *\nDisallow: /api/\nSitemap: https://timeaudit.net/sitemap.xml")

    # Set the content type to text/plain
    response.headers["Content-Type"] = "text/plain"
    
    return response

@app.route("/sitemap.xml", methods=["GET"])
def sitemap_xml():
    # Create a response object
    response = make_response(render_template("sitemap.xml"), 200)

    # Set the content type to application/xml
    response.headers["Content-Type"] = "application/xml"
    
    return response

@app.route("/audit", methods = ["GET", "POST"])
def audit():
    user = get_authenticated_user(request)
    if user:
        _, email, streak = user
        return render_template("statistics.html", email_address=email, streak=streak)  
    return render_template("statistics.html")

@app.route('/calendar')
def calendar():
    user = get_authenticated_user(request)
    if user:
        _, email, streak = user
        return render_template("calendar.html", email_address=email, streak=streak)
    return render_template("calendar.html")

@app.route('/tasks')
def tasks():
    user = get_authenticated_user(request)
    if user:
        _, email, streak = user
        return render_template("tasks.html", email_address=email, streak=streak)
    return render_template("tasks.html")