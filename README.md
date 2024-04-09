# Recipe Sharing API

This API allows users to share recipes and find recipes. It is developed using Django rest framework. 

## Basic Features

- Custom `User` model and authentication using email and password.
- JWT authentication.
- CRUD endpoints for recipe.
- Search functionality for recipes.
- Filter search functionality for recipes
- Step-by-Step Recipes with Image and Ingredients
- Chef Verification System
- Password reset functionality.
- Documentation using `drf_spectacular`.
- Frontend is built using React.js and can be found [here](https://github.com/earthcomfy/Recipe-app).

## Quick Start

To get this project up and running locally on your computer follow the following steps.

1. Clone this repository to your local machine.
2. Create a python virtual environment and activate it.
3. Open up your terminal and run the following command to install the packages used in this project.

```
$ pip install -r requirements.txt
```
4. Run the following commands to setup the database tables and create a super user.

```
$ python manage.py migrate
$ python manage.py createsuperuser
```

5. Run the development server using:

```
$ python manage.py runserver
```

8. Open a browser and go to http://localhost:8000/.

## License

Usage is provided under the [MIT License](http://opensource.org/licenses/mit-license.php). See LICENSE for the full details.
