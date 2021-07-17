import cv2 as cv


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


# Review
def isolate_pupil(image, threshold: int):
    'Returns a binarized version of the image value based on if it is below a threshold or not'
    x, y, c = image.shape
    x_0 = x // 2
    y_0 = y // 2
    for i in range(0, x):
        for j in range(0, y):
            importance = (-((i - x_0) / x) ** 2 + 1) ** 2 * (-((j - y_0) / y) ** 2 + 1) ** 2
            filteredThreshold = int(importance * threshold)
            if image[i, j][0] > filteredThreshold or image[i, j][1] > filteredThreshold or image[i, j][
                2] > filteredThreshold:
                image[i, j] = [255, 255, 255]
            elif (importance < 0.94):
                image[i, j] = [255, 255, 255]
            else:
                image[i, j] = [0, 0, 0]
    return image


# Review
def whiten_region(image, centerX, centerY):
    "Returns the image after all pixels that are too far from the approximate center point of the pupil are whitened"
    x, y, c = image.shape
    random_range = 43  # number of pixels away from the approximate center point of the pupil. Implement dynamically.
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
    return sum // count


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


def iris_radius(image, pupil_center: tuple, pupil_radius: int, threshold: int) -> int:
    "Returns the radius of the iris region"
    x = pupil_center[0] - pupil_radius
    edge = False
    while not edge and x != 0:
        r, g, b = image[x, pupil_center[1]][2], image[x, pupil_center[1]][1], image[x, pupil_center[1]][0]
        if r >= threshold or g >= threshold or b >= threshold:
            edge = True
        x -= 1
    return pupil_center[0] - x + pupil_radius


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
        blurred = cv.medianBlur(image, 5)
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

        # Find radius of the iris region
        thresh = 255 - threshold
        iris_rad = iris_radius(image, center, radius, thresh)
        print("Iris radius =", iris_rad, 'pixels')

        # Circles the pupil region on the original image
        circle_region(original_image, center[0], center[1], radius)
        display(original_image, 2000, 'pupil')

        # Circles the iris region on the original image
        circle_region(original_image, center[0], center[1], iris_rad)
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
        isolate_pupil(image, threshold)

        # Median blur to remove noise
        blurred = cv.medianBlur(image, 5)

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
        thresh = 255 - threshold
        iris_rad = iris_radius(image, center, radius, thresh)
        print("Iris radius =", iris_rad, 'pixels')

        # Ask user if he wishes to continue and repeat the process
        print("Do you want to continue the program? (yes or no)")
        run_program = input().strip()

##########################################################
# MAIN
##########################################################

# p1_identify_regions()
# p1_only_details()
