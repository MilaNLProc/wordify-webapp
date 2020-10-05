# Introduction
This is the repo for the [Wordify](https://wordify.unibocconi.it/index) web-app.

## Structure
Imagine hosting or deploying multiple web applications in production. One will have to carry out the following tasks: (i) handle static files if present, (ii) handle https connections, (iii) recover from crashes, (iv) make sure your application can scale up to serve multiple requests.

That sounds like a lot of work. But the good news is we can tools that take care of them. This web-app is composed by 3 core components:

- The [Flask](https://flask.palletsprojects.com/en/1.1.x/) app: Flask is a simple, lightweight WSGI* web application framework. It provides you with tools, libraries, and technologies that allow you to build a web service. It is a microframework designed to get started quickly and easily, with the ability to scale up to complex applications. If you want to learn Flask, you must check out this amazing [mega-tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
    
    *WSGI is the Web Server Gateway Interface. It is a specification that describes how a web server communicates with web applications, and how web applications can be chained together to process one request. A WSGI middleware component is a Python callable that is itself a WSGI application - Gunicorn in our case. A WSGI component can perform functions like:
        
        - Routing a request to different application objects based on the target URL, after changing the environment variables accordingly.
        
        - Allowing multiple applications or frameworks to run side-by-side in the same process.
        
        - Load balancing and remote processing, by forwarding requests and responses over a network.

- The [Gunicorn](https://gunicorn.org/) application server: Gunicorn is a WSGI server. Gunicorn is built so that many different web servers can interact with it. It also does not care what you used to build your web application — as long as it can be interacted with using the WSGI interface. Gunicorn takes care of everything which happens in-between the web server and your web application. Gunicorns run multiple instances of your web application, making sure that they are healthy and restart them whenever needed, distributing incoming requests across those instances, and communicate with the webserver. A Gunicorn (WSGI) server is a must when an application is deployed in production.

- The [Nginx](https://www.nginx.com/) front-end reverse proxy: Nginx is a free, open-source, high-performance HTTP server. It also serves the purpose of reverse proxy, as well as an IMAP/POP3 proxy server. It is known for its stability, rich feature set, simple configuration, and low resource consumption. Nginx and Apache are the two best web servers to host a web application. In a computer network, a reverse proxy sits between a group of servers and the clients who want to use them. The reverse proxy directs all the requests from the clients to the servers and it also delivers all the responses from the servers to the clients. In our implementation, we will use Nginx as a reverse proxy server.

Roughly speaking, these components are collated together as follows: the web server (Nginx) accepts requests, takes care of general domain logic, and takes care of handling https connections. Only requests which are meant to arrive at the application are passed on toward the application server (Gunicorn) and the application itself (Flask).

<img src="./workflow.png" width="500" />