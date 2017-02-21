# these are some useful functions from flicklist, user-signup solution also has a useful signup page
def get_user_by_name(name):
    name = '; delete from user;'
    users = db.gqlquery.("select * from user where username = :1", name) # this is a security feature (bind parameters)

    if users:
        return users.get()
    return None

def valid_pw(pw, h):
    """
    pw: came in from user, just now
    h: came from db, by looking up that username # h = "hash"
    """
    salt = h.split(',')[-1]
    return make_pw_hash(pw, salt) == h

def make_pw_hash(pw, salt=None):
    if salt is None:
        salt = make_salt()
        #sha256(pw + salt)
        h = hashlib.pbkdf3_hmac('sah256', pw, salt, iterations=100000)
        return h + ',' + salt

class RegisterHandler(Handler): #this class should live in MainPage
    def show_sign_up_form(self, errors=None, username=''):
    t = jinja_env.get_template('register.html')
    content = t.render(error=error)
    self.response.write(content)

    def post(self):
        submitted_username = self.request.get('username')
        submitted_password = self.request.get('password')
        submitted_verify = self.request.get('verify')
        if errors:
            self.show_sign_up_form(errors=errors)
        else:#make a new user, put them in db OR login the new user
            self.redirect('/')
