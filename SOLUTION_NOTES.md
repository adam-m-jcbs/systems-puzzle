# Insight DevOps Engineering Systems Puzzle Solution Notes

This documents Adam Jacobs' exploration of the systems puzzle, approach to the
problem, and notes on the implemented solution. 

## Table of Contents
1. [Understanding the puzzle](SOLUTION_NOTES.md#understanding-the-puzzle)
2. [Debugging](SOLUTION_NOTES.md#debugging)
3. [Final Comments](SOLUTION_NOTES.md#final-comments)

# Understanding the puzzle

- [X] Familiarize self with puzzle code
    - [X] Fork, clone, and review all code files
    - [X] Document review
    - [X] Attempt execution as described by developer
        - [X] Verify installation of Docker and Docker Compose
        - [X] Execute as told by developer
    - [X] Document results of attempted execution

### Code review notes

The code is a basic auction platform including a database.  The source code uses
a few popular tools for achieving this.  

Flask is deployed to build the web app. Docker contains the app and
infrastructure. `flask_wtf`/`wtforms` are used to facilitate the auction web
form which uses `sqlalchemy` to help build database items.  The database is
driven by Postgres.  The auction is served via nginx.

### Initial execution notes

Developer states executing the following in the repo root will initialize the
database:
```
$ docker-compose up -d db
$ docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
```

After this, it should be possible to run the app with
```
$ docker-compose up -d
```

Results of `docker-compose up -d db`:
```
Creating network "systems-puzzle_db_network" with driver "bridge"
Creating network "systems-puzzle_web_network" with driver "bridge"
Creating volume "systems-puzzle_dbdata" with default driver
Pulling db (postgres:9.6.5)...
9.6.5: Pulling from library/postgres
85b1f47fba49: Pull complete
2d4904bea61e: Pull complete
92fb981a71b7: Pull complete
4dda1edd3e9b: Pull complete
5ea002fc8280: Pull complete
feade6b1bbeb: Pull complete
16825a5c9040: Pull complete
a4101e46b1e2: Pull complete
078d6d550d3d: Pull complete
ac9086e062cf: Pull complete
7718e622f74c: Pull complete
111246a411c9: Pull complete
Digest: sha256:2f2b1f4d9d83db7378584d7f41b15a49b2cea25956af67698f8ea80e3bdc28ba
Status: Downloaded newer image for postgres:9.6.5
Creating systems-puzzle_db_1 ... done
```

Results of 
`docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"`
are in `db_init.out`.

When running `docker-compose up -d` and attempting to connect to the platform,
the browser fails to connect.

Just listing containers is enough to see some problems:

```
$  docker container ls
CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS              PORTS                          NAMES
b54002e4607a        nginx:1.13.5              "nginx -g 'daemon of…"   2 hours ago         Up 2 hours          80/tcp, 0.0.0.0:80->8080/tcp   systems-puzzle_nginx_1
e3faf764b4a5        systems-puzzle_flaskapp   "python app.py"          2 hours ago         Up 2 hours          5001/tcp                       systems-puzzle_flaskapp_1
f2df436ede56        postgres:9.6.5            "docker-entrypoint.s…"   2 hours ago         Up 2 hours          5432/tcp                       systems-puzzle_db_1
```

We're directing traffic from 80 to 8080!  The server isn't listening to 8080.

# Debugging 

### Fix forwarding direction

The nginx server was mapping in the wrong direction:
```
services:
  nginx:
    ports:
     - "80:8080"
```
This leads to bad gateway error when connecting in browser.

Instead, we want `"8080:80"` so that requests from the browser at 8080 are
directed to the server listening on the conventional 80.  

### Fix port used by flaskapp

The next issue I found is that the default Flask app port is 5000.  If you're
like me and didn't know this, you'll discover it when you do something like
`docker-compose logs` or attach a terminal to the flask app container. 

The code, however, communicates over and exposes port 5001 as seen in
`flaskapp.conf` and `Dockerfile`.  I chose to resolve this by customizing the
flaskapp port in `app.py` with `app.run(host='0.0.0.0', port=5001)`

The network flow is now correct, and I can see the website when I direct my
browser to it.

### Bad submission redirection (Bad nginx config)

We have the site, but when trying to add an item for auction, we get bad
redirects.

I looked into this for a bit, going down some unfruitful paths.  After enough
tinkering and googling, I realized the issue was in the nginx config as found in
`conf.d/flaskapp.conf`.  `proxy_set_header` is executed twice, setting `HOST`
first to `$host` and then to `$http_host`.  By deleting the second execution and
having the first use `$http_host`, the redirect now works correctly.

I must admit this is a bit of magic to me.  I would like to learn more about
nginx config and proxy passing.  My solution works, but I'm not quite sure why
nor what exactly was wrong before (was there any reasoning behind setting `HOST`
twice, or was it just a mistake?).  This is fine for a puzzle you need to get
working, but magic fixes will bite you later in a production environment.  You
want to understand why a fix works, not just be happy it's working.

### Empty results after submission

With all of the above fixed, we see that the results printed at the end are
empty.  I put some debug prints in `success()` to confirm that the results are
indeed retrieved and in the database, but they cannot be printed in the code's
original form.

I chose to add a `__str__` dunder to the `Items` class to facilitate printing.
I know the string will be rendered as HTML, so I use HTML code for formatting.
In a more production environment it would probably be better to add a
`render_html()` or similar method, as `__str__` shouldn't really be expected to
contain HTML and most code that uses `str()` will not expect to need to render
HTML.  But it works well enough to have minimal, readable formatting of the
database items.

Once `__str__` was implemented, I tweaked the results string and build
it up by iterating over the items in the database.  After all, the query is for
all items.  I could imagine the success page needing to only show the most
recently listed items, but I like being able to see all items and to confirm
that adding multiple items works.

### Confirm success on new machine

When I can, I like to confirm my results on another machine.  In this case, I
attempted to run the code on a Fedora workstation I have.  I was perplexed to
find this did not succeed.  I kept getting permission errors.  This is because
my Fedora workstation uses SELinux for more security.  I learned that you can
[append `:Z` to
volumes](http://www.projectatomic.io/blog/2015/06/using-volumes-with-docker-can-cause-problems-with-selinux/)
in recent Docker versions to make SELinux policies happy.  Though likely not
necessary for this puzzle, I went ahead and did this in `docker-compose.yml`.  

Once this was added, I can confirm my solution works on at least two linux
distros (Arch and Fedora 30).

# Final Comments

I believe the system now achieves the basic goal of being able to take input from
a user, store it in a database, and report the contents of the database to the
user.

With more time, some things that would be nice to do would be:

- Use `nose2` or a similar framework for developing unit and integration tests.
  
- Populate the Python code with `asserts` to accelerate debugging, flagging
  errors that can be anticipated without sacrificing speed.

- Add error handling.  For example, currently the system will not accept
  descriptions or items that exceed a size of 256.  Either don't use magic
  numbers to cap the size or at least warn the user gracefully if they exceed
  size limits.

- Improve `Items` rendering to not abuse the `__str__` dunder I wrote.  Instead,
  have something like a `render_html()` method for cases where an Items instance
  needs to be formatted as HTML.

- Document the code.  This includes writing Markdown or other text documentation
  of the design and use of the code, as well as adding more comments and
  docstrings to the code itself (within reason).  At the least, I feel almost
  anything that can have a docstring should.

- Improve the design/UI.
