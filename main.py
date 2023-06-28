import json
import sys

import requests
    
urlArticle = requests.get('http://82.64.231.72:8000/articles')
articles = json.loads(urlArticle.text)

urlOperation = requests.get('http://82.64.231.72:8000/operations')
operations = json.loads(urlOperation.text)

urlRecipe = requests.get('http://82.64.231.72:8000/recipes')
recettes = json.loads(urlRecipe.text)

def trouver_recette(article_id, liste_recette=None):
    if liste_recette is None:
        liste_recette = []

    recette = None
    for r in recettes:
        if r['id_article'] == article_id:
            recette = r
            break
    if recette:
        recette_temp = {'id_article': recette.get('id_article'),
                        'id_operation': recette.get('id_operation'),
                        'id_composant1': recette.get('id_composant1'),
                        'quantite1': recette.get('quantite1'),
                        'id_composant2': recette.get('id_composant2'),
                        'quantite2': recette.get('quantite2')}
        liste_recette.append(recette_temp)

        if recette.get('id_composant1'):
            trouver_recette(recette.get('id_composant1'), liste_recette)

        if recette.get('id_composant2'):
            trouver_recette(recette.get('id_composant2'), liste_recette)
        
    return liste_recette

def transformer_recettes(liste_recette):
    nouvelle_liste = []
    
    while liste_recette:
        recette = liste_recette.pop(0)

        for r in nouvelle_liste:
            if r['id_article'] == recette['id_article'] and r['id_operation'] == recette['id_operation']:
                r['quantite1'] += recette['quantite1']
                if recette['id_composant2'] is not None:
                    if r['id_composant2'] == recette['id_composant2']:
                        r['quantite2'] += recette['quantite2']
                break
        else:
            nouvelle_liste.append(recette)
    
    nouvelle_liste.reverse()
    
    return nouvelle_liste

def calculer_temps_production(nouvelle_liste, operations, nombre_workunits, articles_primaires):
    nombre_workunits = 26
    workunits_fin = [0] * nombre_workunits
    articles_en_production = []
    articles_disponibles = {article: float('inf') for article in articles_primaires}

    while nouvelle_liste:
        workunit_disponible = workunits_fin.index(min(workunits_fin))

        for recette in nouvelle_liste:
            if (recette['id_composant1'] in articles_disponibles and
                (recette['id_composant2'] is None or recette['id_composant2'] in articles_disponibles)):
                articles_disponibles[recette['id_composant1']] -= recette['quantite1']
                if recette['id_composant2'] is not None:
                    articles_disponibles[recette['id_composant2']] -= recette['quantite2']

                for operation in operations:
                    if operation['id'] == recette['id_operation']:
                        temps_operation = operation['delaiInstallation'] + recette['quantite1'] * operation['delai']
                        if recette['id_composant2'] is not None:
                            temps_operation += recette['quantite2'] * operation['delai']
                        break

                if workunits_fin[workunit_disponible] < temps_operation:
                    workunits_fin[workunit_disponible] = temps_operation
                else:
                    workunits_fin[workunit_disponible] += temps_operation

                articles_en_production.append(recette['id_article'])

                if recette['id_article'] in articles_disponibles:
                    articles_disponibles[recette['id_article']] += 1
                else:
                    articles_disponibles[recette['id_article']] = 1

                nouvelle_liste.remove(recette)
                break
        else:
            break

    total_temps = max(workunits_fin)

    return total_temps


idArticle = int(sys.argv[1])
quantity = int(sys.argv[2])

recette = trouver_recette(idArticle)

nouvelle_recette = transformer_recettes(recette)
test_delai = calculer_temps_production(nouvelle_recette, operations, 26, [
                                       article['id'] for article in articles])

print(test_delai)
