# secret key for generating tokens
SECRET_KEY = 'super-secret-password'

# upload folder
UPLOAD_FOLDER = './app/forms'

# allowed extensions
ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

# maximum size of upload
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# Configuration of a outlook account for sending mails
MAIL_SERVER = 'smtp.office365.com'  #'smtp.googlemail.com'
MAIL_PORT = 587  #465
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'wordify@unibocconi.it'  #'dr.priskott'
MAIL_PASSWORD = 'J!6Qmd+kdrZfM$3Y'  #'Chitarra94'
ADMINS = ['wordify@unibocconi.it']

# password
PASSWORD = '0981'
