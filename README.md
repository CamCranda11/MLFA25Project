# Cameron's Song Recommendation Tool

This is the repository for my song recommendation web application built on a K-Means Clustering model to recommend songs from a dataset of 1 million songs from Spotify, released between 2000 and 2023. This README acts as documentation for each session of work.

# Session 1 - 10/29/25, 10:24 AM
Created repo and added this README

# Session 2 - 10/29/25, 10:29 AM
After consulting a few sources, I have elected to shift my model to a K-Means Clustering model as that would make my end goal more attainable. A Random Forest model could work in theory, but it would train heavily on user data which would not provide a complete project in time for the due date.

# Session 3 - 10/29/25, 12:00 PM
I have built my model and have a few example use cases. I have yet to implement a search option and it will require some tests in order to judge its accuracy. Current outlook is good.

# Session 4 - 10/30/25, 10:02 AM
I have added more features to my model and expanded my k yet again to create a more refined model. I plan to add a system to sort into genres after clustering to create a more organized output.

# Session 5 - 10/30/25, 12:41 AM
I have added a code block to find all songs by a specific artist, and I believe the way the dataset was created was using artists on some form of supported label as I did not find any independent artists during my searching. I also added a block of code to use when I am ready to save my clustered data.

# Session 6 - 10/31/25, 3:02 PM
I have restructured the actual code to cluster within genre as a part of the search, instead of initializing clusters at the start. This should hopefully create a more accurate model and a faster program.

# Project Milestone - 11/11
Unfortunately, not many changes in the last week and a half, but I did go through rigorous testing and believe my model is ready to be turned into a web app. The way it works is:
1 - When a search is made, the program finds every song in the dataset that is in the same genre as the one being searched.
2 - After all the songs in the genre are compiled, the program uses a K-Means Clustering model to find the closest options to the song and outputs 5 random ones.
By clustering after I sort, I have a program that runs quickly, while still being accurate and having some necessary variance.
