[//]: # (Image References)
[image_0]: ./misc/rover_image.jpg
[image_1]: ./misc/rover_lab_notebook.jpg
[image_2]: ./misc/rover_lab_notebook_2.jpg
[image_3]: ./misc/rover_lab_notebook_3.jpg
[image_4]: ./misc/rover_code_snippet.jpg
[![Udacity - Robotics NanoDegree Program](https://s3-us-west-1.amazonaws.com/udacity-robotics/Extra+Images/RoboND_flag.png)](https://www.udacity.com/robotics)
# Search and Sample Return Project


![alt text][image_0] 

This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) and it will give you first hand experience with the three essential elements of robotics, which are perception, decision making and actuation.  You will carry out this project in a simulator environment built with the Unity game engine.  

## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Dependencies
You'll need Python 3 and Jupyter Notebooks installed to do this project.  The best way to get setup with these if you are not already is to use Anaconda following along with the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit). 


Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Recording Data
I've saved some test data for you in the folder called `test_dataset`.  In that folder you'll find a csv file with the output data for steering, throttle position etc. and the pathnames to the images recorded in each run.  I've also saved a few images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, you should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the lesson for performing the various steps of this project.  The notebook should function as is without need for modification at this point.  To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py` and it's your job to fill in the function called `perception_step()` with the appropriate processing steps and update the rover map. `decision.py` includes another function called `decision_step()`, which includes an example of a conditional statement you could use to navigate autonomously.  Here you should implement other conditionals to make driving decisions based on the rover's state and the results of the `perception_step()` analysis.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!  It doesn't drive that well yet, but it's your job to make it better!  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results!  Make a note of your simulator settings in your writeup when you submit the project.**


## Project: Search and Sample Return
---
### Writeup / README
### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

I first ran the functions in the notebook to see what they did. After going through and understanding how, I modified them to test changes in thresholding to produce the best filter for the navigable terrain as well as the gold rocks. I also tried several different ways to produce a nice warped navigation image. I only used the test images provided because it was just easier and could randomly generate another to test multiple cases with the default code that called in images.

![alt text][image_1] 

![alt text][image_2]

#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap. Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.

It did not take long to finish the functions for identifying navigable terrain, obstacles and rock samples. It was a simple mask and apply to different channels, and taking each respective set of pixels and transform them to the rover coordinate system for recognition of its path, and then further coordinate transformation to world pixels was done through the transform functions. I was also able to Locate rock samples with a square indicator using the closest pixel of the sample to the rover in the provided test data but later found out it was unnecessary and was already provided.

![alt text][image_3]
 

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

I modified the perception.py script to mirror the same functions that were created earlier and modified in the online notebook. I modified the decision.py script to include a conditional statement if it got stuck using the telemetry, so if the throttle was active but the velocity was zero, it would back up and turn as if to perform a three point turn. I tried modifying the steering command to hug the wall with an offset to the default output but it either hugged the wall too much or not enough so I wasn’t able to find the magic number.

![alt text][image_3] 

#### 2. Launching in autonomous mode your rover can navigate and map autonomously. Explain your results and how you might improve them in your writeup.

After trying different techniques, I found that with the default steering decision, the robot was able to traverse around obstacles and to all branches of the map well and was able to map on average 75% and with a fidelity of around 60%. Identifying the rocks was easy but I did not pick them up. So to improve, I would add a conditional statement that if a rock was recognized, it would use the location of the pixels to guide it toward the rock, and when close enough to stop and pick it up. Also, I would improve by finding the right steering condition for it to hug the wall. I used the fantastic graphics with a resolution of 1280 x 1024 with the default FPS setting in drive_rover.py.