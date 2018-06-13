# Photoz
A web application in which users can login, create albums that contain photos and like them!

It has been built using flask framework in python 3.5.

It is live at:

http://ec2-13-127-160-149.ap-south-1.compute.amazonaws.com/

http://ec2-13-127-160-149.ap-south-1.compute.amazonaws.com/api

Steps to run it:

- Install mysql and run the sql commands in sql.txt
- Install the requirements using `pip install -r requirements.txt`
- modify the db details in the file src/source/helpers/configuration.py
- Run the runner.py file
- Browse to http://localhost:5000 through a browser
- The UI is pretty self explanatory
- You can find the documentation (Swagger UI) of the api here: http://localhost:5000/api  
