import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
    autoescape = True)

# Definitiions for a blog object
class Blog(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

# A base RequestHandler class for our app.
class Handler(webapp2.RequestHandler):
    # Method to write to page
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # Method to render page with templates
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# Handles requests coming in to root directory
class BlogFront(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("front.html", posts=posts)

#Individual post pages
class BlogPost(Handler):
    def get(self, id):
        post = Blog.get_by_id(int(id))

        if not post:
            self.redirect('/')
        else:
            self.render("permalink.html", post=post)

# Handles requests to /newpost for submitting to blog
class SubmitPost(Handler):
    def render_submit(self, title="", content="", error=""):
        self.render("write.html", title=title, content=content, error=error)

    def get(self):
        self.render_submit()

    def post(self):
        new_title = self.request.get("new-title")
        new_content = self.request.get("new-content")
        all_titles = db.GqlQuery("SELECT title from Blog")

        # If the user typed no title, error
        if (not new_title) or (new_title.strip() == ""):
            error = "Please add a post title."
            self.render_submit(new_title, new_content, error=error)

        # If the user typed no post, self-redirect and error
        elif (not new_content) or (new_content.strip() == ""):
            error = "Please type a post."
            self.render_submit(new_title, new_content, error=error)

        # On success, create a new object for the post and redirect to front
        else:
            new = Blog(title = new_title, content = new_content)
            new.put()
            self.redirect("/{0}".format(new.key().id()))

app = webapp2.WSGIApplication([
    ('/', BlogFront),
    webapp2.Route('/<id:\d+>', BlogPost),
    ('/newpost', SubmitPost)
], debug=True)
