import random
from collections import Counter, defaultdict
from itertools import combinations

# === Card and Deck Setup ===
RANKS = "23456789TJQKA"
SUITS = "cdhs"  # Clubs, Diamonds, Hearts, Spades
RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}

HAND_RANKS = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight",
    "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
]

def create_deck():
    return [r + s for r in RANKS for s in SUITS]

def card_value(card):
    return RANK_VALUES[card[0]]

def card_rank(card):
    return card[0]

def card_suit(card):
    return card[1]

# === Hand Evaluation ===
def evaluate_hand(cards):
    counts = Counter(card_rank(c) for c in cards)
    suits = defaultdict(list)
    for c in cards:
        suits[card_suit(c)].append(c)
    
    is_flush, flush_cards = False, []
    for suit, suited in suits.items():
        if len(suited) >= 5:
            is_flush = True
            flush_cards = sorted(suited, key=card_value, reverse=True)

    # Prepare list of card values (for straight detection)
    values = sorted(set(card_value(c) for c in cards), reverse=True)
    if 14 in values:  # Ace can be low in a straight
        values.append(1)

    def find_straight(vals):
        for i in range(len(vals) - 4):
            window = vals[i:i+5]
            if all(window[j] - 1 == window[j+1] for j in range(4)):
                return window[0]
        return None

    straight_high = find_straight(values)

    # Straight flush / royal flush
    straight_flush = None
    if is_flush:
        flush_vals = sorted(set(card_value(c) for c in flush_cards), reverse=True)
        if 14 in flush_vals:
            flush_vals.append(1)
        sf_high = find_straight(flush_vals)
        if sf_high:
            straight_flush = sf_high
            if sf_high == 14:
                return (9, [14])  # Royal Flush
            else:
                return (8, [sf_high])  # Straight Flush

    # Four of a kind
    for rank, count in counts.items():
        if count == 4:
            kicker = max([card_value(c) for c in cards if card_rank(c) != rank])
            return (7, [RANK_VALUES[rank], kicker])

    # Full house
    trips = [r for r, c in counts.items() if c == 3]
    pairs = [r for r, c in counts.items() if c == 2]
    if trips:
        trip_val = max(trips, key=RANK_VALUES.get)
        if len(trips) > 1:
            pair_val = max([r for r in trips if r != trip_val], default=None)
        else:
            pair_val = max(pairs, default=None, key=RANK_VALUES.get)
        if pair_val:
            return (6, [RANK_VALUES[trip_val], RANK_VALUES[pair_val]])

    # Flush
    if is_flush:
        return (5, sorted([card_value(c) for c in flush_cards[:5]], reverse=True))

    # Straight
    if straight_high:
        return (4, [straight_high])

    # Three of a kind
    if trips:
        trip_val = max(trips, key=RANK_VALUES.get)
        kickers = sorted([card_value(c) for c in cards if card_rank(c) != trip_val], reverse=True)
        return (3, [RANK_VALUES[trip_val]] + kickers[:2])

    # Two pair
    pairs = [r for r, c in counts.items() if c == 2]
    if len(pairs) >= 2:
        top2 = sorted([RANK_VALUES[r] for r in pairs], reverse=True)[:2]
        kicker = max([card_value(c) for c in cards if RANK_VALUES[card_rank(c)] not in top2])
        return (2, top2 + [kicker])

    # One pair
    if len(pairs) == 1:
        pair_val = RANK_VALUES[pairs[0]]
        kickers = sorted([card_value(c) for c in cards if card_rank(c) != pairs[0]], reverse=True)
        return (1, [pair_val] + kickers[:3])

    # High card
    return (0, sorted([card_value(c) for c in cards], reverse=True)[:5])

# === Game Simulation ===
def simulate_hand(num_players=3):
    deck = create_deck()
    random.shuffle(deck)

    hands = {i: [deck.pop(), deck.pop()] for i in range(1, num_players+1)}
    board = [deck.pop() for _ in range(5)]

    print("=== Poker Hand Simulator ===")
    print(f"Players: {num_players}\n")
    for i, hand in hands.items():
        print(f"Player {i}: [{' '.join(hand)}]")

    print(f"\nBoard: [{' '.join(board)}]\n")

    scores = {}
    for i, hand in hands.items():
        full_hand = hand + board
        rank = evaluate_hand(full_hand)
        scores[i] = rank
        rank_name = HAND_RANKS[rank[0]]
        print(f"Player {i}: {rank_name}")

    best_rank = max(scores.values())
    winners = [i for i, r in scores.items() if r == best_rank]

    if len(winners) == 1:
        print(f"\nWinner: Player {winners[0]} 🏆")
    else:
        print(f"\nSplit pot between: {', '.join('Player ' + str(w) for w in winners)} 🤝")

# === Main ===
if __name__ == "__main__":
    try:
        num = int(input("Enter number of players (2–10): "))
        if not 2 <= num <= 10:
            raise ValueError
    except ValueError:
        print("Invalid input. Defaulting to 3 players.")
        num = 3

    simulate_hand(num)