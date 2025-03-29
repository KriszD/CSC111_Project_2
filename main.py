"""HAM and Bacon - CSC111 Project 2.

Instructions: run the main method in order to use the menu. Read the project report for more information on running.

This project was created by Skye Mah-Madjar, Krisztian Drimba, Joshua Iaboni, and Xiayu Lyu."""
import python_ta
import graph_create
import graph_display
import calculations


if __name__ == '__main__':
    # python_ta.check_all(config={
    #     'extra-imports': ['graph_entities', 'graph_create', 'graph_display'],  # the names (strs) of imported modules
    #     'allowed-io': ['print_bacon_path', 'ranking'],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    actor_graph, movie_dict = graph_create.initialize_graphs('Datasets/full_dataset.csv')
    average_bacon_numbers = graph_create.create_dict_from_csv('Datasets/average_bacon_numbers.csv')
    average_bacon_numbers_no_zeroes = {actor: score for actor, score in average_bacon_numbers.items() if score != 0}

    # the meaningful numbers based on OUR dataset.
    average_bacon_numbers_meaningful = {actor: score for actor, score in average_bacon_numbers.items() if score > 1.5}

    running = True
    menu = ['(1) Bacon Number Ranking', '(2) Average Bacon Number of an actor',
            '(3) Bacon Number/Path between two actors', '(4) Movie Recommendations for a movie', '(5) Exit']

    while running:
        print('======================================================================================')
        print('Your options are: ', menu)
        choice = input("Your choice: ").strip()

        while choice not in ['1', '2', '3', '4', '5']:
            print("Invalid Choice, try Again.")
            choice = input("Your choice: ").strip()

        if choice == '1':
            actor_limit = int(input("Number of actors: "))
            calculations.ranking(average_bacon_numbers, actor_limit)

        if choice == '2':
            actor_name = str(input("Actor Name: ")).strip()
            print("The Average Bacon Number for", actor_name, "is:", calculations.average_bacon_number(actor_graph,
                                                                                                       actor_name))
            print("The actor is number", list(average_bacon_numbers_no_zeroes.keys()).index(actor_name) + 1, "out of",
                  len(average_bacon_numbers_no_zeroes), "in the overall rankings.")

        if choice == '3':
            actor1_name = str(input("Actor 1 Name: ")).strip()
            actor2_name = str(input("Actor 2 Name: ")).strip()
            filter_key = str(input("Optional Filters: release date, rating. Type NO if you do not"
                                   " want it to be filtered. ")).strip()

            if filter_key != 'NO':
                lower_threshold = float(input("Lower bound for filtering: "))
                upper_threshold = float(input("Upper bound for filtering: "))
                num = calculations.bacon_number(actor_graph, actor1_name, actor2_name, movie_dict, filter_key,
                                                lower_threshold, upper_threshold)
                if num < 0:
                    print("These actors share no path.")
                else:
                    print("The Bacon Number between", actor1_name, "and", actor2_name, "is:", num)
                    print("A path between them is: ")
                    calculations.print_bacon_path(actor_graph, actor1_name, actor2_name, movie_dict, filter_key,
                                                  lower_threshold, upper_threshold)
                actor_path, _ = calculations.bacon_path(actor_graph, actor1_name, actor2_name, movie_dict, filter_key,
                                                        lower_threshold, upper_threshold)

            else:
                num = calculations.bacon_number(actor_graph, actor1_name, actor2_name, movie_dict)
                if num < 0:
                    print("These actors share no path.")
                else:
                    print("The Bacon Number between", actor1_name, "and", actor2_name, "is:", num)
                    print("A path between them is: ")
                    calculations.print_bacon_path(actor_graph, actor1_name, actor2_name, movie_dict)
                actor_path, _ = calculations.bacon_path(actor_graph, actor1_name, actor2_name)

            graph_display.visualize_actor_path(actor_graph, actor_path, (actor1_name, actor2_name))

        if choice == '4':
            movie_name = str(input("Movie Name: ")).strip()
            movie_limit = int(input("Number of Recommendations: "))
            filter_key = str(input("Optional Filters: release date, rating. Type NO if you do not"
                                   " want it to be filtered. ")).strip()

            if filter_key != 'NO':
                lower_threshold = float(input("Lower bound for filtering: "))
                upper_threshold = float(input("Upper bound for filtering: "))
                print("Recommended Movies: ",
                      calculations.get_recommendations(movie_dict, movie_name, movie_limit, filter_key,
                                                       lower_threshold, upper_threshold)[0])

            else:
                print("Recommended Movies: ", calculations.get_recommendations(movie_dict, movie_name, movie_limit)[0])

        if choice == '5':
            print("Bye! We hope you enjoyed our project! :)")
            running = False
