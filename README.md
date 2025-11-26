# Instructions for the Web App


**1 - Install Necessary Tools:**

Before attempting to run this project, you will need Git and Podman installed.

Go to https://git-scm.com/install/ in order to download the latest version of Git for your operating system, run the installer and leave all the default settings as they are.

Then go to https://podman-desktop.io/downloads and download the latest version of Podman Desktop for your operating system, run the installer and leave all the default setting as as they are.

(To make sure Podman is working correctly, open a terminal and run `podman --version`)

(NOTE: Do NOT make any changes to the Dockerfile, all necessary changes are already committed in this repository)


**2 - Clone GitHub Repository to your Machine:**

Click the green "Code" button above the filetree on GitHub and copy the HTTPS link for this repository to your clipboard. (https://github.com/CamCranda11/MLFA25Project.git)

In your terminal, run `git clone https://github.com/CamCranda11/MLFA25Project.git` and when the cloning is complete, run `cd MLFA25Project/SongRecommenderApp`.


**3 - Build, Run, and Access the Web App:**

In order to build the image for the container and activate it, run the following command while in the /SongRecommenderApp directory: `podman build -t song-app .`

(This may take a moment as all dependencies will need to be downloaded)

Once the build is complete, run the following commend to run the web app: `podman run -p 3000:80 song-app`.

Once you see confirmation that the app is running, open your browser and enter localhost:3000 as the URL and the app will be there.


**4 - Use The Web App:**

You are able to search by either song name or artist when using the web app, for the best results, search using both.

Once a search has been made, a list of matches shows up, and on the right hand side, there is a "Get Recommendations" button.

When clicked, the KMeans Clustering Model will sort out all songs in the same genre as the input song, then cluster based on the features of danceability, energy, mode, speechiness, acousticness, instrumentalness, and valence, and output 10 random songs in the same cluster as the input song.



# Instructions for the Notebook (Diet Version)


**1 - Access Necessary Resources:**

Copy the MLProjectModel.ipynb file into a notebook tool of your choice like Jupyter or Colab

Download and unzip the .csv file from https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks

Drag and drop the spotify_data.csv file into the filetree in your notebook tool, ensuring it's on the top layer so that the filepath on line 7 still directs correctly.


**2 - Initial Run:**

Use the "Run All" option to have the entire program run once to ensure no errors have occured.


**3 - Search Options:**

In the second to last code cell, there is the proper search. When using this, you must enter the song and artist names *exactly* as they show on Spotify.

In the very last code cell, there is an artist search where you can find every entry in the dataset under the selected artist. Again, like with the proper search, the artist name must be *exactly* as it is shown on Spotify.


# Model Information:

This project was build using a KMeans Clustering Model, which is an Unsupervised Learning model that partitions data into K Clusters, where K is a defined number based on the input of the developer with each data point being part of the cluster with the nearest mean. These clusters are based on centroids, which are updated by the algorithm until the centroids stabilize. For my project, the most notable thing I did which could be viewed as unorthodox is intentionally setting a high K value, which is 50. Typically, lower values tend to get the job done, but due to the datasets size, over 1.1 million entries, lower K values would introduce so much bias that the model was good as a random search. By making my K value larger, it did extend the runtime of my app, but it made more accurate results.


Some of the flaws that are specific to the model are not extremely apparent in my project, but they could be issues hiding somewhere inside. One of these is how KMeans models are very sensitive to outliers, which in my model, could cause vastly different recommendations compared to the input song. Combined with the dataset issue of misclassified genres, did present a laughable output every once in a while. Another limitation of the KMeans model is the assumption that clusters are equally sized and similarly shaped. This could have contributed to the aforementioned issue, but also to a potential issue of centroid being more of a suggestion for clustering, rather than a specific truth. One final issue that I do think impacts my project is the Curse of Dimensionality. Due to my project clustering on 7 different features, there is some high dimensionality involved, which potentially reduced the effectiveness and accuracy of my project.
