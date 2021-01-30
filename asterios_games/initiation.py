from asterios.level import BaseLevel


class Level1(BaseLevel):
    """
    Redonne moi se que je te donne.
    """

    def generate_puzzle(self):
        return 'initiation'

    def check_answer(self, answer):
        if 'initiation' == answer:
            return (True, 'Trés bien')

        return (False, "Non je t'ai envoyer le text `initiation`")


class Level2(BaseLevel):
    """
    Redonne moi le text mais en majuscule. 

    Pour savoir comment faire, va dans un terminal python et saisi:

    >>> help(str.upper)
    """

    def generate_puzzle(self):
        return 'initiation'

    def check_answer(self, answer):
        if 'INITIATION' == answer:
            return (True, 'Trés bien')

        return (False, "Renvoie moi le retour de `.upped()` sur le text envoyé")


class Level3(BaseLevel):
    """
    Redonne moi le text mais en minuscule. 

    Pour savoir comment faire, va dans un terminal python et saisi:

    >>> help(str.lower)
    """

    def generate_puzzle(self):
        return 'INITIATION'

    def check_answer(self, answer):
        if 'initiation' == answer:
            return (True, 'Trés bien')

        return (False, "Renvoie moi le retour de `.lower()` sur le text envoyé")



class Level4(BaseLevel):
    """
    Je vais te donner un mot, dis moi s'il est en majuscule

    Je te laisse chercher la réponse dans:
    >>> help(str)
    """

    def generate_puzzle(self):
        return 'initiation'

    def check_answer(self, answer):
        if answer is False:
            return (True, 'Trés bien')

        return (False, "Renvoie moi le retour de `.isupper()` sur le text envoyé")


class Level5(BaseLevel):
    """
    Je vais te donner une liste de mot, pour chaque mot dis moi s'il est
    en majuscule en me renvoyant une list de boolean

    Pour d'aider, voici un morceau de code qui parcour une liste pour en remplire 
    une autre.

        nouvelle_list = []
        for element in une_liste:
             nouvelle_list.append(element)

    C'est équivalent à:

        nouvelle_list = [element for element in une_liste]
    """

    def generate_puzzle(self):
        return ['perdrix', 'OIE', 'CANARD', 'poule', 'dindon', 'PAON']

    def check_answer(self, answer):
        expected = [False, True, True, False, False, True]
        if answer == expected:
            return (True, 'Trés bien')

        return (False, "Renvoie moi une liste")


class Level6(BaseLevel):
    """
    Je vais te donner une liste de mot, dis moi si tous les mot sont en majuscule

    Astuce:

    >>> help(all)
    """

    def generate_puzzle(self):
        return ['PERDRIX', 'OIE', 'CANARD', 'poule', 'DINDON', 'PAON']

    def check_answer(self, answer):
        if answer is False:
            return (True, 'Trés bien')

        return (False, "Renvoie moi True ou False")





