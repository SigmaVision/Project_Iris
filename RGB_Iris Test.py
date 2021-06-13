import cv2 as cv

##########################################################
# METHODS
##########################################################

def read_image(name):
    image = cv.imread(name)
    print(name," - ",image.shape)
    display(image, 20,'Initial Image')
    return image


def display(image, time=100, title = 'Image'):
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

def avg_luminance(image):
    pass

##########################################################
# MAIN
##########################################################
print("Do you want to run the program? (yes or no) /n")
run_program = input().strip()
while run_program == 'yes':
    print("Which image do you want to process? /n")
    name=input().strip()
    
    image = read_image(name)

    print("what is the threshold you want to try? /n")
    threshold=int(input().strip())
    new_img = isolate_pupil(image,threshold)

    display(new_img,50,'final')

    print(center_mass(new_img))

    print("Do you want to continue the program? (yes or no) /n")
    run_program = input().strip()