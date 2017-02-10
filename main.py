import os
import webapp2
import jinja2


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")


class NewPost(Handler):

    def render_newpostform(self, title="", entry="", error=""):
        #run a query:
        entries = db.GqlQuery("SELECT * from Entry ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title=title, entry=entry, error=error, entries=entries)

    def get(self):
        self.render_newpostform()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            #creates a new instance of Entry, called e
            e = Entry(title=title, entry = entry)
            #stores new Art object in database:
            e.put()
            #self.redirect("/blog")
            self.response.write("You submitted! Now what?")
        else:
            error = "We need both title and an entry"
            self.render_newpostform(title, entry, error)

class MainBlog(Handler):

    def render_topfive(self, title="", entry="", error=""):
        #run a query:
        entries = db.GqlQuery("SELECT * from Entry ORDER BY created DESC LIMIT 5")
        self.render("topfive.html", title=title, entry=entry, entries=entries)

    def get(self):
        self.render_topfive()


    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")
        self.response.write(title, entry)

app = webapp2.WSGIApplication([
    ('/' , MainHandler),
    ('/blog', MainBlog),
    ('/newpost', NewPost)
], debug=True)
