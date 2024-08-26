import random
from itertools import combinations
from collections import defaultdict
import json
import os

# Constants
HAND_SIZE = 8
DISCARD_OPPORTUNITIES = 3
MAX_DISCARD = 5
STRAIGHT_LENGTH = 5
RANKS = '23456789TJQKA'
SUITS = 'HDCS'

def create_deck():
    return [f"{rank}{suit}" for rank in RANKS for suit in SUITS]

def deal_hand(deck, size=HAND_SIZE):
    return [deck.pop() for _ in range(size)]

def rank_value(card):
    return RANKS.index(card[0])

def is_straight(cards):
    values = sorted(set(rank_value(card) for card in cards))
    return len(values) >= STRAIGHT_LENGTH and values[-1] - values[0] == STRAIGHT_LENGTH - 1

def longest_sequence(hand):
    values = sorted(set(rank_value(card) for card in hand))
    max_length = 1
    current_length = 1
    for i in range(1, len(values)):
        if values[i] - values[i-1] == 1:
            current_length += 1
            max_length = max(max_length, current_length)
        else:
            current_length = 1
    return max_length

def encode_state(hand):
    longest_seq = longest_sequence(hand)
    hand_values = tuple(sorted(set(rank_value(card) for card in hand)))
    return (longest_seq, hand_values)

def get_possible_actions():
    return [tuple(sorted(comb)) for r in range(1, MAX_DISCARD + 1) 
            for comb in combinations(range(HAND_SIZE), r)]

def q_learning_agent(q_table, state, epsilon):
    if random.random() < epsilon:
        return random.choice(get_possible_actions())
    else:
        return max(get_possible_actions(), key=lambda a: q_table[state][a])

def calculate_reward(old_hand, new_hand):
    old_longest = longest_sequence(old_hand)
    new_longest = longest_sequence(new_hand)
    if is_straight(new_hand):
        return 10
    elif new_longest > old_longest:
        return 1
    elif new_longest < old_longest:
        return -1
    else:
        return 0

def play_game(q_table, epsilon):
    deck = create_deck()
    random.shuffle(deck)
    hand = deal_hand(deck)
    
    for _ in range(DISCARD_OPPORTUNITIES):
        if is_straight(hand):
            return 1  # Win
        
        state = encode_state(hand)
        action = q_learning_agent(q_table, state, epsilon)
        
        old_hand = hand.copy()
        # Discard and draw new cards
        for idx in sorted(action, reverse=True):
            del hand[idx]
        hand.extend(deal_hand(deck, len(action)))
        
        reward = calculate_reward(old_hand, hand)
        if reward == 10:  # Straight formed
            return 1
    
    return 0 if not is_straight(hand) else 1

def train_q_learning(episodes, learning_rate, discount_factor, epsilon):
    q_table = defaultdict(lambda: defaultdict(float))
    possible_actions = get_possible_actions()
    
    for episode in range(episodes):
        deck = create_deck()
        random.shuffle(deck)
        hand = deal_hand(deck)
        
        for _ in range(DISCARD_OPPORTUNITIES):
            state = encode_state(hand)
            action = q_learning_agent(q_table, state, epsilon)
            
            old_hand = hand.copy()
            for idx in sorted(action, reverse=True):
                del hand[idx]
            hand.extend(deal_hand(deck, len(action)))
            
            next_state = encode_state(hand)
            reward = calculate_reward(old_hand, hand)
            
            best_next_action = max(possible_actions, key=lambda a: q_table[next_state][a])
            td_target = reward + discount_factor * q_table[next_state][best_next_action]
            td_error = td_target - q_table[state][action]
            q_table[state][action] += learning_rate * td_error
            
            if is_straight(hand):
                break
        
        if episode % 10000 == 0:
            print(f"Episode {episode} completed")
    
    return q_table

def evaluate_agent(q_table, num_games):
    wins = sum(play_game(q_table, epsilon=0) == 1 for _ in range(num_games))
    return wins / num_games

def save_q_table(q_table, filename):
    with open(filename, 'w') as f:
        json.dump({str(k): v for k, v in q_table.items()}, f)

def load_q_table(filename):
    with open(filename, 'r') as f:
        return defaultdict(lambda: defaultdict(float), {eval(k): v for k, v in json.load(f).items()})

def visualize_strategy(q_table):
    deck = create_deck()
    hand = deal_hand(deck)
    print(f"Initial hand: {', '.join(hand)}")
    
    for round in range(DISCARD_OPPORTUNITIES):
        state = encode_state(hand)
        action = q_learning_agent(q_table, state, epsilon=0)
        
        print(f"\nRound {round + 1}:")
        print(f"Current hand: {', '.join(hand)}")
        print(f"Longest sequence: {longest_sequence(hand)}")
        print(f"Discarding: {', '.join([hand[i] for i in action])}")
        
        old_hand = hand.copy()
        for idx in sorted(action, reverse=True):
            del hand[idx]
        new_cards = deal_hand(deck, len(action))
        hand.extend(new_cards)
        
        print(f"New cards: {', '.join(new_cards)}")
        print(f"Updated hand: {', '.join(hand)}")
        print(f"New longest sequence: {longest_sequence(hand)}")
        print(f"Reward: {calculate_reward(old_hand, hand)}")
        
        if is_straight(hand):
            print("Straight found! Game won.")
            return
    
    print("No straight found. Game lost.")

# Training parameters
EPISODES = 1000000  # Increased number of episodes
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.99  # Increased discount factor
EPSILON = 0.1
SAVE_FILE = 'q_table_improved.json'

# Train or load the agent
if os.path.exists(SAVE_FILE):
    print("Loading previously trained Q-table...")
    trained_q_table = load_q_table(SAVE_FILE)
else:
    print("Training new Q-table...")
    trained_q_table = train_q_learning(EPISODES, LEARNING_RATE, DISCOUNT_FACTOR, EPSILON)
    save_q_table(trained_q_table, SAVE_FILE)

# Evaluate the agent
num_evaluation_games = 10000
win_rate = evaluate_agent(trained_q_table, num_evaluation_games)
print(f"Win rate over {num_evaluation_games} games: {win_rate:.2%}")

# Visualize the strategy
print("\nVisualizing the agent's strategy:")
visualize_strategy(trained_q_table)