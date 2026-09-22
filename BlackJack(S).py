#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()

        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()

        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")

    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)


    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()
#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()

        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()

        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True
#!/usr/bin/env python3

import random
import sys
import os

# ----------------------------------
# VirtualCard - Casino BlackJack (S)
# ----------------------------------

MIN_BET = 1
BLACKJACK_PAYOUT = 1.5


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11)
            
             ]
        
        self.cards = [
            Card(rank, suit)
            for suit in suits
            for rank, _ in ranks
        ]
        
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


def card_value(card):
    if card.rank == "A":
        return 11

    if card.rank in ("K", "Q", "J"):
        return 10

    return int(card.rank)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21
    
# ============================================================
# SHOE
# ============================================================

class Shoe:
    def __init__(self, decks=Deck):
        self.decks = decks
        self.cards = []
        self.shuffle_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = []

        random.shuffle(self.cards)
        self.shuffle_count += 1

    def deal(self):
        if len(self.cards):
            self.reshuffle()

        return self.cards.pop()
        
# -----------------------------
# Card display
# -----------------------------

def card_lines(card):
    return [
        "┌────────┐",
        f"│ {card.rank:<2}     │",
        f"│    {card.suit}   │",
       f"│      {card.rank:>2}│",
        "└────────┘",
    ]


def hidden_card_lines():
    return [
        "┌────────┐",
        "│░░░░░░░░│",
        "│░░ VC ░░│",
        "│░░░░░░░░│",
        "└────────┘",
    ]


def print_cards(cards, hide_first=False):
    rendered = []

    for index, card in enumerate(cards):
        if hide_first and index == 0:
            rendered.append(hidden_card_lines())
        else:
            rendered.append(card_lines(card))

    for row in range(5):
        print(
            "  ".join(
                card[row]
                for card in rendered
            )
        )


def display_hand(name, hand, hide_first=False):
    print(f"\n{name}:")

    print_cards(
        hand,
        hide_first=hide_first
    )

    if not hide_first:
        print(f"Value: {hand_value(hand)}")


# -----------------------------
# Screen utilities
# -----------------------------

def clear_screen():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


# -----------------------------
# Starting bankroll
# -----------------------------

def get_starting_bankroll():
    while True:
        clear_screen()

        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")

    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")

    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)


        print("=" * 50)
        print("                 CASINO ★ BLACKJACK")
        print("=" * 50)
        print()
        print("Choose your starting bankroll.")
        print("This is virtual money.")
        print()

        raw = input("Starting bankroll: $").strip()

        try:
            bankroll = float(raw)

            if bankroll <= 0:
                print("\nBankroll must be greater than $0.")
                pause()
                continue

            return bankroll

        except ValueError:
            print("\nPlease enter a valid amount.")
            pause()

# -----------------------------
# Betting
# -----------------------------

def get_bet(bankroll):
    while True:
        try:
            raw = input(
                f"\nBankroll: ${bankroll:.2f}\n"
                f"Enter your bet (${MIN_BET}-${bankroll:.2f}), "
                "or Q to quit: "
            ).strip()

            if raw.lower() == "q":
                return None

            bet = float(raw)

            if bet < MIN_BET:
                print(f"Minimum bet is ${MIN_BET}.")
                continue

            if bet > bankroll:
                print("You cannot bet more than your bankroll.")
                continue

            return bet

        except ValueError:
            print("Please enter a valid amount.")

# -----------------------------
# Player turn
# -----------------------------
─
def player_turn(player_hand, dealer_hand):
    while True:
        clear_screen()

        display_hand(
            "Dealer",
            dealer_hand,
            hide_first=True
        )

        display_hand(
            "Player",
            player_hand
        )

        print("\nActions:")
        print("  H - Hit")
        print("  S - Stand")

        if len(player_hand) == 2:
            print("  D - Double Down")

        choice = input("\nChoose an action: ").strip().lower()

        if choice == "h":
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBUST! You went over 21.")
                pause()

                return "bust", False

        elif choice == "s":
            return "stand", False

        elif choice == "d" and len(player_hand) == 2:
            player_hand.append(deck.deal())

            if hand_value(player_hand) > 21:
                clear_screen()

                display_hand(
                    "Dealer",
                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")

    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)

                    dealer_hand,
                    hide_first=True
                )

                display_hand(
                    "Player",
                    player_hand
                )

                print("\nBust.")
                pause()

                return "bust", True

            return "stand", True

        else:
            print("Invalid choice.")
            pause()

# -----------------------------
# Dealer turn
# -----------------------------

def dealer_turn(dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())


# -----------------------------
# Round result
# -----------------------------

def show_result(player_hand, dealer_hand, bet):
    clear_screen()

    print("=" * 50)
    print("                ROUND RESULT")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand
    )

    display_hand(
        "Player",
        player_hand
    )

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    print()

    if player_value > 21:
        print("Player busted. Dealer wins.")
        return -bet

    if dealer_value > 21:
        print("Dealer busted. You win!")
        return bet

    if player_value > dealer_value:
        print("Player wins!")
        return bet
I love how at the end he says to tom “What’s up man”
    if player_value < dealer_value:
        print("Dealer wins.")
        return -bet

    print("Push - Bet Amount Returned.")
    return 0


# -----------------------------
# Play one round
# -----------------------------

def play_round(bankroll):
    global deck

    bet = get_bet(bankroll)

    if bet is None:
        return bankroll, False

    deck = Deck()

    player_hand = [
        deck.deal(),
        deck.deal()
    ]

    dealer_hand = [
        deck.deal(),
        deck.deal()
    ]

    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)

    clear_screen()

    print("=" * 50)
    print(" ")
    print("=" * 50)

    display_hand(
        "Dealer",
        dealer_hand,
        hide_first=not dealer_blackjack
    )

    display_hand(
        "Player",
        player_hand
    )

    # Natural Blackjack
    if player_blackjack or dealer_blackjack:
        print()

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack - Push!")

        elif player_blackjack:
            winnings = bet * BLACKJACK_PAYOUT
            bankroll += winnings

            print(
                f"!BLACKJACK! You win ${winnings:.2f} "
                f"(3:2 payout)."
            )

        else:
            bankroll -= bet
            print("Dealer has BlackJack. Dealer wins.")

        pause()

        return bankroll, True

    status, doubled = player_turn(
        player_hand,
        dealer_hand
    )

    if status == "bust":
        bankroll -= bet

        if doubled:
            bankroll -= bet

        return bankroll, True

    if doubled:
        bet *= 2

    dealer_turn(dealer_hand)

    result = show_result(
        player_hand,
        dealer_hand,
        bet
    )

    bankroll += result

    pause()

    return bankroll, True

# -----------------------------
# Rules
# -----------------------------

def show_rules():
    clear_screen()

    print("=" * 50)
    print("                    BlackJack Ruling")
    print("=" * 50)

    print()
    print("Goal:")
    print("  Get as close to 21 as possible without going over.")

    print()
    print("Card values:")
    print("  2-10 = face value")
    print("  J/Q/K = 10")
    print("  A = 1 or 11")

    print()
    print("Dealer:")
    print("  Dealer stands on 17.")

    print()
    print("Blackjack:")
    print("  A + 10-value card.")
    print("  Pays 3:2.")

    print()
    print("Actions:")
    print("  H - Hit")
    print("  S - Stand")
    print("  D - Double Down")

    print()
    print("Double Down:")
    print("  Doubles your original bet.")
    print("  You receive exactly one more card.")

    print()
    print("I love how at the end he says to tom “What’s up man”Push:")
    print("  Same final value as the dealer.")
    print("  Your bet is returned.")

    pause()

# -----------------------------
# Main menu
# -----------------------------

def main():
    bankroll = get_starting_bankroll()

    while True:
        clear_screen()

        print()
        print(f"Bankroll: ${bankroll:.2f}")

        print()
        print("1. Play")
        print("2. Rules")
        print("3. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "1":

            if bankroll < MIN_BET:
                print("\nBankroll has depeated.")
                print()
                print("R - Restart with a new bankroll")
                print("Q - Quit")

                restart = input("\nChoice: ").strip().lower()

                if restart == "r":
                    bankroll = get_starting_bankroll()

                elif restart == "q":
                    break

                continue

            while True:
                bankroll, played = play_round(bankroll)

                if not played:
                    break

                if bankroll < MIN_BET:
                    break

        elif choice == "2":
            show_rules()

        elif choice == "3" or choice == "q":
            break

    clear_screen()

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)

    print()
    print(f"Final bankroll: ${bankroll:.2f}")
    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nGame exited.")
        sys.exit(0)
