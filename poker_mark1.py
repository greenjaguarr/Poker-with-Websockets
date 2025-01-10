# Kaart Class
class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur:str, waarde:str):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K","V","B", "T","9",...,"2"
        """
        self.kleur = kleur
        self.waarde = waarde

    def __str__(self):
        # lmao waarom niet
        return f"{self.waarde}{self.SUIT_SYMBOLS[self.kleur]}"






def calc_waarde(hand: list[Kaart]) -> dict:
    from collections import Counter

    def Is_straight(values):
        value_str = ''.join(values)
        # check if any 5 out of seven match
        for i in range(0,7):
            for j in range(i+1,7):
                temp = value_str[:i] + value_str[i+1:j] + value_str[j+1:]
                if temp in 'A23456789TBVK' or temp in '23456789TBVKA':
                    return True, value_str
        return False, None

    def is_flush(suits):
        # return len(set(suits)) == 1
        if Counter(suits).most_common(1)[0][1] >= 5:
            # flush detected.
            flush_suit = Counter(suits).most_common(1)[0][0]
            highest_flush = max([kaart.waarde for kaart in hand if kaart.kleur == flush_suit], key=lambda x: '23456789TBVKA'.index(x))
            return True, flush_suit, highest_flush
        else: return False,None, None

    values = sorted([kaart.waarde for kaart in hand], key=lambda x: '23456789TBVKA'.index(x))
    suits = [kaart.kleur for kaart in hand]

    is_flush,suit, highest_flush = is_flush(suits)
    is_straight,value_str = Is_straight(values)

    if is_straight and is_flush:
        # assert that all cards of the straight are of the same suit
        straight_flush_cards = [kaart for kaart in hand if kaart.waarde in value_str and kaart.kleur == suit]
        straight_flush_cards = sorted(straight_flush_cards, key=lambda x: '23456789TBVKA'.index(x.waarde))
        straight_flush_cards = straight_flush_cards[-5:]
        # print("[DEBUG]", [str(kaart) for kaart in straight_flush_cards], "straight_flush_cards")
        temp = "".join(sorted([kaart.waarde for kaart in straight_flush_cards], key=lambda x: '23456789TBVKA'.index(x)))
        # print("[DEBUG]", temp, "temp")
        if not temp in 'A23456789TBVK' and not temp in '23456789TBVKA':
            pass # not a stragit flush
        if temp in 'TBVKA':
            return {"resultaat": "royal flush", "hoogste kaart": "A"}
        hoogste_kaart = max([kaart.waarde for kaart in straight_flush_cards], key=lambda x: '23456789TBVKA'.index(x))
        return {"resultaat": "straight flush", "hoogste kaart": hoogste_kaart}
    
    value_counts = Counter(values)
    most_common = value_counts.most_common()
    # print(values, most_common, "values, most_common")

    if most_common[0][1] == 4:
        return {"resultaat": "four of a kind", "hoogste kaart": most_common[0][0]}
    elif most_common[0][1] == 3 and most_common[1][1] >= 2:
        highest_value = max([kaart.waarde for kaart in hand if kaart.waarde == most_common[0][0] or kaart.waarde == most_common[1][0]], key=lambda x: '23456789TBVKA'.index(x))
        return {"resultaat": "full house", "hoogste kaart": highest_value}
    elif is_flush:
        # hoogste_kaart = values[-1] # wrong, only works if the flush is the highest card
        hoogste_kaart = highest_flush
        if "A" in ''.join(values):
            hoogste_kaart = "A"        
        return {"resultaat": "flush", "hoogste kaart": hoogste_kaart}
    elif is_straight:
        hoogste_kaart = values[-1]
        if "AKVBT" in ''.join(values):
            hoogste_kaart = "A"
        return {"resultaat": "straight", "hoogste kaart": hoogste_kaart}
    elif most_common[0][1] == 3:
        return {"resultaat": "three of a kind", "hoogste kaart": most_common[0][0]}
    elif most_common[0][1] == 2 and most_common[1][1] == 2:
        highest_value = max([kaart.waarde for kaart in hand if kaart.waarde == most_common[0][0] or kaart.waarde == most_common[1][0]], key=lambda x: '23456789TBVKA'.index(x))
        return {"resultaat": "two pair", "hoogste kaart": highest_value}
    elif most_common[0][1] == 2:
        return {"resultaat": "one pair", "hoogste kaart": most_common[0][0]}
    else:
        return {"resultaat": "high card", "hoogste kaart": values[-1]}


def compare(hand1: list[Kaart], hand2: list[Kaart]) -> str:
    map_resultaat_volgorde = {
        "high card": 1,
        "one pair": 2,
        "two pair": 3,
        "three of a kind": 4,
        "straight": 5,
        "flush": 6,
        "full house": 7,
        "four of a kind": 8,
        "straight flush": 9,
        "royal flush": 10
    }
    hand1_sanitised = [kaart for kaart in hand1 if kaart]
    hand2_sanitised = [kaart for kaart in hand2 if kaart]

    waarde1 = calc_waarde(hand1_sanitised)
    waarde2 = calc_waarde(hand2_sanitised)

    if map_resultaat_volgorde[waarde1['resultaat']] > map_resultaat_volgorde[waarde2['resultaat']]:
        return "1"
    elif map_resultaat_volgorde[waarde1['resultaat']] < map_resultaat_volgorde[waarde2['resultaat']]:
        return "2"
    else:
        # If the hand types are the same, compare the highest cards
        ranking_order = '23456789TBVKA'
        if ranking_order.index(waarde1['hoogste kaart']) > ranking_order.index(waarde2['hoogste kaart']):
            return "1"
        elif ranking_order.index(waarde1['hoogste kaart']) < ranking_order.index(waarde2['hoogste kaart']):
            return "2"
        else:
            return "0"


    

hand1  = [Kaart("harten", 'A'),  Kaart("harten", 'B'),  Kaart("harten", 'T'), Kaart("harten", '9'), Kaart("schoppen", '4'), Kaart("klaveren", '4'), Kaart("ruiten", '4')]
hand2  = [Kaart("harten", 'K'),  Kaart("schoppen", 'B'),Kaart("schoppen", 'T'), Kaart("harten", '6'), Kaart("schoppen", '3'), Kaart("klaveren", '3'), Kaart("ruiten", '3')]
hand3  = [Kaart("harten", '2'),  Kaart("klaveren", 'V'),Kaart("harten", 'T'), Kaart("harten", '9'), Kaart("schoppen", '4'), Kaart("klaveren", '4'), Kaart("ruiten", '4')]
hand4  = [Kaart("harten", 'A'),  Kaart("harten", 'K'),  Kaart("harten", 'V'), Kaart("harten", 'B'), Kaart("harten", 'T'), Kaart("harten", '9'), Kaart("harten", '8')]
hand5  = [Kaart("harten", '2'),  Kaart("harten", '3'),  Kaart("harten", '4'), Kaart("harten", '5'), Kaart("harten", '6'), Kaart("schoppen", '7'), Kaart("klaveren", '8')]  # straight en een flush maar niet met dezelfde kaarten
hand6  = [Kaart("schoppen", 'A'),Kaart("schoppen", 'K'),Kaart("schoppen", 'V'), Kaart("schoppen", 'B'), Kaart("schoppen", 'T'), Kaart("harten", '9'), Kaart("ruiten", '8')]
hand7  = [Kaart("klaveren", '9'),Kaart("ruiten", '9'),  Kaart("schoppen", '9'), Kaart("harten", '9'), Kaart("harten", '2'), Kaart("harten", '3'), Kaart("harten", '4')]
hand8  = [Kaart("klaveren", '5'),Kaart("ruiten", '5'),  Kaart("schoppen", '5'), Kaart("harten", '5'), Kaart("harten", 'K'), Kaart("schoppen", 'K'), Kaart("klaveren", 'K')]
hand9  = [Kaart("harten", '7'),  Kaart("harten", '8'),  Kaart("harten", '9'), Kaart("harten", 'T'), Kaart("harten", 'B'), Kaart("harten", 'V'), Kaart("harten", 'K')]
hand10 = [Kaart("klaveren", '3'),Kaart("klaveren", '4'),Kaart("klaveren", '5'), Kaart("klaveren", '6'), Kaart("klaveren", '7'), Kaart("harten", '8'), Kaart("harten", '9')]
hand11 = [Kaart("harten", '2'),  Kaart("klaveren", '3'),Kaart("schoppen", '4'), Kaart("ruiten", '5'), Kaart("harten", '6'), Kaart("schoppen", '7'), Kaart("klaveren", '8')]  # straight
hand12 = [Kaart("harten", '2'),  Kaart("harten", '4'),  Kaart("harten", '6'), Kaart("harten", '8'), Kaart("harten", 'T'), Kaart("harten", 'V'), Kaart("harten", 'K')]  # flush
hand13 = [Kaart("harten", '2'),  Kaart("harten", '2'),  Kaart("klaveren", '2'), Kaart("schoppen", '3'), Kaart("schoppen", '3'), Kaart("ruiten", '3'), Kaart("klaveren", '4')]  # full house
hand14 = [Kaart("harten", '2'),  Kaart("klaveren", '2'),Kaart("schoppen", '2'), Kaart("ruiten", '2'), Kaart("harten", '3'), Kaart("schoppen", '4'), Kaart("klaveren", '5')]  # four of a kind
hand15 = [Kaart("harten", '2'),  Kaart("klaveren", '2'),Kaart("schoppen", '2'), Kaart("ruiten", '3'), Kaart("harten", '5'), Kaart("schoppen", '7'), Kaart("klaveren", '9')]  # three of a kind
hand16 = [Kaart("harten", '2'),  Kaart("klaveren", '2'),Kaart("schoppen", '3'), Kaart("ruiten", '3'), Kaart("harten", '5'), Kaart("schoppen", '7'), Kaart("klaveren", '9')]  # two pair
hand17 = [Kaart("harten", '2'),  Kaart("klaveren", '2'),Kaart("schoppen", '3'), Kaart("ruiten", '4'), Kaart("harten", '5'), Kaart("schoppen", '7'), Kaart("klaveren", '9')]  # one pair
hand18 = [Kaart("harten", '2'),  Kaart("klaveren", '3'),Kaart("schoppen", '5'), Kaart("ruiten", '7'), Kaart("harten", '9'), Kaart("schoppen", 'B'), Kaart("klaveren", 'V')]  # high card



if __name__ == "__main__":
    # # game_logic = PokerGameLogic()
    # print("1", game_logic.compare(hand1, hand2))  # 1
    # print("2", game_logic.compare(hand1, hand3))  # 0
    # print("3", game_logic.compare(hand2, hand3))  # 2
    # print("4", game_logic.compare(hand1, hand1))  # 0
    # print("5", game_logic.compare(hand1, hand4))  # 2
    # print("6", game_logic.compare(hand5, hand6))  # 2
    # print("7", game_logic.compare(hand7, hand8))  # 1
    # print("8", game_logic.compare(hand9, hand10))  # 1
    # print("9", game_logic.compare(hand11, hand12))  # 2
    # print("10", game_logic.compare(hand13, hand14))  # 2
    # print("11", game_logic.compare(hand15, hand16))  # 1 # three of a kind beats two pair
    # print("12", game_logic.compare(hand17, hand18))  # 1
    # print("13", game_logic.compare(hand4, hand6))  # 0
    # print("14", game_logic.compare(hand5, hand9))  # 2
    # print("15", game_logic.compare(hand10, hand11))  # 1
    # print("16", game_logic.compare(hand12, hand13))  # 2
    # print("1", game_logic.calc_waarde(hand1))  # {'resultaat': 'three of a kind', 'hoogste kaart': '4'}
    # print("2", game_logic.calc_waarde(hand2))  # {'resultaat': 'three of a kind', 'hoogste kaart': '3'}
    # print("3", game_logic.calc_waarde(hand3))  # {'resultaat': 'three of a kind', 'hoogste kaart': '4'}
    # print("4", game_logic.calc_waarde(hand4))  # {'resultaat': 'royal flush', 'hoogste kaart': 'A'}
    # print("5", game_logic.calc_waarde(hand5))  # {'resultaat': 'straight flush', 'hoogste kaart': '6'}
    # print("6", game_logic.calc_waarde(hand6))  # {'resultaat': 'royal flush', 'hoogste kaart': 'A'}
    # print("7", game_logic.calc_waarde(hand7))  # {'resultaat': 'four of a kind', 'hoogste kaart': '9'}
    # print("8", game_logic.calc_waarde(hand8))  # {'resultaat': 'four of a kind', 'hoogste kaart': '5'}
    # print("9", game_logic.calc_waarde(hand9))  # {'resultaat': 'straight flush', 'hoogste kaart': 'K'}
    # print("10", game_logic.calc_waarde(hand10))  # {'resultaat': 'straight flush', 'hoogste kaart': '7'}
    # print("11", game_logic.calc_waarde(hand11))  # {'resultaat': 'straight', 'hoogste kaart': '8'}
    # print("12", game_logic.calc_waarde(hand12))  # {'resultaat': 'flush', 'hoogste kaart': 'K'}
    # print("13", game_logic.calc_waarde(hand13))  # {'resultaat': 'full house', 'hoogste kaart': '3'}
    # print("14", game_logic.calc_waarde(hand14))  # {'resultaat': 'four of a kind', 'hoogste kaart': '2'}
    # print("15", game_logic.calc_waarde(hand15))  # {'resultaat': 'three of a kind', 'hoogste kaart': '2'}
    # print("16", game_logic.calc_waarde(hand16))  # {'resultaat': 'two pair', 'hoogste kaart': '3'}
    # print("17", game_logic.calc_waarde(hand17))  # {'resultaat': 'one pair', 'hoogste kaart': '2'}
    # print("18", game_logic.calc_waarde(hand18))  # {'resultaat': 'high card', 'hoogste kaart': 'V'}
    pass