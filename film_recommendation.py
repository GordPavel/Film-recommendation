from statistics import mean
import networkx as nx

# can load any data script with needed collections:
# movies: [str] - list of movies' titles
# users: [str] - list of users' ids
# movies_similarities: [(str,str)] - Adjacency list of movies' similarities
# users_connections: [(str,str)] - Adjacency list of users network graph
# user_movies_connections: [(str,str)] - Adjacency list of users' seen movies -
# bipartite graph of movies and users
from data1 import *

# prepare data sources for effective data access

# save users' connections as graph for fast finding friends list
users_connections_graph = nx.Graph(users_connections)
# add single users
for user in users:
    users_connections_graph.add_node(user)

# save all movies' similarities to graph to fast compute all
# transitive similarities for any movie
# (get all connected nodes for specified node)
movies_similarities_graph = nx.Graph(movies_similarities)
# add unique movies
for movie in movies:
    movies_similarities_graph.add_node(movie)

# save users' seen movies to graph to fast find specified user's seen movies
user_movies_connections_graph = nx.Graph(user_movies_connections)
# add never seen movies
for movie in movies:
    user_movies_connections_graph.add_node(movie)
# add users with no seen movies
for user in users:
    user_movies_connections_graph.add_node(user)


def film_comparator_for(user: str):
    def num_friends_have_seen_movie(movie):
        """
        Compute F - Discussability = the number of friends of user,
        who have already seen that movie
        :param movie: movie id to compute recommendation score
        :return: discussability score
        """
        return sum([
            # count if friend has seen specified movie
            1 if movie in user_movies_connections_graph.neighbors(friend) else 0
            # get user's friends
            for friend in users_connections_graph.neighbors(user)
        ])

    def mean_friends_similar_seen_movies(movie):
        """
        Compute S - Uniqueness = mean of the number of similar movies seen for
        each friend
        :param movie:  movie id to compute score
        :return: Uniqueness score
        """

        def count_user_seen_similar_movies(user_):
            """
            Counts intersection between friend's seen movies and
            similar movies for specified one
            :param user_: friend's id
            :return: friend's similar movies seen count
            """
            # get friend's seen movies
            user_seen = set(user_movies_connections_graph.neighbors(user_))
            # get connected component by movie id
            movie_similarity_component = set(nx.node_connected_component(
                movies_similarities_graph,
                movie
            ))
            # subtract specified movie itself from connected cluster
            similar_movies = movie_similarity_component - {movie}
            return len(user_seen & similar_movies)

        # Obviously if user has no friends, mean = 0
        if not users_connections_graph.neighbors(user):
            return 0

        return mean(
            count_user_seen_similar_movies(friend)
            for friend in users_connections_graph.neighbors(user)
        )

    def movie_score(movie):
        """
        Compute movie score for specified user as F/S, where

        F - Discussability = the number of friends of user,
        who have already seen that movie
        S - Uniqueness = mean of the number of similar movies seen for each
        friend

        :param movie: movie id to compute recommendation score
        :return: recommendation score
        """

        # don't recommend one movie for user twice
        if user_movies_connections_graph.has_edge(user, movie):
            return float('-inf')
        denominator = mean_friends_similar_seen_movies(movie)
        # Exclude the movies with S = 0
        # PS but if think it's mathematically and logically correct
        # to recommend unique movies for users - return float('inf')
        if denominator == 0:
            return float('-inf')
        else:
            nominator = num_friends_have_seen_movie(movie)
            return nominator / float(denominator)

    return movie_score


def film_recommendation_for(user: str):
    # get movie with maximal score
    return max(movies, key=film_comparator_for(user))


# For data1 script should print Movie 2, because score = 4.0 is maximal
# F = 2 – friends have seen this movie
# S = .5 – User1 has seen 1 similar movie Movie1 and
# User2 has seen 0 similar movies
print(film_recommendation_for('User 3'))
