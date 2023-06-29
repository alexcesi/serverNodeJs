import requests
import json
from collections import defaultdict


def recup_donnees(type):
    url = "http://82.64.231.72:8000/" + type

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

    return data


def trouver_recette(recipeList, idArticle):
    rootArticle = next(
        (article for article in recipeList if article["id_article"] == idArticle), None)

    if rootArticle:
        recette_temp = [
            rootArticle.get('id_article'),
            rootArticle.get('id_operation'),
            rootArticle.get('id_composant1'),
            rootArticle.get('quantite1'),
            rootArticle.get('id_composant2'),
            rootArticle.get('quantite2')
        ]
        recette = [recette_temp]

        if rootArticle.get("id_composant1"):
            sous_arbre_gauche = trouver_recette(
                recipeList, rootArticle["id_composant1"])
            if sous_arbre_gauche:
                recette += sous_arbre_gauche
            else:
                recette.append([
                    rootArticle["id_composant1"],
                    rootArticle["quantite1"]
                ])

        if rootArticle.get("id_composant2"):
            sous_arbre_droit = trouver_recette(
                recipeList, rootArticle["id_composant2"])
            if sous_arbre_droit:
                recette += sous_arbre_droit
            else:
                recette.append([
                    rootArticle["id_composant2"],
                    rootArticle["quantite2"]
                ])

        return recette
    else:
        return None


with open('recipes.json') as f:
    recipeList = json.load(f)

racine = 40
arbre = trouver_recette(recipeList, racine)

result_dict = defaultdict(list)

for list_ in arbre:
    key = list_[0]
    if result_dict[key]:
        if len(list_) > 3 and list_[3] is not None:
            result_dict[key][3] += list_[3]
        if len(list_) > 5 and list_[5] is not None:
            result_dict[key][5] += list_[5]
    else:
        result_dict[key] = list(list_)

list_of_lists = list(result_dict.values())
print(list_of_lists)
