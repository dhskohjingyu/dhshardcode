import webapp2
from google.appengine.ext import db
from google.appengine.api import users
import datetime

class Items(db.Model): #key_name = id
    Title = db.StringProperty()
    Seller = db.UserProperty()
    Description = db.StringProperty()
    Price = db.StringProperty()
    Creation_Date = db.StringProperty()
    Key_Date = db.StringProperty()
    Comments = db.ListProperty(str)

class Profile(db.Model): #key_name = email
    Name = db.StringProperty()
    Items = db.StringProperty()

class Login(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.write("""<h1>SECURITY NOT DONE. USE AT OWN RISK.</h1><br>""")
            self.response.write("""<a href="/browse">Browse Items</a><br>""")
            self.response.write("""<a href="%s">Log Out</a>""" % users.create_logout_url("/"))
        else:
            self.response.write("""<h1>SECURITY NOT DONE. USE AT OWN RISK.</h1><br>""")
            self.response.write("""<a href="%s">Log In</a>""" % users.create_login_url(self.request.uri))
    
class Browse(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.write("""<h1>HI """ + user.nickname() + """</h1>""")
        self.response.write("""<table border="1" cellspacing="0"><tr>
                                <td>Title</td>
                                <td>Seller</td>
                                <td>Price</td>
                                <td>Creation Date</td>
                                <td>Interested?</td>
                                </tr>""")
        for i in Items.all():
            self.response.write("""<tr>""")
            self.response.write("""<td>""" + i.Title + """</td>""")
            self.response.write("""<td>""" + i.Seller.nickname() + """</td>""")
            self.response.write("""<td>""" + i.Price + """</td>""")
            self.response.write("""<td>""" + i.Creation_Date + """</td>""")
            self.response.write("""<td><form name="item_detail" action="/item_detail" method="post">""")
            self.response.write("""<input type="text" value="%s" name="key_name" style="display:none">""" % str(i.Key_Date) + """</input>""")
            self.response.write("""<button type="submit">I'm interested!</button>""")
            self.response.write("""</form></td></tr>""")
        self.response.write("""</table>""")
        self.response.write("""<form method="get" action="/post_item">
                                <button type="submit">Post Item</button>
                                </form>""")

class Post_Item(webapp2.RequestHandler):
    def get(self):
        self.response.write("""<form name="item" action="/post_item_confirmed" method="post">
                                Item: <input type="text" name="title" />
                                Description: <input type="text" name="description" />
                                Price: <input type="number" name="price" />
                                <input type="submit" />
                                </form>""")

class Post_Item_Confirmed(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        seller = user
        title = self.request.get("title")
        description = self.request.get("description")
        price = self.request.get("price")
        creation_date = str((datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%d %B %Y %I:%M %p"))
        key_date = str(datetime.datetime.now() + datetime.timedelta(hours=8))
        Items(key_name = key_date, Title = title, Description = description, Price = price, Seller = seller, Creation_Date = creation_date, Key_Date = key_date).put()
        self.redirect("/browse")

class Item_Detail(webapp2.RequestHandler):
    def post(self):
        key_name = self.request.get("key_name")
        self.response.write("""Title: """ + Items.get_by_key_name(key_name).Title)
        self.response.write("""<br>Description: """ + Items.get_by_key_name(key_name).Description)
        self.response.write("""<br>Price: """ + Items.get_by_key_name(key_name).Price)
        self.response.write("""<br>Seller: """ + Items.get_by_key_name(key_name).Seller.nickname())
        self.response.write("""<br>Creation Date: """ + Items.get_by_key_name(key_name).Creation_Date)
        for comment in Items.get_by_key_name(key_name).Comments:
            self.response.write("""<br>""" + comment)
        self.response.write("""<br><form name="comment_post" action="/comment_post" method="post">
                                    <input type="text" name="key_name" style="display:none" value="%s" />
                                    <input type="text" name="comment" multiline="true" /><br>
                                    <button type="submit">Post Reply</button>
                                    </form>""" % key_name)

class Comment_Post(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        key_name = self.request.get("key_name")
        comment = user.nickname() + """ says: """ + self.request.get("comment") #needs more efficient way of storing comments
        comments_list = Items.get_by_key_name(key_name).Comments
        comments_list.append(comment)
        Items(key_name = key_name, Title = Items.get_by_key_name(key_name).Title, Description = Items.get_by_key_name(key_name).Description, \
              Price = Items.get_by_key_name(key_name).Price, Creation_Date = Items.get_by_key_name(key_name).Creation_Date, \
              Key_Date = Items.get_by_key_name(key_name).Key_Date, Seller = Items.get_by_key_name(key_name).Seller, Comments = comments_list).put()
        self.redirect("/browse")

app = webapp2.WSGIApplication([
    ('/', Login),
    ('/browse', Browse),
    ('/post_item', Post_Item),
    ('/post_item_confirmed', Post_Item_Confirmed),
    ('/item_detail', Item_Detail),
    ('/comment_post', Comment_Post)
], debug=True)
