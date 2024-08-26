import random
from collections import Counter

SUIT_EMOJIS = {'H': '♥️', 'D': '♦️', 'C': '♣️', 'S': '♠️'}
CARD_VALUES = {'A':14,'K':13,'Q':12,'J':11,'T':10,'9':9,'8':8,'7':7,'6':6,'5':5,'4':4,'3':3,'2':2}
HAND_SIZE = 8

def create_deck():
    ranks = '23456789TJQKA'
    suits = 'HDCS'
    return [f"{r}{s}" for r in ranks for s in suits]

def card_to_emoji(card):
    return f"{card[0]}{SUIT_EMOJIS[card[1]]}"

def generate_possible_straights():
    values = list(CARD_VALUES.keys())
    straights = []
    for i in range(len(values) - 4):
        straights.append(values[i:i+5])
    straights.append(['A', '2', '3', '4', '5'])  # Add the Ace-low straight
    return straights

POSSIBLE_STRAIGHTS = generate_possible_straights()

def optimal_discard_straight(hand):
    values = [card[0] for card in hand]
    unique_values = set(values)
    
    # Step 1: Prioritize discarding duplicates, but leave at least one of each
    value_counts = Counter(values)
    duplicates = []
    for value, count in value_counts.items():
        if count > 1:
            cards_of_value = [card for card in hand if card[0] == value]
            duplicates.extend(cards_of_value[1:])  # Keep one, discard the rest
    
    if len(duplicates) >= 5:
        return duplicates[:5], unique_values
    
    # Step 2 & 3: Find the straight with the most intersections
    best_straight = max(POSSIBLE_STRAIGHTS, 
                        key=lambda s: (len(set(s) & unique_values), max(CARD_VALUES[v] for v in s)))
    
    # Step 4: Prioritize discarding duplicates, then cards outside the best straight
    keep_values = set(best_straight)
    discard = duplicates.copy()  # Start with the duplicates we identified earlier
    
    # Add cards outside the best straight, but not already in discard
    for card in hand:
        if card[0] not in keep_values and card not in discard:
            discard.append(card)
    
    # # If we're discarding less than 5 cards, add more cards to discard
    # if len(discard) < 5:
    #     keep = [card for card in hand if card[0] in keep_values]
    #     keep.sort(key=lambda x: CARD_VALUES[x[0]], reverse=True)
    #     discard.extend(keep[5-len(discard):])
    
    return discard[:5], unique_values

def optimal_discard_flush(hand):
    suits = [card[1] for card in hand]
    suit_counts = Counter(suits)
    target_suit = max(suit_counts, key=suit_counts.get)
    return [card for card in hand if card[1] != target_suit]

def is_straight(hand):
    values = [CARD_VALUES[card[0]] for card in hand]
    unique_values = sorted(set(values))
    
    for i in range(len(unique_values) - 4):
        if unique_values[i+4] - unique_values[i] == 4:
            return True
    
    if set([14, 2, 3, 4, 5]).issubset(set(values)):
        return True
    
    return False

def is_flush(hand):
    suit_counts = Counter(card[1] for card in hand)
    return max(suit_counts.values()) >= 5

def simulate_draw(initial_hand, deck, target_hand_type, max_draws=3, debug=False):
    hand = initial_hand.copy()
    random.shuffle(deck)
    draw_pile = deck.copy()
    discard_pile = []  # Keep track of all discarded cards

    if debug:
        print(f"Starting {target_hand_type} attempt with hand: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")

    for draw in range(max_draws):
        if target_hand_type == 'straight' and is_straight(hand):
            if debug:
                print(f"Straight achieved on draw {draw+1}: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
            return True
        elif target_hand_type == 'flush' and is_flush(hand):
            if debug:
                print(f"Flush achieved on draw {draw+1}: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
            return True

        if debug:
            if target_hand_type == 'straight':
                print(f"Current hand: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
                print(f"Current unique values: {sorted(set(card[0] for card in hand), key=lambda x: CARD_VALUES[x], reverse=True)}")
            else:
                suit_counts = Counter(card[1] for card in hand)
                print(f"Current suit counts: {dict(suit_counts)}")
        
        if target_hand_type == 'straight':
            discard, unique_values = optimal_discard_straight(hand)
        else:
            discard = optimal_discard_flush(hand)
            discard = discard[:5]

        if debug:
            print(f"Draw {draw+1} - Discarding: {[card_to_emoji(card) for card in sorted(discard, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
            print(f"Draw {draw+1} - Keeping: {[card_to_emoji(card) for card in sorted([card for card in hand if card not in discard], key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")

        hand = [card for card in hand if card not in discard]
        discard_pile.extend(discard)  # Add discarded cards to discard pile
        draw_count = len(discard)
        new_cards = []
        for _ in range(draw_count):
            if draw_pile:
                new_cards.append(draw_pile.pop())
            else:
                break  # If draw pile is empty, stop drawing
        hand.extend(new_cards)

        if debug:
            print(f"Draw {draw+1} - New hand: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")

    if (target_hand_type == 'straight' and is_straight(hand)) or (target_hand_type == 'flush' and is_flush(hand)):
        if debug:
            print(f"{target_hand_type.capitalize()} achieved on final draw: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
        return True

    if debug:
        print(f"Final hand: {[card_to_emoji(card) for card in sorted(hand, key=lambda x: CARD_VALUES[x[0]], reverse=True)]}")
        if target_hand_type == 'straight':
            print(f"Final unique values: {sorted(set(card[0] for card in hand), key=lambda x: CARD_VALUES[x], reverse=True)}")
        else:
            print(f"Final suit counts: {dict(Counter(card[1] for card in hand))}")
        print(f"{target_hand_type.capitalize()} not achieved")

    return False

def run_simulation(num_simulations=10000):
    straight_successes = 0
    flush_successes = 0
    deck = create_deck()

    print("Debugging a single straight attempt:")
    # Random starting hand
    straight_hand = random.sample(deck, HAND_SIZE)
    # Fixed starting hand (uncomment to use)
    # straight_hand = ['AH', 'QD', 'JS', '9H', '4H', '2D', '2S', '2C']
    straight_deck = [card for card in deck if card not in straight_hand]
    simulate_draw(straight_hand, straight_deck, 'straight', debug=True)

    print("\nDebugging a single flush attempt:")
    # Random starting hand
    flush_hand = random.sample(deck, HAND_SIZE)
    # Fixed starting hand (uncomment to use)
    # flush_hand = ['2H', '3H', '2D', '3D', '2C', '3C', '2S', '3S']
    flush_deck = [card for card in deck if card not in flush_hand]
    simulate_draw(flush_hand, flush_deck, 'flush', debug=True)

    print("\nRunning full simulation...")
    for _ in range(num_simulations):
        # Random starting hand
        straight_hand = random.sample(deck, HAND_SIZE)
        # Fixed starting hand (uncomment to use)
        # straight_hand = ['7H', '7D', '7S', '7C', '2H', '2D', '2S', '2C']
        straight_deck = [card for card in deck if card not in straight_hand]
        
        if simulate_draw(straight_hand, straight_deck, 'straight'):
            straight_successes += 1
        
        # Random starting hand
        flush_hand = random.sample(deck, HAND_SIZE)
        # Fixed starting hand (uncomment to use)
        # flush_hand = ['2H', '3H', '2D', '3D', '2C', '3C', '2S', '3S']
        flush_deck = [card for card in deck if card not in flush_hand]
        
        if simulate_draw(flush_hand, flush_deck, 'flush'):
            flush_successes += 1

    straight_probability = straight_successes / num_simulations
    flush_probability = flush_successes / num_simulations
    print(f"Straight probability: {straight_probability:.6f}")
    print(f"Flush probability: {flush_probability:.6f}")

run_simulation()