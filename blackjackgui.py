# TIE-02106 Introduction to Programming
# PseudoBlackjack game using tkinter
# Lassi Raatikainen 277990, Tampere University of Technology

"""
Documentation/rules of game:
In PseudoBlackjack the rules are similar to those of actual Blackjack. In the beginning of a turn you press serve cards
to get your first two cards, after which you can't use the button again in the same turn, as the following cards if
the player wants more will be dealt one at a time from the button saying "One more card!". The "One more card!" button
will then get disabled if the points gained within a turn go over 21, as then the player has in effect lost the round.
The "One more card!" button is also disabled if the player has not been dealt their first two cards.
The "End turn!" button causes the player's turn to end which will either start the next player's turn or if it already
that the game will end and will show the result of the game in the bottom left corner. The state of the game is always
shown at the bottom left hand corner (in effect who's turn is it or who won the game).
The "Start a new game!"  button resets the game and scores in effect simply starting a new game as the button implies.
The "Quit game" simply closes the program.

Object of the game: To get to 21 points or as close to it, without going over it.

How to win: The player with the most points under 22 wins, if players have the same amount of points the game is called
to be a draw.

Special cases (Naturals): If a player gets 21 points on their first two cards they achieve a natural, in which case
they will win even if another player got 21 points, unless they also got a natural in which case the game is called to
be a draw.

Scoring: All of the face cards are worth 10 points, the ace is worth 11 points if the player has not exceeded 10 points
during the turn and 1 point if the player has exceeded 10 points, all of the other cards are worth their pip values.

Scalable GUI: The game is scalable to however many players the user wants to play with and this is
determined based on the value of the constant PLAYER_AMOUNT within the code. The amount of cards dealt cannot be
changed as that would fundamentally change the ruleset of the game.
"""

from tkinter import *
import random

CARDPICS = ["Gray_back.gif", "2S.gif", "3S.gif", "4S.gif", "5S.gif", "6S.gif", "7S.gif", "8S.gif", "9S.gif", "10S.gif",
            "AS.gif", "JS.gif", "KS.gif", "QS.gif"]

PLAYER_AMOUNT = 4  # assigning a global constant for the amount of player for the game


class Blackjack:
    def __init__(self):
        """
        Initialising the class of Blackjack
        """
        self.__window = Tk()  # creating a tkinter window for the game
        self.__window.title("Blackjack")  # changing the title of the window to Blackjack

        self.__cardpics = []  # initialising list for the card pictures
        for cardfile in CARDPICS:  # going through the list containing cards' pictures names
            picture = PhotoImage(file=cardfile)
            picture = picture.subsample(4, 4)  # making the pictures significantly smaller in size to fit the UI nicely
            self.__cardpics.append(picture)  # appending pictures of cards into the list

        for i in range(PLAYER_AMOUNT):  # creating labels for all players, so their scores can be tracked easily
            Label(self.__window, text="Player " + str(i + 1) + " score:") \
                .grid(row=i + 1, column=0, sticky=E)

        self.__infoLabel = Label(self.__window)  # creating a label containing information of the gamestate
        self.__infoLabel.grid(row=PLAYER_AMOUNT + 1, column=0, columnspan=2)
        self.__pointlabels = []  # initialising a list for labels of players' points

        for i in range(PLAYER_AMOUNT):
            new_label = Label(self.__window)  # adding all labels for players' points into the GUI
            new_label.grid(row=i + 1, column=1, sticky=W)
            self.__pointlabels.append(new_label)  # appending all labels for players' points into a list

        self.__cardpiclabel1 = Label(self.__window)  # adding the pictures of cards to interface to show points gained
        self.__cardpiclabel1.grid(row=0, column=2)
        self.__cardpiclabel2 = Label(self.__window)
        self.__cardpiclabel2.grid(row=0, column=3)

        # adding buttons for one more card, ending turn, starting new game,
        # quitting game and serving first cards all with their appropriate commands
        self.__newcardbutton = Button(self.__window, text="One more card!", command=self.new_card)
        self.__newcardbutton.grid(row=0, column=4, sticky=W + E)
        self.__nextturnbutton = Button(self.__window, text="End turn!", command=self.next_turn)
        self.__nextturnbutton.grid(row=1, column=4, sticky=W + E)
        Button(self.__window, text="Start new game!", command=self.new_game).grid(row=2, column=4, sticky=W + E)
        Button(self.__window, text="Quit game", command=self.__window.destroy).grid(row=3, column=4, sticky=W + E)
        Button(self.__window, text="Serve cards", command=self.first_cards).grid(row=0, column=0, sticky=W + E)

        self.__natural = [False] * PLAYER_AMOUNT  # initialising a list for naturals gotten during the game
        self.__firsthit = True  # creating a variable tracking if first two cards have been dealt during the turn
        self.__turn = 0  # creating a variable tracking which turn it is
        self.__playerpoints = [0] * PLAYER_AMOUNT  # initialising a list for points of the players
        # creating a variable for the state of the game, which will be used in the info label initialised earlier
        self.__gamesituationtext = "Player " + str(self.__turn + 1) + " turn"
        self.__firsthitpoints = [0] * 2  # initialising a list containing points gotten during first two cards
        self.__additionalhitpoints = 0  # creating a variable tracking points gained when dealt an additional card
        # configuring pictures of card pack to labels of card pictures to signify
        # that no cards have been dealt at the moment in their respective slots
        self.__cardpiclabel1.configure(image=self.__cardpics[0])
        self.__cardpiclabel2.configure(image=self.__cardpics[0])
        self.__card1 = 0  # creating a variable tracking value of first card of the initial deal of two cards
        self.__card2 = 0  # creating a variable tracking value of second card of the initial deal of two cards
        self.__card = 0  # creating a variable tracking value of additional card deal

        self.new_game()  # resetting game state to beginning state

    def update_ui(self):
        """
        Updates the user interface to represent current situation of the game
        :return: None
        """
        for i in range(len(self.__pointlabels)):  # updating all the points of players
            self.__pointlabels[i].configure(text=self.__playerpoints[i])

        self.__infoLabel.configure(text=self.__gamesituationtext)  # updating game situation text

    def first_cards(self):
        """
        Deals first two cards of the turn and gives player the points from the deal. Cannot be used if it
        already has been used once during the turn
        :return: None
        """
        if self.__firsthit:  # checks that the first two cards have not been dealt already during the turn
            # assigning two random integers within 1-13 to first and second card dealt
            # and assigning correct pictures for their respective labels with the random integers
            self.__card1 = random.randint(1, 13)
            self.__card2 = random.randint(1, 13)
            self.__cardpiclabel1.configure(image=self.__cardpics[self.__card1])
            self.__cardpiclabel2.configure(image=self.__cardpics[self.__card2])
            # determining points given to players based on the random integers of the cards
            if 1 <= self.__card1 <= 9:  # situations with number cards
                self.__firsthitpoints[0] = self.__card1 + 1
            elif self.__card1 == 10:  # situation with ace
                self.__firsthitpoints[0] = 11
            elif self.__card1 > 10:  # situations with face cards
                self.__firsthitpoints[0] = 10
            if 1 <= self.__card2 <= 9:  # situations with number cards
                self.__firsthitpoints[1] = self.__card2 + 1
            elif self.__card2 == 10:  # situation with ace
                if self.__firsthitpoints[0] == 11:  # if first card was an ace give player 1 point
                    self.__firsthitpoints[1] = 1
                else:  # if first card was not an ace give them 11 points
                    self.__firsthitpoints[1] = 11
            elif self.__card2 > 10:  # situations with face cards
                self.__firsthitpoints[1] = 10
            # rewarding player with points equal to the sum of the first two cards' points
            self.__playerpoints[self.__turn] += sum(self.__firsthitpoints)
            # if player got 21 points within their first two cards award them with a natural
            if self.__playerpoints[self.__turn] == 21:
                self.__natural[self.__turn] = True
            # change variable to indicate that first two cards have been dealt
            self.__firsthit = False
            self.update_ui()  # update the UI to show correct points for player's turn
        else:  # if first cards have been dealt during the turn do nothing
            pass

    def new_card(self):
        """
        Deals player another card as long as the player has not passed 21 points during the turn already
        and if the player has already been dealt their first two cards.
        :return: None
        """
        # making sure the player has not exceeded
        if not self.__firsthit and self.__playerpoints[self.__turn] < 22:
            # assigning a random integer within 1-13 to new card dealt
            # and assigning correct picture for the left label of a card using the random integer
            self.__card = random.randint(1, 13)
            self.__cardpiclabel1.configure(image=self.__cardpics[self.__card])
            # rewarding player the correct amount of points with the random integer value
            if 1 <= self.__card <= 9:  # situations with number cards
                self.__additionalhitpoints = self.__card + 1
            elif self.__card == 10:  # situation with ace
                if self.__playerpoints[self.__turn] <= 10:  # if player hasn't exceeded 10 points award them 11 points
                    self.__additionalhitpoints = 11
                else:  # if player has exceeded 10 points award them 1 point
                    self.__additionalhitpoints = 1
            elif self.__card > 10:  # situations with face cards
                self.__additionalhitpoints = 10
            # configuring the second card picture to be of the deck to signify the second card was not dealt
            self.__cardpiclabel2.configure(image=self.__cardpics[0])
            self.__playerpoints[self.__turn] += self.__additionalhitpoints  # awarding player their points

            self.update_ui()  # updating UI to show the amount of points player gained
        else:  # if player has passed 21 points during turn or has not been dealt first two cards, do nothing
            pass

    def next_turn(self):
        """
        Ends the turn of the player resulting in the turn moving to the next player or showing the result of the game
        :return: None
        """
        if self.__turn < (PLAYER_AMOUNT - 1):  # if it not the last player's turn yet move the turn to next player
            self.__turn += 1  # increase the turn by one moving the turn to next player
            self.__gamesituationtext = "Player " + str(self.__turn + 1) + " turn"  # change the situation description
            self.__firsthit = True  # indicate that the first two cards have not been dealt during the new turn
            self.update_ui()  # update the UI to indicate the turn has changed
        else:  # if it is the last player's turn determine and show the result of the game
            self.winner()  # call method to determine and show the winner

    def start_game(self):
        """
        Starts tkinter window
        :return: None
        """
        self.__window.mainloop()

    def new_game(self):
        """
        Restart game state to beginning in effect starting a new game
        :return: None
        """
        self.__natural = [False] * PLAYER_AMOUNT  # resetting the naturals gotten during the game
        self.__firsthit = True  # resetting variable tracking whether first two cards have been dealt
        self.__firsthitpoints = [0] * 2  # resetting points gotten by the player's first two cards
        self.__additionalhitpoints = 0  # resetting points gotten with additional card
        self.__turn = 0  # resetting turn to player 1
        self.__playerpoints = [0] * PLAYER_AMOUNT  # resetting all players' points
        # resetting game situation's text to indicate it's player 1's turn
        self.__gamesituationtext = "Player " + str(self.__turn + 1) + " turn"
        # resetting both pictures of cards to pictures of decks signifying no cards have been dealt
        self.__cardpiclabel1.configure(image=self.__cardpics[0])
        self.__cardpiclabel2.configure(image=self.__cardpics[0])

        self.update_ui()  # updating UI to represent current state of the game

    def winner(self):
        """
        Determines the result of the game and updates the game UI to show who won or if the game ended in a draw.
        :return:
        """
        draw = False  # variable tracking whether game ended in a tie
        winner_found = False  # variable tracking whether a winner has been found
        i = 0  # creating a variable that tracks which player is being checked to have a natural
        naturals = []

        for player in self.__natural:  # checking if any player got a natural
            if player:
                naturals.append(i)
            i += 1

        if len(naturals) == 1:  # if one player got a natural update that player to be the winner of the game
            winner = naturals[0]
            winner_found = True  # change variable to display that a winner has been found
        elif len(naturals) == 0:  # if no one got a natural continue to attempt finding a winner
            winner_found = False
        else:  # if more than one player got a natural call the game as a draw
            draw = True
            winner_found = True  # update the variable to indicate a 'winner' was found
        if not winner_found:  # if winner has not been found yet attempt finding it with another method
            i = 0  # reset variable of which player is being checked
            best_found = 0  # create a variable for the best score found thus far

            # going through all players' points to see who had the best score
            for points in self.__playerpoints:
                # if points found are better than previous best update the new best found and change current winner
                # to be the current player who's points are the best found at that point
                if points > best_found and points <= 21:
                    best_found = points
                    winner = i
                    draw = False  # change the state of the result of the game to not be a draw
                # if current points are the same as the previous best found points update the game to be a draw
                # at the current time
                elif points == best_found:
                    draw = True
                # if at the end the best found score is still 0 call the game to be a draw
                elif best_found == 0:
                    draw = True
                i += 1

        # if the game ended in a draw change the game's situation text to signify that
        if draw:
            self.__gamesituationtext = "It's a draw!"
        # if the game was not a draw update the game's situation text to show who won the game
        else:
            self.__gamesituationtext = "Player " + str(winner + 1) + " wins!"

        self.update_ui()  # update the UI to show the result of the game


def main():
    game = Blackjack()  # create a Blackjack class
    game.start_game()  # initialise the Blackjack class' tkinter window


main()