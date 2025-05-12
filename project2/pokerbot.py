
import random
import time
from itertools import combinations
from collections import Counter

deck = list(range(1, 54))

# convert to card meanings
def card_to_rank_suit(card_id):
    suit = (card_id - 1) // 13  # 0-3 → spades, clubs, hearts, diamonds
    rank = (card_id - 1) % 13 + 2  # 2-14 (A = 14)
    return (rank, suit)

def best_hand(cards):
    # make all 5 card combinations that you can
    five_card_combos = combinations(cards, 5)
    # return the best hand you can make
    return max([evaluate_hand(combo) for combo in five_card_combos])

def evaluate_hand(combo):
    ranks = [card_to_rank_suit(c)[0] for c in combo]
    suits = [card_to_rank_suit(c)[1] for c in combo]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    counts = sorted(rank_counts.values(), reverse=True)
    # five of the same suit
    is_flush = max(suit_counts.values()) == 5
    # sequential order
    is_straight, high_card = check_straight(ranks)

    if is_flush and is_straight:
        # royal and straight flush
        return (8, high_card) # royal if high card is 14/ace
    elif counts[0] == 4:
        # 4 of a kind
        four = get_key(rank_counts, 4)
        kicker = max(r for r in ranks if r != four)
        return (7, four, kicker)
    elif counts[0] == 3 and counts[1] == 2:
        # full house
        three = get_key(rank_counts, 3)
        pair = get_key(rank_counts, 2)
        return (6, three, pair)
    elif is_flush:
        # flush
        return (5, *sorted(ranks, reverse=True))
    elif is_straight:
        # straight
        return (4, high_card)
    elif counts[0] == 3:
        # three of a kind
        three = get_key(rank_counts, 3)
        kickers = sorted([r for r in ranks if r != three], reverse=True)
        return (3, three, *kickers)
    elif counts.count(2) == 2:
        # two pair
        pairs = sorted([r for r in rank_counts if rank_counts[r] == 2], reverse=True)
        kicker = max(r for r in ranks if r not in pairs)
        return (2, *pairs, kicker)
    elif counts[0] == 2:
        # one pair
        pair = get_key(rank_counts, 2)
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (1, pair, *kickers)
    else:
        # high card
        return (0, *sorted(ranks, reverse=True))

def check_straight(ranks):
    ranks = list(set(ranks))  # remove duplicates
    ranks.sort(reverse=True)
    
    if set([14, 2, 3, 4, 5]).issubset(ranks):  # wheel
        return True, 5

    for i in range(len(ranks) - 4):
        window = ranks[i:i+5]
        if window[0] - window[4] == 4 and len(window) == 5:
            return True, window[0]
    return False, 0

def get_key(d, val):
    return max(k for k, v in d.items() if v == val)

def poker(bot, opponent, community):
    bot_best = best_hand(bot + community)
    opp_best = best_hand(opponent + community)

    if bot_best > opp_best:
        return "bot"
    elif opp_best > bot_best:
        return "opponent"
    else:
        return "tie"

def mcts(bot, community):
    wins = 0
    total = 0

    known_cards = set(bot + community)
    unknown_cards = [c for c in range(1, 54) if c not in known_cards]

    # you have 10 seconds
    start_time = time.time()
    time_limit = 10

    while time.time() - start_time < time_limit:
        # generate random rollouts
        random.shuffle(unknown_cards)
        idx = 0

        opponent = [unknown_cards[idx], unknown_cards[idx + 1]]
        idx += 2

        full_community = community[:]
        while len(full_community) < 5:
            full_community.append(unknown_cards[idx])
            idx += 1

        winner = poker(bot, opponent, full_community)
        if winner == "bot":
            wins += 1
        total += 1

    print("MCTS Wins / Total: ", wins/total)

    return wins / total

def main():
    # shuffle deck
    random.shuffle(deck)

    print(deck)

    bot = []
    opponent = []
    community = []

    # pre-flop
    bot.append(deck.pop(0))
    bot.append(deck.pop(0))
    opponent.append(deck.pop(0))
    opponent.append(deck.pop(0))

    print("Bot: ", bot)
    print("Opponent: ", opponent)

    if mcts(bot, community) < 0.5:
        print("Folded pre-flop")
        return "fold"

    # flop
    community.append(deck.pop(0))
    community.append(deck.pop(0))
    community.append(deck.pop(0))

    print("Community: ", community)

    if mcts(bot, community) < 0.5:
        print("Folded pre-turn")
        return "fold"

    # turn
    community.append(deck.pop(0))
    print("Community: ", community)

    if mcts(bot, community) < 0.5:
        print("Folded pre-river")
        return "fold"

    # river
    community.append(deck.pop(0))
    print("Community: ", community)

    winner = poker(bot, opponent, community)

    print("Winner: ", winner)

    return winner


if __name__ == "__main__":
    main()

