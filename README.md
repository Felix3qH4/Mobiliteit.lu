Last updated on: August 22nd 2025

# Real-Time Bus lateness tracker
Real-Time tracking of bus lines across Luxembourg thanks to the API of Mobiliteit.lu
Shows how late buses are at a station.
Some stations may have problems for example be unavailable at a certain moment, that is why there are black dots on the map.

DOCUMENTATION FOR THE MOBILITEIT.LU API: https://github.com/Felix3qH4/Mobiliteit.lu-API-documentation
# How to start
Start the "main.py" file. You will need Python (works on Python 3.9.10).
You will see an output while it works.
After it has updated all bus lines, it will sleep for a few minutes and then update again.
The updated content is saved when you see the program printing something to the screen, not when it is sleeping, as some update processes take longer than others, that way it is assured that all updates are done.

To see the map open "map.html" in your browser.
The map updates itself regularly (each 10 seconds or so). You can change the update speed at the bottom of "map.html" in the function window.setInterval() next to the comment indicating how much time is represented.


## Map explication
Meaning of the dots:
  - Black: No data (maybe an error or no departures/arrivals)
  - Green: No late bus or late up to 3 minutes
  - Yellow: Buses are late 3 to 6 minutes
  - Orange: Buses are late 6 to 10 minutes
  - Red: Buses are late more than 10 minutes

When you first open the map, the dots indicate the total lateness.
This means that the lateness/color of the dot is the sum of the lateness of each bus that stops at that stop.
So if Stop 1 has 5 buses and each bus is 1 minute late, the lateness will be 5 minutes for Stop 1 and the color will be yellow.
BUT that also means that if 5 buses stop at Stop 1, if 4 are on time and one is 5 minutes late, the result is the same as if all 5 were 1 minute late.

That is why you can choose on the top right: Total lateness (explained above) or Average lateness (explained below)

Average Lateness means that the total lateness is divided by the amount of buses that stop at that station.
So if we have 5 buses that stop at Station 1 and they are all 1 minute late, this gives us a total of 5 minutes.
But as we are in average lateness mode, the 5 minutes are divided by the 5 buses, so that the stop will indicate a lateness of 1 minute and thereby be green.
BUT this also means that if 4 buses are on time and one bus is 5 minutes late, it will appear as if all buses are 1 minute late, altough only one bus is very late.

You can change the criterias for the colors on the bottom right.
So that if you want green to be buses late from 0 to 5 minutes you can change that with the slider.
(Note: You will have to adapt the other sliders too if you change the time too much, so you don't just see one color.)

You can hide/show the different colors by clicking on the respective button on the bottom left.
This can be useful to see on which main roads, buses are late. You can then hide the green and black dots, so they don't cover up the rest.


# !It is possible that the API-Key will be disabled after some time. The program won't work without a valid API-Key, so you will have to ask for your own (mobiliteit.lu)(opendata-api@verkeiersverbond.lu)(I have nothing to do with them. They are the ones providing the key for the API and are a public entity from the Luxemburgish government) and ask for its request limit to be made higher!

(The API which I use and is made available to the public by mobiliteit.lu is an API from Hafas.de)
(The link to the user interface embedded on Hafas.de is: cdt.hafas.de)
(So if you don't want an API-Key you can try getting your data that way altough their API is not open to public.)
(But there are ways to get the data from their servers.)


If you have any questions, feel free to contact me.
