import logging
from app import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
   
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
	
