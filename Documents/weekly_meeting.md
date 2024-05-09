# Weekly meeting
- [9 May 2024](#Date-9th-May-2024)
- [2 May 2024](#Date-2th-May-2024)
- [25 April 2024](#Date-25th-April-2024)
- [18 April 2024](#Date-18th-April-2024)
- [9 April 2024](#Date-9th-April-2024)
- [26 March 2024](#Date-26th-March-2024)
- [14 March 2024](#Date-14th-March-2024)
- [5 March 2024](#Date-5th-March-2024)
- [29 February 2024](#Date-29th-February-2024)
- [15 February 2024](#Date-15th-February-2024)

## Date: 9th May 2024 

### What helped you this week?
- 

### What did you achieve?
- 

### What did you struggle with?
- 

### What would you like to work on next week?
- 

### Where do you need help from Amelia?
- 

### What are the agreements after this meeting? (to fill in after the meeting)
- 

## Date: 2th May 2024 

### What helped you this week?
- Feedback on the report draft.
- Sunshine.
- We improved our workflow for training models.


### What did you achieve?
- Finished our report draft.
- Added countdown & start button to our frontend.
- Cleaned our common words dataset.

### What did you struggle with?
- Training dynamic svm models.


### What would you like to work on next week?
- Write report.
- Experiment with dynamic models.
- Experiment with cleaning our data using PCA.

### Where do you need help from Amelia?

### What are the agreements after this meeting? (to fill in after the meeting)

## Date: 25th April 2024 

### What helped you this week?


### What did you achieve?
- Improvements on the frontend(It now shows corresponding videos when learning a common word).
- Trained a dynamic model for common words.


### What did you struggle with?
- Youtube data scraping.
- Time(model training, scraping, etc)


### What would you like to work on next week?
- Model adjustment
- Writing

### Where do you need help from Amelia?
- Which part of the report should we focus on for the draft.

- We would like to go through the intended learning outcomes and hear your interpretation of them related to our project. (https://itustudent.itu.dk/Study-Administration/Project-Work/Intended-Learning-Outcomes)

### What are the agreements after this meeting? (to fill in after the meeting)

  
## Date: 18th April 2024 

### What helped you this week?
- Reading in the book. (Chapter 7)

### What did you achieve?
- Created more data for the static asl alfabet.
- Created a better model for static asl alfabet classification.
- Improved our frontend.


### What did you struggle with?
- React, Our old code.

### What would you like to work on next week?
- Finishing touches on the frontend.
- Train/Adjust dynamic model for common signs.
- Begin writing on the report.

### Where do you need help from Amelia?


### What are the agreements after this meeting? (to fill in after the meeting)

## Date: 9th April 2024 

### What helped you this week?
- Whiteboards and Excalidraw

### What did you achieve?
- Took a step back and looked at our project proposal to find out what to priotize(We decided to priotize recognising some common signs) To do that we need to 1. Scrape data 2. Switch from the mediapipe hands library to mediapipe hollistic.
- Scrape data: The script is ready
- Hollistic model implementation for training our model: Almost done
  
### What did you struggle with?
- just about everything

### What would you like to work on next week?
- Testing/Fixing left and right hands for static images
- Evaluate dynamic data using home-made dynamic data
- Compare Kaggle and YT dataset.


### Where do you need help from Amelia?
We have sequences of frames of variable size, if there are more than our target number of frames we cut it down by selecting key frames, but if there is less than our desired number of frames we are in doubt of whether we should pad them by calculating an approximate inbetween frame or it would be better if we discard data that does not contain enough frames.

We are in doubt about how to handle the issue of left and right hands
	- We think it might confuse the model that the data contains signs made by using either left or right hands


### What are the agreements after this meeting? (to fill in after the meeting)
- 2nd of May - draft of thesis
	- Send draft on the beginning of week, 29th of April.


## Date: 26th March 2024 

### What helped you this week?
- Confidence boost from passing a very hard exam :D

### What did you achieve?
- Dockerized our application.
- CSV parsing.
- Started writing on the report, [here](https://github.com/PatNei/Bsc-Sign-Language-Recon/blob/main/Documents/BachelorProject.pdf).

### What did you struggle with?


### What would you like to work on next week?
- Improve Frontend by hiding capturing modes.
- Combining our dynamic and static model into one.
- Creating binary classifiers for all letters.



### Where do you need help from Amelia?
- What are good experiments? 

### What are the agreements after this meeting? (to fill in after the meeting)


## Date: 14th March 2024 

### What helped you this week?
-  Whiteboards

### What did you achieve?
- Trajectory classifier, "fist-up" or "fist-down"?
- Dockerized the application
- Extracting "key frames" from a image sequence.

### What did you struggle with?
- Getting an appropriate amount of frames from a sequence to satisfy the model.
- VITE

### What would you like to work on next week?
- Report writing, detailing our progress so far, classifying the first dynamic sign.
- Enable support for using two hands.
- Deploy it.

### Where do you need help from Amelia?
- Extracting "good" key frames, any tips?
- How do we train a model that isn't that sensitive to the amount of features?
  - Our first model always expected exactly 12+1 frames😭

### What are the agreements after this meeting? (to fill in after the meeting)
- 

## Date: 5th March 2024 

### What helped you this week?
- 

### What did you achieve?
- Optimized hyper parameters for multiclass model (and binary classifier) for ASL alphabet
- we implemented simple trajectories, reducing the hand to a single point
- Learning app (frontend) is now able to capture sequences of landmarks and send them off to the API.

### What did you struggle with?
- Python & React

### What would you like to work on next week?
- Creating a trajectory classifier.

### Where do you need help from Amelia?
- What are the limits of a multiclass classification model? (How would it scale with a 1000 classes?)
- How much math should be put into the report?

### What are the agreements after this meeting? (to fill in after the meeting)
-  Consider loss functions (Sci-kit magic)
	-  No blackbox
-  Consider how our application/model relates to our research question
-  Consider whether multiclass classification or binary classification is the right approach to solve our goal with the research question.
	- _Test both options_
 	- Do we care about storage issues, prediction time and available data.
 - Bring some metrics for next time. (confusion metrics,precision and accuracy)


## Date: 29th February 2024 

### What helped you this week?
- Being informed about grlib python library

### What did you achieve?
- We remade the frontend and added duolingo features.
- We analyzed and made a plan for how to handle dynamic gestures.

### What did you struggle with?
- Re-exam for the whole group
- Struggled with grlib (python library for gesture detection)

### What would you like to work on next week?
- See: [Implement model that supports motion](https://github.com/PatNei/Bsc-Sign-Language-Recon/issues/10)

### Where do you need help from Amelia?

### What are the agreements after this meeting? (to fill in after the meeting)
- Send the report to Amelia before the deadline maybe two weeks before. (can add to overleaf)
- Amelia isn't available at 15:30 but is available at 15:00
- Fill out weekly meetings before the weekly meeting (a day before)

### What are the agreements after this meeting? (to fill in after the meeting)
- Keep on working with the dynamic processing

## Date: 15th February 2024 
### If relevant, your supervisor will ask Lottie to add you to the group purrlab_students on ITU's HPC, where you will be able to find both raw and preprocessed datasets.
Are there any data relevant for our project
	
### Who did you help this week?
...
    
### What helped you this week?
- Switching from devcontainers to devbox
- Reading the book
	
### What did you achieve?
- We have a front end with media hands running
- A backend that can process data from the frontend and parse it to our model
- A first iteration of the model that works on letters
    
### What did you struggle with?
- FastAPI
- Dev environments
- It was hard to take an image from the computer and make it work on the model from the book

### What would you like to work on next week?
- Figure our how we are going to process video
    - How would it work in the frontend
    - How would we process an extra dimension for the landmarks (a period of time (video))
    - How long should a video be
    - Probably start to move away from using the book examples for our project	
    
### Where do you need help from Amelia?
- Any books you can recommend besides the ones we are already using.
- Any tips from going from processing static image data, to video data.
    
### What are the agreements after this meeting? (to fill in after the meeting)
- Show confusion matrix
- Begin writing project

