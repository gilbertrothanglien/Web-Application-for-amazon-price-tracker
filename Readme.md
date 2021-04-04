# cs50TrackPrice
#### Video Demo:  <URL HERE>
#### Description:
##### Hello this is my final project for cs50: Introduction to computer science. My project tracks price of a product on amazon and sends email to user when the price drops to or below the user specified price.
##### **Static Folder**: This folder contains all the static files like .css, .js files etc.
##### **Templates Folder**: This folder contains all the html files for our web page.
##### **application.py**: This is a flask application that runs and maintains all the things done by the user. It takes in the user input and stores it to the database. Maintain all the login, register, track price, etc. input by the user.
##### **helpers.py**: contains login_required function that I use in application.py so that every user will need to login/register before they can use the application
##### **database.db**: Contains all the information of users.
##### **track.py**: This python program runs in parallel with the flask application so that in will look into the database and compare each price with current online price for the user. If the price of the online site is lower or equal to the user input, it will send an email to the user notifying that the price has dropped.
