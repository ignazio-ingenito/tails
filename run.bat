.\lib\Scripts\activate.bat
python .\run.py

1. What command do we run to start your server?
   I used virtualenv, so before to start, you have run the activate.bat in tail\lib\Scripts
   came back to the tail dir and run the app with a python run.py.
   I've created an html index page for some testing at http://localhost:8080

2. If you had more time, what improvements would you make if any ?
   More detailed comments in the code and a more detailed documentation
   More test cases in test.py
   I had to use the SimpleCache, with more time I prefer to use memcache implementation
   
3. What bits did you find the toughest? What bit are you most proud of? In both cases, why?
   I took a little bit of extra time, to create an html page, this to show I'm not only a backend developer
   but I'm able to deal with the frontend side (the page use angular.js, materialize for styling)

4. What one thing could we do to improve this test?
   Probably a better description of the api requests/responses could help who is going to do the test