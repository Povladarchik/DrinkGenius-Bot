import os
import sqlite3
import Levenshtein
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

load_dotenv()


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def select_query(self, query, params=None, fetch_all=True):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)

            result = cursor.fetchall() if fetch_all else cursor.fetchone()

        return [row[0] for row in result] if fetch_all else result[0]


class Cocktail:
    DB_PATH = os.getenv('DATABASE_PATH')
    TABLE = 'Cocktails'

    def __init__(self, name):
        self.name = self._find_closest_match(name)

    @staticmethod
    def _find_closest_match(input_str):
        all_names_query = f"SELECT name FROM {Cocktail.TABLE}"
        all_names = DatabaseManager(Cocktail.DB_PATH).select_query(all_names_query, fetch_all=True)
        best_match = max(all_names, key=lambda x: Levenshtein.ratio(input_str.lower(), x.lower()))
        return best_match

    def _get_cocktail_info(self, column):
        query = f"SELECT {column} FROM {Cocktail.TABLE} WHERE name = ?"
        return DatabaseManager(Cocktail.DB_PATH).select_query(query, (self.name,), fetch_all=False)

    def _get_cocktail_name_by_index(self, index):
        query = f"SELECT name FROM {Cocktail.TABLE} LIMIT 1 OFFSET ?"
        return DatabaseManager(Cocktail.DB_PATH).select_query(query, (index,), fetch_all=False)

    def get_recipe(self):
        return self._get_cocktail_info('recipe')

    def get_ingredients(self):
        return self._get_cocktail_info('ingredients')

    def get_image(self):
        return self._get_cocktail_info('image')

    def get_degree(self):
        return self._get_cocktail_info('degree')

    def get_taste(self):
        return self._get_cocktail_info('taste')

    def get_base(self):
        return self._get_cocktail_info('base')

    def get_category(self):
        return self._get_cocktail_info('category')

    def recommend_similar_cocktails(self):
        all_recipes_query = f"SELECT recipe FROM {Cocktail.TABLE}"
        all_recipes = DatabaseManager(Cocktail.DB_PATH).select_query(all_recipes_query, fetch_all=True)
        single_recipe = self._get_cocktail_info('recipe')

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(all_recipes)
        query_vec = vectorizer.transform([single_recipe])

        similarity_matrix = cosine_similarity(query_vec, X)
        similar_indices = list(map(int, similarity_matrix[-1].argsort()[:-4:-1]))
        similar_cocktails = [self._get_cocktail_name_by_index(index) for index in similar_indices]
        return similar_cocktails