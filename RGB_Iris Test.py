import cv2 as cv
import numpy as np


##########################################################
# FUNCTIONS
##########################################################

def read_image(name: str):
    'Returns a copy of the file'
    image = cv.imread(name)
    return image


def display(image, time: int = 2000, title: str = 'Image') -> None:
    'Display the image for a certain number of milliseconds'
    cv.imshow(title, image)
    cv.waitKey(time)
    # cv.destroyWindow(title)


def isolate_pupil(image, threshold: int):
    'Returns a binarized version of the image value based on if it is below a threshold or not'
    x, y, c = image.shape
    x_0 = x // 2
    y_0 = y // 2

    counter = 0
    original_image = image.copy()

    for i in range(0, x):
        for j in range(0, y):
            importance = (-((i - x_0) / x) ** 2 + 1) * (-((j - y_0) / y) ** 2 + 1)
            filteredThreshold = int(importance * threshold)
            if (importance < 0.92):
                image[i, j] = [255, 255, 255]
            elif image[i, j][0] > filteredThreshold or image[i, j][1] > filteredThreshold or image[i, j][
                2] > filteredThreshold:
                image[i, j] = [255, 255, 255]
            else:
                image[i, j] = [0, 0, 0]
                counter += 1

    if counter < 20:
        image = isolate_pupil(original_image, threshold * 2)

    return image


def whiten_region(image, centerX: int, centerY: int):
    "Returns the image after all pixels that are too far from the approximate center point of the pupil are whitened"
    x, y, c = image.shape
    random_range = 35  # Chosen cuz it made sense and it worked. Just don't question it ¯\_(ツ)_/¯
    for i in range(0, x):
        for j in range(0, y):
            if abs(i - centerX) > random_range or abs(j - centerY) > random_range:
                image[i, j] = [255, 255, 255]
            else:
                continue
    return image


def center_mass(image) -> tuple:
    'Returns x, y coordinate of the approximate center of mass of the pupil region'
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


def add_point(image, point: tuple, size: int):
    "Returns an image with a red square around the specified point"
    x, y = point
    for i in range(x - size, x + size):
        for j in range(y - size, y + size):
            image[i, j] = [0, 0, 255]
    return image


def find_corners(image) -> tuple:
    "Returns the coordinates of the top-left and bottom-right corners of the pupil region"
    x, y, c = image.shape
    extremities = list()

    counter = 0
    temp1 = (0, 0)
    for i in range(0, x):
        for j in range(0, y):
            r, g, b = image[i, j][2], image[i, j][1], image[i, j][0]
            if r == 0 and g == 0 and b == 0 and counter == 0:  # leftmost point
                counter += 1
                extremities.append(i)
            elif r == 0 and g == 0 and b == 0:  # rightmost point
                temp1 = i
            else:
                continue
    extremities.append(temp1)

    counter = 0
    temp2 = (0, 0)
    for j in range(0, y):
        for i in range(0, x):
            r, g, b = image[i, j][2], image[i, j][1], image[i, j][0]
            if r == 0 and g == 0 and b == 0 and counter == 0:  # topmost point
                counter += 1
                extremities.append(j)
            elif r == 0 and g == 0 and b == 0:  # bottommost point
                temp2 = j
            else:
                continue
    extremities.append(temp2)
    return (extremities[0], extremities[3]), (extremities[1], extremities[2])


def average_luminance(image) -> int:
    "Returns the average luminance found across the entire image for thresholding purposes"
    sum = 0
    count = 0
    x, y, c = image.shape
    for i in range(0, x):
        for j in range(0, y):
            r, g, b = image[i, j][2], image[i, j][1], image[i, j][0]
            brightness = (r + g + b) // 3
            sum += brightness
            count += 1
    return sum // count / 2


def fill_pupil(image) -> None:
    "Fills the area of the pupil reflecting light due to the picture's flash in black"
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(image, contours, 1, (0, 0, 0), thickness=-1)


def circle_region(image, centerX: int, centerY: int, radius: int) -> None:
    "Draws a circle around a specified area on the picture. Used to identify the pupil and iris regions of the eye"
    cv.circle(image, (centerY, centerX), radius, (0, 255, 0), thickness=2)


def recenter_point(bottom_left: tuple, top_right: tuple) -> tuple:
    "Returns the coordinates of the re-centered center point of the pupil region"
    x1, y1 = bottom_left
    x2, y2 = top_right
    center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
    return center


def pupil_radius(bottom_left: tuple, top_right: tuple) -> int:
    "Returns the radius of the pupil region"
    x1, y1 = bottom_left
    x2, y2 = top_right
    radius = int((abs(x2 - x1) / 4 + abs(y2 - y1) / 4))
    return radius


def isolate_iris(image, alpha: float, beta: int):
    new_image = np.zeros(image.shape, image.dtype)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            for c in range(image.shape[2]):
                new_image[y, x, c] = np.clip(alpha * image[y, x, c] + beta, 0, 255)
    return new_image


def simon_iris_radius(image, pupil_center: tuple, pupil_radius: int) -> int:
    image = isolate_iris(cv.medianBlur(image, 7), 1.2, 50)
    y = pupil_center[0]
    x = pupil_center[1] + pupil_radius
    past_bright = 0
    current_bright = 0
    highest_recorded = (0, 0)
    for i in range(60):
        if i < 30:
            x += 1
        elif i == 31:
            r1, g1, b1 = image[y, x][2], image[y, x][1], image[y, x][0]
            past_bright = r1 + g1 + b1
            x += 1
        else:
            r2, g2, b2 = image[y, x][2], image[y, x][1], image[y, x][0]
            current_bright = r2 + g2 + b2
            difference = current_bright - past_bright
            if difference > highest_recorded[0]:
                highest_recorded = (difference, x)
            past_bright = current_bright
    return abs(highest_recorded[1] - pupil_center[1])



def iris_radius(image, pupil_center: tuple, pupil_radius: int) -> int:
    "Returns the radius of the iris region"
    image = isolate_iris(cv.medianBlur(image, 7), 1.2, 50)
    memory = []

    class Elem:
        def __init__(self, image, x, y, length):
            self.x = x
            self.y = y
            self.length = abs(length)
            temp = []
            for i in range(length):
                r, g, b = image[y, x+i][2], image[y, x+i][1], image[y, x+i][0]
                temp.append((r + g + b) // 3)
            self.contrast = max(temp) - min(temp)
            self.isRight = temp.index(max(temp))>temp.index(min(temp))

    length = 5
    x = pupil_center[1] + pupil_radius
    for i in range(13):
        y = pupil_center[0]
        hll = Elem(image, x, y, length)
        if hll.isRight:
            memory.append(hll)
        x += length


    current_max = Elem(image, pupil_center[0], pupil_center[1], length)
    for elem in memory:
        if elem.contrast > current_max.contrast:
            current_max = elem

    iris_radius = current_max.x - pupil_center[1]
    return abs(iris_radius) + pupil_radius


def yassine_iris_radius(image, pupil_center: tuple, pupil_radius: int) -> int:
    "Returns the radius of the iris region"
    image = cv.medianBlur(image, 7)
    memory = []

    class Elem:
        def __init__(self, image, x, y, length):
            self.x = x
            self.y = y
            self.length = length
            temp = []
            for i in range(length):
                r, g, b = image[y, i][2], image[y, i][1], image[y, i][0]
                temp.append((r + g + b) // 3)
            self.contrast = max(temp)

    for i in range(1):
        y = pupil_center[0]
        x = pupil_center[1] + pupil_radius + 5
        memory.append(Elem(image, x, y, 5))
        x += 5

    current_max = Elem(image, pupil_center[0], pupil_center[1], 5)
    for i in range(len(memory)):
        if i == 0:
            continue
        else:
            contrast_diff = memory[i - 1].contrast - memory[i].contrast
            if contrast_diff < current_max.contrast:
                current_max = memory[i]

    iris_radius = current_max.x - pupil_center[1]
    return abs(iris_radius)


def p1_identify_regions():
    "Part 1 -  Prints details and outputs the utilized identification process for the pupil and iris regions of an eye"
    run_program = 'yes'

    while run_program == 'yes':
        # Read the image
        print("Which image do you want to process?")
        name = input().strip()
        original_image = read_image(name)
        image = read_image(name)

        # Display the original image and print its properties
        print('Image Properties: \n', 'Name:', name, "\n", 'Width:', original_image.shape[0], "pixels\n", 'Height:',
              original_image.shape[1], 'pixels')
        display(image, 2000, 'Original')

        # Find average luminance - threshold
        threshold = average_luminance(image)
        print('Average luminance - threshold value:', threshold, 'RGB')

        # Binarize image based on threshold
        binarized = isolate_pupil(image, threshold)
        display(binarized, 2000, 'After Binarization')

        # Median blur to remove noise

        blurred = cv.medianBlur(binarized, 7)
        display(blurred, 2000, 'Blurred')

        # Find approximate center of mass of the pupil region
        centerX, centerY = center_mass(blurred)
        print('Pupil region approximate center of mass:', center_mass(blurred))

        # Whiten picture to isolate pupil region
        whitened = whiten_region(blurred, centerX, centerY)
        display(whitened, 2000, 'Whitened')

        # Fill the pupil region in black
        fill_pupil(whitened)
        display(whitened, 2000, 'Filled')

        # Find top-left and bottom-right corners of the pupil region
        corners = find_corners(whitened)
        print('Top-left corner:', corners[0], ' - ', 'Bottom-right corner:', corners[1])

        # Find the exact center of mass of the pupil region
        center = recenter_point(corners[0], corners[1])
        print('Exact center of mass:', center)

        # Add the point of the exact center of mass of the pupil region
        add_point(whitened, center, 5)
        display(whitened, 2000, 'Center')

        # Find the radius of the pupil region
        radius = pupil_radius(corners[0], corners[1])
        print('Pupil radius =', radius, 'pixels')

        # Circles the pupil region on the original image
        circle_region(original_image, center[0], center[1], radius)
        display(original_image, 2000, 'pupil')

        # Find radius of the iris region
        # thresh = 255 - threshold
        # iris_rad = iris_radius(image, center, radius, thresh)
        # print("Iris radius =", iris_rad, 'pixels')

        iris = simon_iris_radius(read_image(name), center, radius)
        print("Iris radius =", iris, " pixels")

        # Circles the iris region on the original image
        circle_region(original_image, center[0], center[1], iris)
        display(original_image, 2000, 'iris')

        # Ask user if he wishes to continue and repeat the process
        print("Do you want to continue the program? (yes or no)")
        run_program = input().strip()


def p1_only_details():
    "Part 1 - Only prints details. Does not display the region identification process and transformations"
    run_program = 'yes'

    while run_program == 'yes':
        # Read the image
        print("Which image do you want to process?")
        name = input().strip()
        original_image = read_image(name)
        image = read_image(name)

        # Print original image properties and display original
        print('Image Properties: \n', 'Name:', name, "\n", 'Width:', original_image.shape[0], "pixels\n", 'Height:',
              original_image.shape[1], 'pixels')

        # Find average luminance - threshold
        threshold = average_luminance(image)
        print('Average luminance - threshold value:', threshold, 'RGB')

        # Binarize image based on threshold
        binarized = isolate_pupil(image, threshold)

        # Median blur to remove noise
        blurred = cv.medianBlur(binarized, 7)

        # Find approximate center of mass of the pupil region
        centerX, centerY = center_mass(blurred)
        print('Pupil region approximate center of mass:', center_mass(blurred))

        # Whiten picture to isolate pupil region
        whitened = whiten_region(blurred, centerX, centerY)

        # Fill the pupil region in black
        fill_pupil(whitened)

        # Find top-left and bottom-right corners of the pupil region
        corners = find_corners(whitened)
        print('Top-left corner:', corners[0], ' - ', 'Bottom-right corner:', corners[1])

        # Find the exact center of mass of the pupil region
        center = recenter_point(corners[0], corners[1])
        print('Exact center of mass:', center)

        # Find the radius of the pupil region
        radius = pupil_radius(corners[0], corners[1])
        print('Pupil radius =', radius, 'pixels')

        # Find radius of the iris region
        iris_rad = simon_iris_radius(image, center, radius)
        print("Iris radius =", iris_rad, 'pixels')

        # Ask user if he wishes to continue and repeat the process
        print("Do you want to continue the program? (yes or no)")
        run_program = input().strip()


##########################################################
# MAIN
##########################################################

p1_identify_regions()
# p1_only_details()
