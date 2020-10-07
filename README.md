Usage
-----
- Using virtualenv is highly recommended.
- Have django installed.
- Clone the repository.
- Install requirements.
- Run migrations.
- Create django superuser.
- Run development server.

```bash
python -m venv venv
. ./venv/bin/activate
pip install django
git  clone https://github.com/andristaurenis/django-homework
cd django-homework
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com
python manage.py runserver
```

Documentation
-------------
I did spend a lot more than two evenings on this project. Most of it was dealing with django specific boilerplate. Wanted to do everything properly. If I had to do a similar task from scratch in django again I expect to be able to finish in two evenings. At one point automatic tests worked, but now they do not. Sadly I am out of time.

Test version is hosted at http://78.58.52.209/ it has 1 admin and 3 users:
- Username admin Password admin
- Username a Password a
- Username b Password b
- Username c Password c

Implementation details:
- Each vote corresponds to a row in DB that has a weight. Weight is calculated at time of voting.
  Alternative implementation that was considered: To have one row for each user-restaurant pair and have an integer column for "numberOfVotesCast".
  Chosen solution is believed to be more flexible to possible changes in the future.
  Also it allows to leverage SQL more.
- Number of votes for user can be configured from the admin panel in user view. No API method was implemented for this purpose.
- Active voting information is in the same table as voting history. For each of tables Restaurant and RestaurantChoiceHistory there is one sentry row crated at the initial migration script. Sentry in RestaurantChoiceHistory is used to keep track of active ongoing voting. Sentry in Restaurant was a foreign key necessity. A sentry in Vote table was also considered as it would resolve the problem of not having any votes when voting is finished, but it seems to add more problems than it resolves.
- Restaurants are not actually deleted but have a column "deletedAt" that gets set. This is done so that they would remain in history.
- When voting is supposed to finish server expects to have an endpoint called.
  Alternative implementation that was considered: Have a daemon-like construction running in the background that performs the task of finishing voting automatically.
  Alternative solution is more work for the programmer that could be pushed to DevOps. Django does not provide a place in the architecture for such a daemon.
  See Known bugs.
- Project was started from the following skeleton: https://github.com/Mischback/django-project-skeleton

Known bugs:
- There are possible race conditions. User could vote vote more than allowed, or the weights could be wrong if he votes fast enough. Voting at the same time when voting is closed can also produce unexpected results.
  Solution: Add database locks. For votes they can be on per user basis.
  Lock votes table for everyone when finishing the voting.
- When restaurant name is changed the history does not reflect this.
  Solution: Pretend its a feature.
- 'django.middleware.csrf.CsrfViewMiddleware' is disabled in settings. (lack of understanding in browser sessions)
  Solution: Unknown
- 'finalizeRestaurantChoice' can be called arbitrarily.
  Solution: Do not allow this method to be called too frequently.
  For testing purposes this lack of functionality is very useful and that is why it is left there.
  To do this properly .env file loading has to be implemented.
- Use of ' and " are not consistent.
  Solution: Set up stricter linter. There might be other problems of such sort.
