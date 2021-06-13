import cv2 as cv

##########################################################
# METHODS
##########################################################

def read_image(name):
    image = cv.imread(name)
    print(name," - ",image.shape)
    display(image, 2000,'Initial Image')
    return image


def display(image, time=2000, title = 'Image'):
    cv.imshow(title,image)
    cv.waitKey(time)


def isolate_pupil(image,threshold):
    '''(rgb_matrix, int) -> rgb_matrix
    Binarize value based on if it is below the threshold or not
    '''
    x,y,c=image.shape
    for i in range(0,x):
        for j in range(0,y):

            if not(image[i,j][0] < threshold and image[i,j][1] < threshold and image[i,j][2] < threshold):
                image[i,j]=[255,255,255]
            else:
                image[i,j]=[0,0,0]

    return image

def center_mass(image):
    sum_i = sum_j = 0
    total = 0
    x,y,c=image.shape
    for i in range(0,x):
        for j in range(0,y):

            if  image[i,j][0] == 0:
                sum_i+=i
                sum_j+=j
                total+=1

    return (sum_i//total,sum_j//total)

def add_center(image,size):
    '''
    (rgb_matrix, int) -> rgb_matrix

    Returns an image with a blue square around it's center of mass
    '''
    x,y=center_mass(image)
    for i in range(x-size,x+size):
        for j in range(y-size,y+size):
            image[i,j]=[0,0,255]
    return image


def avg_luminance(image):
    pass

##########################################################
# MAIN
##########################################################

run_program = 'yes'

while run_program == 'yes':

    # Read Image
    print("Which image do you want to process?")
    name=input().strip()
    image = read_image(name)

    # Binarize based on Threshold
    print("what is the threshold you want to try?")
    threshold=int(input().strip())
    new_img = isolate_pupil(image,threshold)
    display(new_img,2000,'After Binarization')

    # Blur to remove noise
    blurred = cv.medianBlur(image,5)
    display(blurred,2000,'Blurred')

    # Find and display center of mass
    print(center_mass(blurred))
    center = add_center(blurred,5)
    display(center,2000,'Center added')

    # Ask user if he wishes to continue
    print("Do you want to continue the program? (yes or no)")
    run_program = input().strip()