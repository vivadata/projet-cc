"""
Traite les données brutes pour obtenir le Top 5 des événements les plus coûteux.
"""
data_sinistres_cyclone = [
    {'Date': '01/02/2025', 'Évènement': 'Cyclone Garance', 'Coût estimé': '380 M€ (Assurances)', 'Sources': 'France Assureurs, LINFO.re, CCR'},
    {'Date': '01/01/2024', 'Évènement': 'Cyclone Belal', 'Coût estimé': '100 M€ (Assurances)', 'Sources': 'France Assureurs, News Assurances Pro'},
    {'Date': '01/02/2022', 'Évènement': 'Cyclone Batsirai', 'Coût estimé': '47 M€ (Pertes agricoles)', 'Sources': 'Chambre d\'Agriculture, Imaz Press, Wikipedia'},
    {'Date': '01/04/2018', 'Évènement': 'Tempête Fakir', 'Coût estimé': '> 15 M€ (Dégâts matériels et réseaux)', 'Sources': 'Imaz Press, LINFO.re'},
    {'Date': '01/01/2018', 'Évènement': 'Tempête Berguitta', 'Coût estimé': '16,7 M€ (Pertes agricoles)', 'Sources': 'Chambre d\'Agriculture, LINFO.re'},
    {'Date': '01/01/2014', 'Évènement': 'Cyclone Bejisa', 'Coût estimé': '62 M€ (Dégâts globaux estimés)', 'Sources': 'Imaz Press, LINFO.re'},
    {'Date': '01/10/2011', 'Évènement': 'Incendie du Maïdo', 'Coût estimé': '~25 M€ (Total)', 'Sources': 'LINFO.re, ONF'},
    {'Date': '01/02/2007', 'Évènement': 'Cyclone Gamède', 'Coût estimé': '220 M€ (Assurances)', 'Sources': 'Coin de l\'Assurance, CCR'},
    {'Date': '2005-2006', 'Évènement': 'Épidémie Chikungunya', 'Coût estimé': '> 155 M€ (Coûts médicaux directs)', 'Sources': 'Lexpress.mu, Sénat, Insee'},
    {'Date': '01/01/2002', 'Évènement': 'Cyclone Dina', 'Coût estimé': '169 M€ (Assurances)', 'Sources': 'Forum Météo Réunion, Cyclonextreme'},
    {'Date': '01/01/1989', 'Évènement': 'Cyclone Firinga', 'Coût estimé': '198 M€ (Dégâts matériels)', 'Sources': 'Sénat, Forum Météo Réunion'},
    {'Date': '01/01/1980', 'Évènement': 'Cyclone Hyacinthe', 'Coût estimé': '330 M€ (Réévalué avec inflation)', 'Sources': 'Cycloneoi, Météo France, MeteoI.re'},
    {'Date': '01/02/1962', 'Évènement': 'Cyclone Jenny', 'Coût estimé': '83 M€ (Réévalué valeur 2018)', 'Sources': 'Wikipedia, CCR (Caisse Centrale de Réassurance)'}
]


def get_mois_labels_short():
    return {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
    
def get_mois_labels():
    return {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
        7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

def get_couleurs_zones():
    return {
        'AV_H': '#009E73', 
        'SV_H': '#0072B2',
        'AV_C': '#D55E00',
        'SV_C': '#F0E442'
    }

def get_coordonnees_reunion():
    # Coordonnées centrales de La Réunion, approximativement
    latitude = -21.114533
    longitude = 55.532062
    return [latitude, longitude]