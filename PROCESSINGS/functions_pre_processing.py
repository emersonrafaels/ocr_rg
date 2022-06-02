import cv2
from dynaconf import settings
import matplotlib.pyplot as plt


def plot_histogram_image(image):

    plt.hist(image.ravel(), bins=256, fc='k', ec='k')  # calculating histogram
    plt.show()


def thresh_binary(image, thresh_value,
                  max_val=settings.THRESHOLD_MAX_COLOR_VALUE):

    # REALIZANDO O THRESHOLD POR LIMIARIZAÇÃO SIMPLES
    val, thresh = cv2.threshold(image, thresh_value, max_val, cv2.THRESH_BINARY)

    return val, thresh


def thresh_otsu(image,
                min_value=settings.THRESHOLD_MIN_COLOR_VALUE,
                max_val=settings.THRESHOLD_MAX_COLOR_VALUE):

    # REALIZANDO O THRESHOLD POR LIMIARIZAÇÃO PELO MÉTODO DE OTSU
    val, thresh = cv2.threshold(image, min_value, max_val, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return val, thresh


def thresh_adaptive(image, max_val=settings.THRESHOLD_MAX_COLOR_VALUE,
                    threshold_ksize=settings.THRESHOLD_KSIZE,
                    subtract_from_mean=settings.SUBTRACT_FROM_MEAN):

    # REALIZANDO O THRESHOLD POR LIMIARIZAÇÃO POR LIMIARIZAÇÃO ADAPTATIVA
    thresh = cv2.adaptiveThreshold(image, max_val,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, threshold_ksize,
                                   subtract_from_mean)

    return thresh