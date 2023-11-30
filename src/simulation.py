from src.custom_types import Polygon, Vertex, RGBA, Canvas
from src.reconstruction import polygon_init, polygon_mutate
from src.visualize import add_polygon, visualize_canvas
from src.loss import sad
from PIL import Image
from numpy import array
from copy import copy, deepcopy
import numpy as np


class Simulation:
    def __init__(self, **kwargs):
        """
        Init simulation.
        Keywords:
            - Base image
            - Output image
            - Max generations / polygons
            - Stagnation limit
            - Number evaluations
            - Number Verticies
        """
        self.base_image: np.ndarray = np.asarray(Image.open(kwargs.get("b_image")))
        self.output_image = kwargs.get("o_image")
        self.max_polygons: int = kwargs.get("m_poly", 10)
        self.stagnation_limit: int = kwargs.get("stag_lim", 10)
        self.n_verticies: int = kwargs.get("n_vert", 3)
        self.num_evals: int = kwargs.get("n_evals", 50000)
        # NOTE: this value is from the paper

        # Derived class variables
        self.height, self.width = self.base_image.shape
        self.canvas = Canvas(list())
        self.counter = 0

        self.canvas = self.create_polygon(self.canvas)

    def update_probabilities(
        self,
    ):
        """
        Choose a polygon to mutate weighted by the sequence probabilities
        """
        num = self.canvas.how_many()

        # Generate Geometric series of probabilities for the sequence
        probabilities = array([1 / (2 ** (1 + x)) for x in range(num)])

        # Normalize the probabilities to 1
        n_probabilities = probabilities / np.sum(probabilities)
        self.probabilities = n_probabilities
        return n_probabilities

    def norm_opti_probs(
        self,
    ):
        """
        Create a uniform distribution with mg elements, where mg is the max
        generations / max number of polygons
        """
        self.probabilities = [1 / self.max_polygons] * self.max_polygons
        return self.probabilities

    def eval_loss(self, image: Canvas):
        """
        Evaluate an image to the base_image and return the SAD
        """
        return sad(self.base_image, image.image())

    def cc_loss(self, parent: Canvas, child: Canvas) -> tuple[float, float]:
        """
        Compute and compare loss
        """

        # compute the loss of the child iteration with the parent
        l_parent = self.eval_loss(parent)
        l_child = self.eval_loss(child)

        return l_parent, l_child

    def select(
        self,
    ):
        """
        Using probabilities, randomly select and return a polygon from the
        canvas sequence and its index
        """
        indx, self.polygon_i = np.random.choice(
            list(enumerate(self.canvas.sequence)), p=self.probabilities
        )

        return indx, self.polygon_i

    def create_polygon(self, c: Canvas):
        """
        Create polygon and add it to the canvas
        """

        c = add_polygon(canvas=c, polygon=polygon_init(id=c.how_many()))

        # self.counter = 0
        self.update_probabilities()
        return c

    def run(
        self,
    ):
        """
        Run the simulation until completion.
        """

        # initialize vars
        t = 0

        generations = [self.canvas]

        newer_solution = None
        older_solution = None
        # get loss of current solution
        v_k = self.eval_loss(self.canvas)

        while t <= self.num_evals:
            _indx, self.polygon_i = self.select()

            # use temporary variables to store previous and current solutions
            older_solution = self.canvas
            newer_solution = polygon_mutate(self.canvas, self.polygon_i)

            # compare and compute the child with the parent loss
            l_parent, l_child = self.cc_loss(older_solution, newer_solution)

            # compare loss
            if l_child < l_parent:
                self.counter = 0
                # pushing the better solution
                self.canvas = newer_solution
            else:
                self.counter += 1
                # keep the old canvas
                self.canvas = older_solution

            t += 1

            if (self.counter > self.stagnation_limit) and (
                self.canvas.how_many() < self.max_polygons
            ):
                if l_child < v_k:
                    # update the canvas to the improved version
                    generations.append(deepcopy(self.canvas))
                    self.canvas = self.create_polygon(self.canvas)

                    v_k = l_child
                    self.counter = 0
                else:
                    # reinit polygon
                    #  This is attempting to perform a rollback
                    previous_generation = generations[-1]
                    # reinitializing a polygon onto the canvas
                    self.canvas = self.create_polygon(previous_generation)

                    # keep pushing the counter up
                    self.counter += 1

            if (self.counter > self.stagnation_limit) and (
                self.canvas.how_many() == self.max_polygons
            ):
                # Once we reach the maximum number of generations, now we can
                # send the rest of our cycles optimizing all polygons
                self.norm_opti_probs()
            # TODO: incorporate logging at end of loop cycle to track sim status

    def write_results(
        self,
        generations: bool = False,
    ):
        """
        Save the results of the simulation to disk
        if generations is made true, save all the saved generations up to the final result
        """
        if generations:
            pass

        # TODO: add mkfldr
        # TODO: save images to dir
        # TODO: save other simulation data to that folder
        return


def get_energy_map(source: np.ndarray, recon: np.ndarray) -> np.ndarray:
    """
    Computes the energy map.

    Args:
        source (np.ndarray): Source image as ndarray.
        recon (np.ndarray): Reconstructed image as ndarray.

    Returns:
        np.ndarray: Supplementary matrix of cumulative energy values of each
        pixel.
    """
    # Compute for total difference
    cumulative_e = np.sum(np.absolute(source - recon))

    # Compute for pixel-wise probability
    pixel_e = 0
    for channel in [0, 1, 2]:
        pixel_e += np.absolute(source[:, :, channel] - recon[:, :, channel])

    prob_matrix = pixel_e / cumulative_e

    # Supplementary matrix is the cumulative sum of probabilities
    supp_matrix = prob_matrix.cumsum().reshape(source.shape[:2])

    return supp_matrix


def vertices_em(source: np.ndarray, recon: np.ndarray, n_vertices: int = 3) -> Vertex:
    """

    Args:
        source (np.ndarray): Source image as ndarray.
        recon (np.ndarray): Reconstructed image as ndarray.
        n_vertices (int): Number of vertices. Defaults to

    Returns:
        Vertex: A set of vertices chosen based on the energy map.
    """
    matrix = get_energy_map(source, recon)
    x = []
    y = []
    for _ in range(n_vertices):
        threshold = np.random.rand()
        raw_index = np.argmax(matrix > threshold)
        print(raw_index)
        x_new = raw_index // source.shape[0]
        y_new = raw_index % source.shape[1]
        x.append(x_new)
        y.append(y_new)

    return Vertex(np.array(x), np.array(y))
