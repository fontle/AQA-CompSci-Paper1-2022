# Skeleton Program code for the AQA A Level Paper 1 Summer 2022 examination
# this code should be used in conjunction with the Preliminary Material
# written by the AQA Programmer Team
# developed in the Python 3.9 programming environment

import random
import os


def Main():
    ThisGame = Breakthrough()
    ThisGame.PlayGame()


class Breakthrough():
    def __init__(self):
        self.__Deck = CardCollection("DECK")
        self.__Hand = CardCollection("HAND")
        self.__Sequence = CardCollection("SEQUENCE")
        self.__Discard = CardCollection("DISCARD")
        self.__Score = 0
        self.__Locks = []
        self.__GameOver = False
        self.__CurrentLock = Lock()
        self.__LockSolved = False
        self.__PeekUsed = False
        self.__MulliganUsed = False
        self.__LoadLocks()

    def PlayGame(self):
        if len(self.__Locks) > 0:
            self.__SetupGame()
            while not self.__GameOver:
                self.__LockSolved = False
                BonusCounter = 20
                MenuChoice = None # Prevent unbound error
                while not self.__LockSolved and not self.__GameOver:
                    print()
                    print("Current score:", self.__Score)
                    print(self.__CurrentLock.GetLockDetails(self.__Sequence.GetCardDescriptions()))
                    print(self.__Sequence.GetCardDisplay())
                    print("Cards in Deck: ", self.__Deck.GetNumberOfCards())
                    print(self.__Hand.GetCardDisplay())
                    MenuChoice = self.__GetChoice()
                    if MenuChoice == "D":
                        print(self.__Discard.GetCardDisplay())
                    elif MenuChoice == "U":
                        BonusCounter -= 1
                        CardChoice = self.__GetCardChoice()
                        DiscardOrPlay = self.__GetDiscardOrPlayChoice()
                        if DiscardOrPlay == "D":
                            self.__MoveCard(
                                self.__Hand, self.__Discard,
                                self.__Hand.GetCardNumberAt(CardChoice - 1))
                            self.__GetCardFromDeck(CardChoice)
                        elif DiscardOrPlay == "P":
                            self.__PlayCardToSequence(CardChoice)
                    elif MenuChoice == "P":
                        if not self.__PeekUsed:
                            self.__PeekUsed = True
                            print("\nPeeked Deck: ")
                            print(self.__Deck.GetCardDescriptionAt(0))
                            print(self.__Deck.GetCardDescriptionAt(1))
                            print(self.__Deck.GetCardDescriptionAt(2))
                            print()

                        else:
                            print("\nPeek already used on this lock.\n")

                    elif MenuChoice == "M":

                        if not self.__MulliganUsed:
                            # Reset Card Collections
                            self.__MulliganUsed = True
                            self.__Deck = CardCollection("DECK")
                            self.__Hand = CardCollection("HAND")
                            self.__Sequence = CardCollection("SEQUENCE")
                            self.__Discard = CardCollection("DISCARD")
                            # Create deck without difficulties
                            self.__CreateStandardDeck()
                            self.__Deck.Shuffle()
                            # Deal cards to player
                            for Count in range(5):
                                self.__MoveCard(self.__Deck, self.__Hand,
                                                self.__Deck.GetCardNumberAt(0))
                            # Add difficulties to pack
                            self.__AddDifficultyCardsToDeck()
                            # Reshuffle
                            self.__Deck.Shuffle()

                        else:
                            print("\nMulligan already used this game.\n")

                    elif MenuChoice == "Q":
                        self.__GameOver = True
                        print("\nThank you for playing!\n")
                        break # Exit current lock


                    if self.__CurrentLock.GetLockSolved():
                        if BonusCounter > 0:
                            self.__Score += BonusCounter
                        self.__PeekUsed = False
                        self.__LockSolved = True
                        self.__ProcessLockSolved()

                if MenuChoice != "Q":
                    self.__GameOver = self.__CheckIfPlayerHasLost()
        else:
            print("No locks in file.")

    def __ProcessLockSolved(self):
        self.__Score += 10
        print("Lock has been solved.  Your score is now:", self.__Score)
        while self.__Discard.GetNumberOfCards() > 0:
            self.__MoveCard(self.__Discard, self.__Deck,
                            self.__Discard.GetCardNumberAt(0))

        # Add multi-tools to deck
        for card in ["P", "K", "F"]:
            NewCard = ToolCard(card, "m")
            self.__Deck.AddCard(NewCard)

        self.__Deck.Shuffle()
        self.__CurrentLock = self.__GetRandomLock()

    def __CheckIfPlayerHasLost(self):
        if self.__Deck.GetNumberOfCards() == 0:
            print(
                "You have run out of cards in your deck.  Your final score is:",
                self.__Score)
            return True
        else:
            return False

    def __SetupGame(self):
        Choice = input("Enter L to load a game from a file, anything else to play a new game:>").upper()
        if Choice == "L":
            if not self.__LoadGame("game1.txt"):
                self.__GameOver = True
        else:
            self.__CreateStandardDeck()
            self.__Deck.Shuffle()
            for Count in range(5):
                self.__MoveCard(self.__Deck, self.__Hand,
                                self.__Deck.GetCardNumberAt(0))
            self.__AddDifficultyCardsToDeck()
            self.__AddGeniusCardToDeck()
            self.__Deck.Shuffle()
            self.__CurrentLock = self.__GetRandomLock()

    def __PlayCardToSequence(self, CardChoice):

        # If card is multi-tool
        if self.__Hand.GetCardDescriptionAt(CardChoice - 1)[2] == "m":
            Choice = input("You've chosen a multi-tool! Choose what type you want it to be (a), (b), (c):> ").lower()
            if Choice not in ["a", "b", "c"]:
                self.__PlayCardToSequence(CardChoice)
                return
            else:
                self.__Hand.SetCardToolKitAt(CardChoice - 1, Choice)

        if self.__Sequence.GetNumberOfCards() > 0:

            # If last card is of different type
            if self.__Hand.GetCardDescriptionAt(
                    CardChoice - 1)[0] != self.__Sequence.GetCardDescriptionAt(
                        self.__Sequence.GetNumberOfCards() - 1)[0]:
                self.__Score += self.__MoveCard(
                    self.__Hand, self.__Sequence,
                    self.__Hand.GetCardNumberAt(CardChoice - 1))
                self.__GetCardFromDeck(CardChoice)

            else:
                # If player tried to play same card type twice
                print(
f"""
Cannot play the same tooltype two times in a row!
You tried to play: {self.__Hand.GetCardDescriptionAt(CardChoice - 1)}
On top of previous card: {self.__Sequence.GetCardDescriptionAt(self.__Sequence.GetNumberOfCards() - 1)}
"""
                    )

        else:
            self.__Score += self.__MoveCard(
                self.__Hand, self.__Sequence,
                self.__Hand.GetCardNumberAt(CardChoice - 1))
            self.__GetCardFromDeck(CardChoice)
        if self.__CheckIfLockChallengeMet():
            print()
            print("A challenge on the lock has been met.")
            print()
            self.__Score += 5

    def __CheckIfLockChallengeMet(self):
        SequenceAsString = ""
        for Count in range(self.__Sequence.GetNumberOfCards() - 1,
                           max(0,
                               self.__Sequence.GetNumberOfCards() - 3) - 1,
                           -1):
            if len(SequenceAsString) > 0:
                SequenceAsString = ", " + SequenceAsString
            SequenceAsString = self.__Sequence.GetCardDescriptionAt(
                Count) + SequenceAsString
            if self.__CurrentLock.CheckIfConditionMet(SequenceAsString):
                return True
        return False

    def __SetupCardCollectionFromGameFile(self, LineFromFile, CardCol):
        if len(LineFromFile) > 0:
            SplitLine = LineFromFile.split(",")
            for Item in SplitLine:
                if len(Item) == 5:
                    CardNumber = int(Item[4])
                else:
                    CardNumber = int(Item[4:6])
                if Item[0:3] == "Dif":
                    CurrentCard = DifficultyCard(CardNumber)
                    CardCol.AddCard(CurrentCard)
                elif Item[0:3] == "Gen":
                    CurrentCard = GeniusCard(CardNumber)
                    CardCol.AddCard(CurrentCard)
                else:
                    CurrentCard = ToolCard(Item[0], Item[2], CardNumber)
                    CardCol.AddCard(CurrentCard)

    def __SetupLock(self, Line1, Line2):
        SplitLine = Line1.split(";")
        for Item in SplitLine:
            Conditions = Item.split(",")
            self.__CurrentLock.AddChallenge(Conditions)
        SplitLine = Line2.split(";")
        for Count in range(0, len(SplitLine)):
            if SplitLine[Count] == "Y":
                self.__CurrentLock.SetChallengeMet(Count, True)

    def __LoadGame(self, FileName):
        try:
            with open(FileName) as f:
                LineFromFile = f.readline().rstrip()
                self.__Score = int(LineFromFile)
                LineFromFile = f.readline().rstrip()
                LineFromFile2 = f.readline().rstrip()
                self.__SetupLock(LineFromFile, LineFromFile2)
                LineFromFile = f.readline().rstrip()
                self.__SetupCardCollectionFromGameFile(LineFromFile,
                                                       self.__Hand)
                LineFromFile = f.readline().rstrip()
                self.__SetupCardCollectionFromGameFile(LineFromFile,
                                                       self.__Sequence)
                LineFromFile = f.readline().rstrip()
                self.__SetupCardCollectionFromGameFile(LineFromFile,
                                                       self.__Discard)
                LineFromFile = f.readline().rstrip()
                self.__SetupCardCollectionFromGameFile(LineFromFile,
                                                       self.__Deck)
                return True
        except:
            print("File not loaded")
            return False

    def __LoadLocks(self):
        FileName = "locks.txt"
        self.__Locks = []
        try:
            with open(FileName) as f:
                LineFromFile = f.readline().rstrip()
                while LineFromFile != "":
                    Challenges = LineFromFile.split(";")
                    LockFromFile = Lock()
                    for C in Challenges:
                        Conditions = C.split(",")
                        LockFromFile.AddChallenge(Conditions)
                    self.__Locks.append(LockFromFile)
                    LineFromFile = f.readline().rstrip()
        except:
            print("File not loaded")

    def __GetRandomLock(self):
        return self.__Locks[random.randint(0, len(self.__Locks) - 1)]

    def __GetCardFromDeck(self, CardChoice):
        if self.__Deck.GetNumberOfCards() > 0:
            if self.__Deck.GetCardDescriptionAt(0) == "Dif":
                print(self.__Deck.DisplayStats())
                CurrentCard = self.__Deck.RemoveCard(
                    self.__Deck.GetCardNumberAt(0))
                print()
                print("Difficulty encountered!")
                print(self.__Hand.GetCardDisplay())
                print("To deal with this you need to either lose a key ",
                      end='')
                Choice = input(
                    "(enter 1-5 to specify position of key) or (D)iscard five cards from the deck:> "
                )
                print()
                self.__Discard.AddCard(CurrentCard)
                CurrentCard.Process(self.__Deck, self.__Discard, self.__Hand,
                                    self.__Sequence, self.__CurrentLock,
                                    Choice, CardChoice)
            elif self.__Deck.GetCardDescriptionAt(0) == "Gen":
                CurrentCard = self.__Deck.RemoveCard(
                    self.__Deck.GetCardNumberAt(0))
                print()
                print("Genius card encountered!")
                if input("Would you like to play the genius card? (y)es or (n)o:> ").lower() == "y":
                    # Get lock details and enumerate challenges for user to input
                    LockDetails = self.__CurrentLock.GetLockDetails(self.__Sequence.GetCardDescriptions()).split('\n')[3:-2:]
                    LockDetails = [f"({i + 1}) {C}" for i, C in enumerate(LockDetails)]
                    print('\n'.join(LockDetails))
                    # Get users Choice of challenge to solve
                    Choice = int(input("Choose which challenge to solve:> "))
                    # Set chosen challenge to solved
                    self.__CurrentLock.SetChallengeMet(Choice - 1, True)

        while self.__Hand.GetNumberOfCards(
        ) < 5 and self.__Deck.GetNumberOfCards() > 0:
            if self.__Deck.GetCardDescriptionAt(0) == "Dif":
                self.__MoveCard(self.__Deck, self.__Discard,
                                self.__Deck.GetCardNumberAt(0))
                print(
                    "A difficulty card was discarded from the deck when refilling the hand."
                )

            if self.__Deck.GetCardDescriptionAt(0) == "Gen":
                self.__MoveCard(self.__Deck, self.__Discard,
                                self.__Deck.GetCardNumberAt(0))
                print(
                    "A Genius card was discarded from the deck when refilling the hand."
                )
            else:
                self.__MoveCard(self.__Deck, self.__Hand,
                                self.__Deck.GetCardNumberAt(0))
        if self.__Deck.GetNumberOfCards(
        ) == 0 and self.__Hand.GetNumberOfCards() < 5:
            self.__GameOver = True

    def __GetCardChoice(self):
        Choice = None
        while Choice is None:
            try:
                Choice = int(
                    input(
                        "Enter a number between 1 and 5 to specify card to use:> "
                    ))
            except:
                pass
        return Choice

    def __GetDiscardOrPlayChoice(self):
        Choice = input("(D)iscard or (P)lay?:> ").upper()
        return Choice

    def __GetChoice(self):
        print()

        choices = "(D)iscard inspect, (U)se card"
        if not self.__PeekUsed:
            choices += ", (P)eek"
        if not self.__MulliganUsed:
            choices += ", (M)ulligan"
        choices += ", (Q)uit:> "

        return input(choices).upper()

    def __AddDifficultyCardsToDeck(self):
        for Count in range(5):
            self.__Deck.AddCard(DifficultyCard())

    def __AddGeniusCardToDeck(self):
        if random.random() < 1.25:
            for x in range(10):
                self.__Deck.AddCard(GeniusCard())

    def __CreateStandardDeck(self):
        for Count in range(5):
            NewCard = ToolCard("P", "a")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("P", "b")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("P", "c")
            self.__Deck.AddCard(NewCard)
        for Count in range(3):
            NewCard = ToolCard("F", "a")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("F", "b")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("F", "c")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("K", "a")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("K", "b")
            self.__Deck.AddCard(NewCard)
            NewCard = ToolCard("K", "c")
            self.__Deck.AddCard(NewCard)
        # Add multi-tools to deck
        for card in ["P", "K", "F"]:
            NewCard = ToolCard(card, "m")
            self.__Deck.AddCard(NewCard)

    def __MoveCard(self, FromCollection, ToCollection, CardNumber):
        Score = 0
        if FromCollection.GetName() == "HAND" and ToCollection.GetName(
        ) == "SEQUENCE":
            CardToMove = FromCollection.RemoveCard(CardNumber)
            if CardToMove is not None:
                ToCollection.AddCard(CardToMove)
                Score = CardToMove.GetScore()
        else:
            CardToMove = FromCollection.RemoveCard(CardNumber)
            if CardToMove is not None:
                ToCollection.AddCard(CardToMove)
        return Score


class Challenge():
    def __init__(self):
        self._Met = False
        self._Condition = []

    def GetMet(self):
        return self._Met

    def GetCondition(self):
        return self._Condition

    def SetMet(self, NewValue):
        self._Met = NewValue

    def SetCondition(self, NewCondition):
        self._Condition = NewCondition


class Lock():
    def __init__(self):
        self._Challenges = []

    def AddChallenge(self, Condition):
        C = Challenge()
        C.SetCondition(Condition)
        self._Challenges.append(C)

    def __ConvertConditionToString(self, C):
        ConditionAsString = ""
        for Pos in range(0, len(C) - 1):
            ConditionAsString += C[Pos] + ", "
        ConditionAsString += C[len(C) - 1]
        return ConditionAsString

    def GetLockDetails(self, Sequence):
        LockDetails = "\n" + "CURRENT LOCK" + "\n" + "------------" + "\n"
        for C in self._Challenges:

            if C.GetMet():
                LockDetails += "Challenge met: "

            elif (len(C.GetCondition()) == 3
                    and len(Sequence) > 1
                    and Sequence[-2::] == C.GetCondition()[:2:]):

                LockDetails += "Partially met: "

            else:
                LockDetails += "Not met:       "

            LockDetails += self.__ConvertConditionToString(
                C.GetCondition()) + "\n"

        LockDetails += "\n"
        return LockDetails

    def GetLockSolved(self):
        for C in self._Challenges:
            if not C.GetMet():
                return False
        return True

    def CheckIfConditionMet(self, Sequence):
        for C in self._Challenges:
            if not C.GetMet() and Sequence == self.__ConvertConditionToString(
                    C.GetCondition()):
                C.SetMet(True)
                return True
        return False

    def SetChallengeMet(self, Pos, Value):
        self._Challenges[Pos].SetMet(Value)

    def GetChallengeMet(self, Pos):
        return self._Challenges[Pos].GetMet()

    def GetNumberOfChallenges(self):
        return len(self._Challenges)


class Card():
    _NextCardNumber = 0

    def __init__(self):
        self._CardNumber = Card._NextCardNumber
        Card._NextCardNumber += 1
        self._Score = 0

    def GetScore(self):
        return self._Score

    def Process(self, Deck, Discard, Hand, Sequence, CurrentLock, Choice,
                CardChoice):
        pass

    def GetCardNumber(self):
        return self._CardNumber

    def GetDescription(self):
        if self._CardNumber < 10:
            return " " + str(self._CardNumber)
        else:
            return str(self._CardNumber)


class ToolCard(Card):
    def __init__(self, *args):
        self._ToolType = args[0]
        self._Kit = args[1]
        if len(args) == 2:
            super(ToolCard, self).__init__()
        elif len(args) == 3:
            self._CardNumber = args[2]
        self.__SetScore()

    def __SetScore(self):
        if self._ToolType == "K":
            self._Score = 3
        elif self._ToolType == "F":
            self._Score = 2
        elif self._ToolType == "P":
            self._Score = 1

    def SetCardToolKit(self, ToolKit):
        self._Kit = ToolKit

    def GetDescription(self):
        return self._ToolType + " " + self._Kit


class DifficultyCard(Card):
    def __init__(self, *args):
        self._CardType = "Dif"
        if len(args) == 0:
            super(DifficultyCard, self).__init__()
        elif len(args) == 1:
            self._CardNumber = args[0]

    def GetDescription(self):
        return self._CardType

    def Process(self, Deck, Discard, Hand, Sequence, CurrentLock, Choice,
                CardChoice):
        ChoiceAsInteger = None
        try:
            ChoiceAsInteger = int(Choice)
        except:
            pass
        if ChoiceAsInteger is not None:
            if ChoiceAsInteger >= 1 and ChoiceAsInteger <= 5:
                if ChoiceAsInteger >= CardChoice:
                    ChoiceAsInteger -= 1
                if ChoiceAsInteger > 0:
                    ChoiceAsInteger -= 1
                if Hand.GetCardDescriptionAt(ChoiceAsInteger)[0] == "K":
                    CardToMove = Hand.RemoveCard(
                        Hand.GetCardNumberAt(ChoiceAsInteger))
                    Discard.AddCard(CardToMove)
                    return
        Count = 0
        while Count < 5 and Deck.GetNumberOfCards() > 0:
            CardToMove = Deck.RemoveCard(Deck.GetCardNumberAt(0))
            Discard.AddCard(CardToMove)
            Count += 1

class GeniusCard(Card):
    def __init__(self, *args):
        self._CardType = "Gen"
        if len(args) == 0:
            super(GeniusCard, self).__init__()
        elif len(args) == 1:
            self._CardNumber = args[0]

    def GetDescription(self):
        return self._CardType

class CardCollection():
    def __init__(self, N):
        self._Name = N
        self._Cards = []

        self._NumPicks = 0
        self._NumFiles = 0
        self._NumKeys = 0

    def SetCardToolKitAt(self, pos, kit):
        self._Cards[pos].SetCardToolKit(kit)

    def GetName(self):
        return self._Name

    def GetCardNumberAt(self, X):
        return self._Cards[X].GetCardNumber()

    def GetCardDescriptionAt(self, X):
        return self._Cards[X].GetDescription()

    def GetCardDescriptions(self): # Had to create for task 8 to achieve partially met
        return [card.GetDescription() for card in self._Cards]

    def AddCard(self, C):
        self._Cards.append(C)

        CardType = C.GetDescription()[0] # Return its type
        if CardType == "K":
            self._NumKeys += 1
        elif CardType == "P":
            self._NumPicks += 1
        elif CardType == "F":
            self._NumFiles += 1

    def GetNumberOfCards(self):
        return len(self._Cards)

    def DisplayStats(self):

        if self._NumPicks != 0:
            percentPick = round((self._NumPicks / self.GetNumberOfCards()) * 100, 2)
        else:
            percentPick = 0
        if self._NumFiles != 0:
            percentFile = round((self._NumFiles / self.GetNumberOfCards()) * 100, 2)
        else:
            percentFile = 0
        if self._NumKeys != 0:
            percentKeys = round((self._NumKeys / self.GetNumberOfCards()) * 100, 2)
        else:
            percentKeys = 0

        print(f"""
There is a {percentKeys}% chance that the next card will be a key,
a {percentFile}% chance it will be a file,
and a {percentPick}% chance it will be a pick.
                """)

    def Shuffle(self):
        for Count in range(10000):
            RNo1 = random.randint(0, len(self._Cards) - 1)
            RNo2 = random.randint(0, len(self._Cards) - 1)
            TempCard = self._Cards[RNo1]
            self._Cards[RNo1] = self._Cards[RNo2]
            self._Cards[RNo2] = TempCard

    def RemoveCard(self, CardNumber):
        CardFound = False
        Pos = 0
        while Pos < len(self._Cards) and not CardFound:
            if self._Cards[Pos].GetCardNumber() == CardNumber:
                CardToGet = self._Cards[Pos]
                CardFound = True
                self._Cards.pop(Pos)
                CardType = CardToGet.GetDescription()[0] # Return its type
                if CardType == "K":
                    self._NumKeys -= 1
                elif CardType == "P":
                    self._NumPicks -= 1
                elif CardType == "F":
                    self._NumFiles -= 1
            Pos += 1


        return CardToGet

    def __CreateLineOfDashes(self, Size):
        LineOfDashes = ""
        for Count in range(Size):
            LineOfDashes += "------"
        return LineOfDashes

    def GetCardDisplay(self):
        CardDisplay = "\n" + self._Name + ":"
        if len(self._Cards) == 0:
            return CardDisplay + " empty" + "\n" + "\n"
        else:
            CardDisplay += "\n" + "\n"
        LineOfDashes = ""
        CARDS_PER_LINE = 10
        if len(self._Cards) > CARDS_PER_LINE:
            LineOfDashes = self.__CreateLineOfDashes(CARDS_PER_LINE)
        else:
            LineOfDashes = self.__CreateLineOfDashes(len(self._Cards))
        CardDisplay += LineOfDashes + "\n"
        Complete = False
        Pos = 0
        while not Complete:
            CardDisplay += "| " + self._Cards[Pos].GetDescription() + " "
            Pos += 1
            if Pos % CARDS_PER_LINE == 0:
                CardDisplay += "|" + "\n" + LineOfDashes + "\n"
            if Pos == len(self._Cards):
                Complete = True
        if len(self._Cards) % CARDS_PER_LINE > 0:
            CardDisplay += "|" + "\n"
            if len(self._Cards) > CARDS_PER_LINE:
                LineOfDashes = self.__CreateLineOfDashes(
                    len(self._Cards) % CARDS_PER_LINE)
            CardDisplay += LineOfDashes + "\n"
        return CardDisplay


if __name__ == "__main__":
    Main()
