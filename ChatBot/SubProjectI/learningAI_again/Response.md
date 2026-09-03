 In Django, you can create migration by running the following commands:

1. **Run `makemigrations`**: This command will automatically create migration files based on any changes made to your models.

```bash
python manage.py makemigrations
```

2. **Run `migrate`**: After creating migration files, this command will apply those migrations to your database.

```bash
python manage.py migrate
```

However, if you want to make manual changes to the database without running migrations every time, you can use Django's built-in commands:

1. **Create a new migration manually**: You can create a new migration file by running `makemigrations` with the `-m` option and specifying the model(s) that have been modified.

```bash
python manage.py makemigrations myapp --fake
```

Replace `myapp` with the name of your app.

2. **Apply the manual migration**: Once you've created a new migration, you can apply it to your database using the `migrate` command.

```bash
python manage.py migrate --fake-apps myapp
```

Again, replace `myapp` with the name of your app.

**Using Django's migrations in a real-world scenario**

Here's an example of how you might use migrations when creating models:

Let's say we have two models: `Book` and `Author`.

In our `models.py`, we define these models as follows:
```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)

class Author(models.Model):
    name = models.CharField(max_length=100)
```
To create the initial migration, we run:

```bash
python manage.py makemigrations
```

This will generate a new file in our `migrations` directory containing the necessary SQL to create these tables. When we run `makemigrations` again after making changes to our models (e.g., adding more fields or changing existing ones), it will automatically update the migration files and apply those changes to our database.

For example, let's say we modify the `Book` model as follows:

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    publication_date = models.DateField()
```
If we want to create a new migration that includes these changes, we can run:

```bash
python manage.py makemigrations myapp --fake
```

This will generate a new file in our `migrations` directory containing the necessary SQL to apply these changes to our database.

Remember to always review and test your migrations before applying them to your production database!