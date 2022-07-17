import matplotlib.pyplot as plt
import numpy as np
import cv2


def naive_decomposition(img: np.ndarray) -> list:
    """Decomposes an image into road map (reduced graph)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    X, Y, _ = img.shape
    kernel_shape = int(np.sqrt(X)), int(np.sqrt(Y))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_shape)
    # erosion is used since the logic is inverted (the intent is to dilate the image)
    expanded = cv2.erode(thresh, kernel)

    contours, hierarchy = cv2.findContours(expanded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        for p in c:
            x, y = p[0]
            img[y, x] = (0, 0, 255)

    plt.imshow(img)
    plt.show()


if __name__ == '__main__':
    img = cv2.imread("test.png")
    naive_decomposition(img)
