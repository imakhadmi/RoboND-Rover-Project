import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

def find_rocks(img):
    # define range of yellow color in RGB
    lower_yellow = np.array([110, 110, 0], dtype = 'uint8')
    upper_yellow = np.array([240, 240, 80], dtype = 'uint8')
    # Threshold the RGB image to get only yellow colors
    sample = cv2.inRange(img, lower_yellow, upper_yellow)
    return sample 

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = xpos + (xpix_rot / scale)
    ypix_translated = ypos + (ypix_rot / scale)
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))

    return warped, mask


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                  [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    
    # 2) Apply perspective transform
    warped, mask = perspect_transform(Rover.img, source, destination)
    
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed = color_thresh(warped)
    sample = find_rocks(warped)
    obstacles = np.absolute(np.float32(threshed) - 1) * mask

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = obstacles * 255
    Rover.vision_image[:,:,1] = sample * 255
    Rover.vision_image[:,:,2] = threshed * 255

    # 5) Convert map image pixel values to rover-centric coords
    scale = 2 * dst_size
    world_size = Rover.worldmap.shape[0]

    
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    yaw = Rover.yaw
    
    xpix, ypix = rover_coords(threshed) 
    navigable_x_world, navigable_y_world = pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale)
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 2
    nav_pix = Rover.worldmap[:,:,2] > 200
    Rover.worldmap[nav_pix,0] = 0
    

    oxpix, oypix = rover_coords(obstacles)
    obstacle_x_world, obstacle_y_world = pix_to_world(oxpix, oypix, xpos, ypos, yaw, world_size, scale)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    #obs_pix = Rover.worldmap[:,:,0] > 150
    #Rover.worldmap[nav_pix,2] = 0

    sxpix, sypix = rover_coords(sample)
    sdist, sangles = to_polar_coords(sxpix, sypix) 
    mean_dir = np.mean(sangles)
    if sample.any():
        closest_point = sypix.min()
        middle_point = sxpix.mean()
        #if closest_point < 80:
        sample_x_world, sample_y_world = pix_to_world(middle_point, closest_point, xpos, ypos, yaw, world_size, scale)
        Rover.worldmap[sample_y_world, sample_x_world, :] += 10
            #xlocs = [item[0] for item in rock_locations]
            #ylocs = [item[1] for item in rock_locations]
            #closelocs=[]
            #for n in range(len(xlocs)):
            #    difx = np.abs(sample_x_world - xlocs[n])
            #    dify = np.abs(sample_y_world - ylocs[n])
            #    if difx < 20 and dify < 20:
            #        closelocs.append([difx,dify])
            #if len(closelocs) == 0:
            #    rock_locations.append([sample_x_world,sample_y_world])
                #rock_points = np.float32([[int(sample_x_world) - 2 , int(sample_y_world)],
                #                      [int(sample_x_world) + 2 , int(sample_y_world)],
                #                      [int(sample_x_world) + 2 , int(sample_y_world) - 4],
                #                      [int(sample_x_world) - 2 , int(sample_y_world) - 4]])
            #    rock_points = np.float32([[int(sample_x_world) , int(sample_y_world)],
            #                          [int(sample_x_world) + 4, int(sample_y_world) +4]])
            #    cv2.rectangle(Rover.worldmap, (np.int32(rock_points[0][0]),np.int32(rock_points[0][1])), (np.int32(rock_points[1][0]),np.int32(rock_points[1][1])), (200, 200, 200), -1)
                #Rover.samples_located +=1

    # 6) Convert rover-centric pixel values to world coordinates
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    dist, angles = to_polar_coords(xpix, ypix) 
    mean_dir = np.mean(angles>1.047)
    Rover.nav_dists = dist
    Rover.nav_angles = angles
 
    
    
    return Rover