from src.arg_parse import args
from src.simulation import Simulation
from src.custom_types import Canvas, Polygon
import matplotlib.pyplot as mpl

if __name__ == "__main__":
    sim = Simulation(
        b_image=args.base_image,
        o_image=args.output_image,
        m_poly=args.max_polygons,
        stag_lim=args.stagnation_limit,
        num_evals=args.max_evaluations,
    )
    # run simulation
    sim.run()

    # TODO: automate making an output folder with all simulation information such as args, photos, logs
    # write results
    sim.write_results()
