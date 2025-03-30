import main
import graph_create
import graph_entities_v4
import calculations
import graph_display
g, movie_dict = graph_create.initialize_graphs('Datasets/full_dataset.csv')
input_movie = 'The Matrix'
lower = 5.0
upper = 5.6
key = 'rating'
rec_result, sim_scores = calculations.get_recommendations(movie_dict, input_movie, limit=5, key=key, lower=lower, upper=upper)
movie_graph = graph_create.create_recommended_movie_graph(input_movie, rec_result, sim_scores)
graph_display.visualize_movie_graph(movie_graph, layout='spring_layout')
