import matplotlib.pyplot as plt
import numpy as np
import cv2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
VERTEX = (0, 0, 255)


def naive_vertex_extraction(img: np.ndarray) -> np.ndarray:
    """Extracts future graphs' vertices by finding contours of an eroded image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    X, Y, _ = img.shape
    kernel_shape = int(np.sqrt(X)), int(np.sqrt(Y))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_shape)
    # erosion is used since the logic is inverted (the intent is to dilate the image)
    expanded = cv2.erode(thresh, kernel)

    contours, hierarchy = cv2.findContours(
        expanded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    for c in contours:
        for p in c:
            x, y = p[0]
            img[y, x] = VERTEX

    return img


def merge_neighbours(img: np.ndarray):
    """Merges groups of vertices into more solitary points of interest. Works well a with 3x3 window."""
    X, Y, _ = img.shape
    for i in range(1, X - 1):
        for j in range(1, Y - 1):
            if np.any(img[i, j] != VERTEX):
                continue
            window = img[max(0, i - 1):min(i + 2, X), max(0, j - 1):min(j + 2, Y), :]
            XX, YY, _ = window.shape
            for ii in range(XX):
                for jj in range(YY):
                    if ii == jj:
                        continue
                    if np.all(window[ii, jj] == VERTEX):
                        img[i, j] = WHITE
    return img


def image_to_graph(img: np.ndarray):
    """Returns networkx graph"""
    ...


if __name__ == "__main__":
    img = cv2.imread("test.png")
    img = naive_vertex_extraction(img)
    plt.figure()
    plt.imshow(img)
    plt.show()
    img = merge_neighbours(img)
    plt.figure()
    plt.imshow(img)
    plt.show()
