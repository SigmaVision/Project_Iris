import cv2 as cv


##########################################################
# FUNCTIONS
##########################################################

def read_image(name: str):
    'Returns a copy of the file'
    image = cv.imread(name)
    print(name, " - ", image.shape)
    display(image, 2000, 'Initial Image')
    return image


def display(image, time: int = 2000, title: str = 'Image') -> None:
    'Display the image for a certain number of milliseconds'
    cv.imshow(title, image)
    cv.waitKey(time)
    # cv.destroyWindow(title)


def isolate_pupil(image, threshold: int):
    'Binarize value based on if it is below the threshold or not'
    x,y,c=image.shape
    x_0=x//2
    y_0=y//2
    for i in range(0,x):
        for j in range(0,y):
            importance = (-((i-x_0)/x)**2+1)**2 * (-((j-y_0)/y)**2+1)**2
            filteredThreshold = int(importance * threshold)
            if image[i,j][0] > filteredThreshold or image[i,j][1] > filteredThreshold or image[i,j][2] > filteredThreshold:
                image[i,j]=[255,255,255]
            elif(importance < 0.94):
                image[i,j]=[255,255,255]
            else:
                image[i, j] = [0, 0, 0]

    return image


def clean_pupil(image, centerX, centerY):
    x, y, c = image.shape
    rand = 43
    for i in range(0, x):
        for j in range(0, y):
            if abs(i - centerX) > rand or abs(j - centerY) > rand:
                image[i, j] = [255, 255, 255]
            else:
                continue
    return image


def center_mass(image) -> tuple:
    'Find x, y coordinate of the center of mass'
    sum_i = sum_j = 0
    total = 0
    x, y, c = image.shape
    for i in range(0, x):
        for j in range(0, y):

            if image[i, j][0] == 0:
                sum_i += i
                sum_j += j
                total += 1

    return (sum_i // total, sum_j // total)


def add_center(image, size: int):
    "Returns an image with a red square around it's center of mass"
    x, y = center_mass(image)
    for i in range(x - size, x + size):
        for j in range(y - size, y + size):
            image[i, j] = [0, 0, 255]
    return image


def avg_luminance(image):
    sum = 0
    count = 0
    x, y, c = image.shape
    for i in range(0, x):
        for j in range(0, y):
            r, g, b = image[i, j][2], image[i, j][1], image[i, j][0]
            brightness = (r + g + b) // 3
            sum += brightness
            count += 1
    print(sum // count)
    return sum // count


def fill_pupil(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(image, contours, 1, (0, 0, 0), thickness=-1)


def shape_pupil(image, centerX, centerY):
    # need to find the radius first
    cv.circle(image, (centerY, centerX), 25, (0, 255, 0), thickness=2)


def recenter_point(bottom_left: tuple, top_right: tuple) -> tuple:
    x1, y1 = bottom_left
    x2, y2 = top_right
    center = (int((x1+x2)/2),int((y1+y2)/2))
    return center

def pupil_radius(bottom_left: tuple, top_right: tuple) -> int:
    x1, y1 = bottom_left
    x2, y2 = top_right
    radius = int(((x1+x2)/4+(y1+y2)/4))
    return radius

##########################################################
# MAIN
##########################################################

run_program = 'yes'

while run_program == 'yes':
    # Read Image
    print("Which image do you want to process?")
    name = input().strip()
    image = read_image(name)

    # Binarize based on Threshold
    threshold = avg_luminance(image)
    new_img = isolate_pupil(image, threshold)
    display(new_img, 2000, 'After Binarization')

    # Blur to remove noise
    blurred = cv.medianBlur(image, 5)
    display(blurred, 2000, 'Blurred')

    # clean pupil
    centerX, centerY = center_mass(blurred)
    cleaned = clean_pupil(blurred, centerX, centerY)
    display(cleaned, 2000, 'Cleaned')
    print(center_mass(blurred))

    # fill pupil
    fill_pupil(cleaned)
    display(cleaned, 2000, 'filled')

    # Find and display center of mass
    print(center_mass(cleaned))
    center = add_center(cleaned, 5)
    display(center, 2000, 'Center added')

    # Ask user if he wishes to continue
    print("Do you want to continue the program? (yes or no)")
    run_program = input().strip()
