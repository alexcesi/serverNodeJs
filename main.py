# -*- coding: utf-8 -*-
import json
import sys
import requests


def recup_operationbyworkunit():
    base_url = "http://82.64.231.72:8000/operations_by_workunit/"
    ids = range(1, 27)
    data_list = []

    for id in ids:
        url = base_url + str(id)
        response = requests.get(url)
        data = response.json()
        data_list.append(data)

    for index, sublist in enumerate(data_list, start=1):
        sublist.append({'id': index})
    return data_list


def recup_donnees(type):
    url = "http://82.64.231.72:8000/" + type

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

    return data

articles_primaire = []


def trouver_recette(idArticle, liste_recette=None):

    if liste_recette is None:
        liste_recette = []

    recette = None

    for r in recettes:
        if r['id_article'] == idArticle:
            recette = r
            break

    if recette:
        recette_temp = {'id_article': recette.get('id_article'),
                        'id_operation': recette.get('id_operation'),
                        'id_composant1': recette.get('id_composant1'),
                        'quantite1': recette.get('quantite1'),
                        'id_composant2': recette.get('id_composant2'),
                        'quantite2': recette.get('quantite2')
                        }
        liste_recette.append(recette_temp)

        if recette.get('id_composant1'):
            trouver_recette(recette.get('id_composant1'), liste_recette)

        if recette.get('id_composant2'):
            trouver_recette(recette.get('id_composant2'), liste_recette)

    else:
        if recette is None:
            global articles_primaire
            articles_primaire.append(idArticle)
            
    return liste_recette


def multi_quantite(liste_recettes, quantity):
    for recette in liste_recettes:
        if recette.get('quantite1') is not None:
            recette['quantite1'] *= quantity
        if recette.get('quantite2') is not None:
            recette['quantite2'] *= quantity
    return liste_recettes


def transformer_recettes(liste_recette):
    nouvelle_liste = []

    while liste_recette:

        recette = liste_recette.pop(0)

        for index, r in enumerate(nouvelle_liste):
            if r['id_article'] == recette['id_article'] and r['id_operation'] == recette['id_operation']:
                r['quantite1'] += recette['quantite1']
                if recette['id_composant2'] is not None:
                    if r['id_composant2'] == recette['id_composant2']:
                        r['quantite2'] += recette['quantite2']
                nouvelle_liste.insert(0, nouvelle_liste.pop(index))
                break
        else:
            nouvelle_liste.insert(0, recette)

    return nouvelle_liste


def calculer_temps_production(nouvelle_liste, operations, nombre_workunits, articles_primaires):

    workunits_fin = [0] * nombre_workunits

    articles_en_production = []

    articles_disponibles = {article: float(
        'inf') for article in articles_primaires}

    while nouvelle_liste:
        workunit_disponible = workunits_fin.index(min(workunits_fin))

        for recette in nouvelle_liste:
            if (recette['id_composant1'] in articles_disponibles and
                    (recette['id_composant2'] is None or recette['id_composant2'] in articles_disponibles)):
                articles_disponibles[recette['id_composant1']
                                     ] -= recette['quantite1']
                if recette['id_composant2'] is not None:
                    articles_disponibles[recette['id_composant2']
                                         ] -= recette['quantite2']

                for operation in operations:
                    if operation['id'] == recette['id_operation']:
                        temps_operation = operation['delaiInstallation'] + \
                            recette['quantite1'] * operation['delai']
                        if recette['id_composant2'] is not None:
                            temps_operation += recette['quantite2'] * \
                                operation['delai']
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


def print_article(delai):
    print(delai)


articles = recup_donnees("articles")
operations = recup_donnees("operations")
recettes = recup_donnees("recipes")
workunitsbyoperations = recup_operationbyworkunit()

recette = trouver_recette(idArticle)

recette_quantite = multi_quantite(recette, quantity)

nouvelle_recette = transformer_recettes(recette_quantite)

delai = calculer_temps_production(
    nouvelle_recette, operations, 26, articles_primaire)

print_article(delai)
