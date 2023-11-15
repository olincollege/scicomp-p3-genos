from numpy import ndarray, absolute, count_nonzero, zeros, ones
import matplotlib.pyplot as plt
import matplotlib.image as img


def image_diff(image1:ndarray, image2:ndarray)->float:
    """
    Compute the absolute difference of two images
    """
    if image1.size != image2.size:
        raise Exception("Images must be of the same size")

    abs_diff_mat = absolute(image1- image2)
    percentage = (count_nonzero(abs_diff_mat) * 100)/ abs_diff_mat.size

    return percentage

def complete_percent(base_image:ndarray,comp_image:ndarray)->float:
    """
    Compute the complete percentage loss metric
    
    This value is the difference between the maximum loss between the base image 
    and the canvas, minus the loss of the comparison and base images, normalized
    as a percentage. 
    """
    blank  = zeros(base_image.shape)
    max_l  = image_diff(base_image, blank)

    if max_l == 0:
        raise Exception("The images provided are identical,\npreventing divide by 0 error")
    l_best = image_diff(base_image, comp_image)

    return ((max_l - l_best) / max_l) * 100


if __name__ == "__main__":
    # test case of comparing two images
    one = img.imread("../img/1.png")
    b = zeros(one.shape)
    w = ones(one.shape)
    
    print(one.shape)
    print("absdiff of:\n\twhite, black:",complete_percent(w,b))
    print("absdiff of:\n\twhite, g.png",complete_percent(w,one))



