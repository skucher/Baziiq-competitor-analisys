from google.appengine.api import users
from google.appengine.ext import webapp

supported_users = ['povichu4er', 'sergeyku4er','alexpov','natan.nar']

class LoginPage(webapp.RequestHandler):
    
    
    def get(self):
        user = users.get_current_user()
        
        if user:
            if str(user) not in supported_users:
                self.response.out.write('%s Sorry you are not authorised to use this app' % user)
                return
            self.redirect('/reports')
            self.response.out.write(
                'Hello %s <a href="%s">Sign out</a><br>Is administrator: %s' % 
                (user.nickname(), users.create_logout_url("/"), users.is_current_user_admin())
            )
        else:
            self.redirect(users.create_login_url(self.request.uri))