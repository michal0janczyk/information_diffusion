from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import skfuzzy
import skfuzzy.control as ctrl

class FuzzyModule:
    def __init__ (self, followersStart=0, followersStop=10, tweetTextStart=1, tweetTextStop=280, popularityStart=0, popularityStop=1000):
        self.__followersStart = followersStart
        self.__followersStop = followersStop
        self.__tweetTextStart = tweetTextStart
        self.__tweetTextStop = tweetTextStop
        self.__popularityStart = popularityStart
        self.__popularityStop = popularityStop

    def setFollowersLowStart(self, start):
        self.__followersLowStart = start

    def setFollowersLowMid(self, mid):
        self.__followersLowMid = mid

    def setFollowersLowStop(self, stop):
        self.__followersLowStop = stop

    def setFollowersModStart(self, start):
        self.__followersModStart = start

    def setFollowersModMid(self, mid):
        self.__followersModMid = mid

    def setFollowersModStop (self, stop):
        self.__followersModStop = stop

    def setFollowersHighStart(self, start):
        self.__followersHighStart = start

    def setFollowersHighMid(self, mid):
        self.__followersHighMid = mid

    def setFollowersHighStop(self, stop):
        self.__followersHighStop = stop

    def setFollowersLow(self, start, mid, stop):
        self.setFollowersLowStart(start)
        self.setFollowersLowMid(mid)
        self.setFollowersLowStop(stop)

    def setFollowersMod(self, start, mid, stop):
        self.setFollowersModStart(start)
        self.setFollowersModMid(mid)
        self.setFollowersModStop(stop)

    def setFollowersHigh(self, start, mid, stop):
        self.setFollowersHighStart(start)
        self.setFollowersHighMid(mid)
        self.setFollowersHighStop(stop)

    def setFollowers(self, lowStart, lowMid, lowStop, modStart, modMid, modStop, highStart, highMid, highStop):
        self.setFollowersLow(lowStart, lowMid, lowStop)
        self.setFollowersMod(modStart, modMid, modStop)
        self.setFollowersHigh(highStart, highMid, highStop)

    def setTweetTextLowStart(self, start):
        self.__tweetTextLowStart = start

    def setTweetTextLowMid(self, mid):
        self.__tweetTextLowMid = mid

    def setTweetTextLowStop(self, stop):
        self.__tweetTextLowStop = stop

    def setTweetTextModStart(self, start):
        self.__tweetTextModStart = start

    def setTweetTextModMid(self, mid):
        self.__tweetTextModMid = mid

    def setTweetTextModStop(self, stop):
        self.__tweetTextModStop = stop

    def setTweetTextHighStart(self, start):
        self.__tweetTextHighStart = start

    def setTweetTextHighMid(self, mid):
        self.__tweetTextHighMid = mid

    def setTweetTextHighStop(self, stop):
        self.__tweetTextHighStop = stop

    def setTweetTextLow(self, start, mid, stop):
        self.setTweetTextLowStart(start)
        self.setTweetTextLowMid(mid)
        self.setTweetTextLowStop(stop)

    def setTweetTextMod(self, start, mid, stop):
        self.setTweetTextModStart(start)
        self.setTweetTextModMid(mid)
        self.setTweetTextModStop(stop)

    def setTweetTextStop(self, start, mid, stop):
        self.setTweetTextHighStart(start)
        self.setTweetTextHighMid(mid)
        self.setTweetTextHighStop(stop)

    def setTweetText(self, lowStart, lowMid, lowStop, modStart, modMid, modStop, highStart, highMid, highStop):
        self.setTweetTextLow(lowStart, lowMid, lowStop)
        self.setTweetTextMod(modStart, modMid, modStop)
        self.setTweetTextStop(highStart, highMid, highStop)

    def setPopularityLowStart(self, start):
        self.__popularityLowStart = start

    def setPopularityLowMid(self, mid):
        self.__popularityLowMid = mid

    def setPopularityLowStop(self, stop):
        self.__popularityLowStop = stop

    def setPopularityModStart(self, start):
        self.__popularityModStart = start

    def setPopularityModMid(self, mid):
        self.__popularityModMid = mid

    def setPopularityModStop(self, stop):
        self.__popularityModStop = stop

    def setPopularityHighStart(self, start):
        self.__popularityHighStart = start

    def setPopularityHighMid(self, mid):
        self.__popularityHighMid = mid

    def setPopularityHighStop(self, stop):
        self.__popularityHighStop = stop

    def unPopular(self, start, mid, stop):
        self.setPopularityLowStart(start)
        self.setPopularityLowMid(mid)
        self.setPopularityLowStop(stop)

    def midPopular(self, start, mid, stop):
        self.setPopularityModStart(start)
        self.setPopularityModMid(mid)
        self.setPopularityModStop(stop)

    def veryPopular(self, start, mid, stop):
        self.setPopularityHighStart(start)
        self.setPopularityHighMid(mid)
        self.setPopularityHighStop(stop)

    def setPopularity(self, lowStart, lowMid, lowStop, modStart, modMid, modStop, highStart, highMid, highStop):
        self.unPopular(lowStart, lowMid, lowStop)
        self.midPopular(modStart, modMid, modStop)
        self.veryPopular(highStart, highMid, highStop)

    def makeVariables (self):
        """
            step 1: create input, output variables
        :return:
        """
        self.__followers = ctrl.Antecedent(np.arange(self.__followersStart, self.__followersStop), "FOLLOWERS")
        self.__tweetText = ctrl.Antecedent(np.arange(self.__tweetTextStart, self.__tweetTextStop), "TWEETTEXT")
        self.__popularity = ctrl.Consequent(np.arange(self.__popularityStart, self.__popularityStop), "POPULARITY")

    def makeMemberFunctions (self):
        """
            step 2: create member functions
        :return:
        """
        self.__followers["small"] = skfuzzy.trimf( self.__followers.universe,
                                                 [self.__followersLowStart, self.__followersLowMid,
                                                  self.__followersLowStop] )
        self.__followers["medium"] = skfuzzy.trimf( self.__followers.universe,
                                                      [self.__followersModStart, self.__followersModMid,
                                                       self.__followersModStop] )
        self.__followers['high'] = skfuzzy.trimf( self.__followers.universe,
                                                  [self.__followersHighStart, self.__followersHighMid,
                                                   self.__followersHighStop] )

        self.__tweetText["small"] = skfuzzy.trimf( self.__tweetText.universe,
                                                   [self.__tweetTextLowStart, self.__tweetTextLowMid,
                                                    self.__tweetTextLowStop] )
        self.__tweetText['medium'] = skfuzzy.trimf( self.__tweetText.universe,
                                                    [self.__tweetTextModStart, self.__tweetTextModMid,
                                                     self.__tweetTextModStop] )
        self.__tweetText['high'] = skfuzzy.trimf( self.__tweetText.universe,
                                                  [self.__tweetTextHighStart, self.__tweetTextHighMid,
                                                   self.__tweetTextHighStop] )

        self.__popularity["small"] = skfuzzy.trimf(self.__popularity.universe,
                                                   [self.__popularityLowStart, self.__popularityLowMid,
                                                    self.__popularityLowStop])
        self.__popularity["medium"] = skfuzzy.trimf( self.__popularity.universe,
                                                    [self.__popularityModStart, self.__popularityModMid,
                                                     self.__popularityModStop])
        self.__popularity["high"] = skfuzzy.trimf( self.__popularity.universe,
                                                    [self.__popularityHighStart, self.__popularityHighMid,
                                                     self.__popularityHighStop])

    def makeRules(self):
        """
            step 3: create fuzzy rules
        :return:
        """
        rule1 = ctrl.Rule( self.__followers["small"] & self.__tweetText["small"], self.__popularity["small"])
        rule2 = ctrl.Rule( self.__followers["small"] & self.__tweetText["medium"], self.__popularity["small"])
        rule3 = ctrl.Rule( self.__followers["small"] & self.__tweetText["high"], self.__popularity["medium"])

        rule4 = ctrl.Rule( self.__followers["medium"] & self.__tweetText["small"], self.__popularity["small"])
        rule5 = ctrl.Rule( self.__followers["medium"] & self.__tweetText["medium"], self.__popularity["medium"])
        rule6 = ctrl.Rule( self.__followers["medium"] & self.__tweetText["high"], self.__popularity["medium"] )

        rule7 = ctrl.Rule( self.__followers["high"] & self.__tweetText["small"], self.__popularity["high"])
        rule8 = ctrl.Rule( self.__followers["high"] & self.__tweetText["medium"], self.__popularity["high"])
        rule9 = ctrl.Rule( self.__followers["high"] & self.__tweetText["high"], self.__popularity["high"])

        """
            step 4: create a control system
        """
        self.__rules = []
        for i in range(1, 10):
            self.__rules.append(eval("rule" + str(i)))

        self.__popularityCtrl = ctrl.ControlSystem(self.__rules)
        self.__popularityCtrl.view()


    def simulate(self, followersVal, tweetTextLong):
        """
        :param followersVal: number of followers
        :param tweetTextLong: number of signs in text message
        :return: res: a string store step by step instructions how the fuzzy controler infer
        res is stored in result.txt
        """
        popularityCtrlSil = ctrl.ControlSystemSimulation( self.__popularityCtrl )
        popularityCtrlSil.input["FOLLOWERS"] = followersVal
        popularityCtrlSil.input["TWEETTEXT"] = tweetTextLong
        popularityCtrlSil.compute()

        self.result = popularityCtrlSil.print_state()
        self.output = popularityCtrlSil.output.items()[0][1]

        # def getResult():
        #     outputFile = open("result.txt", "r")
        #     return outputFile.read()
        #
        # getResult()
        print(popularityCtrlSil.output)
        print(self.result)

def main():
    fuzzyModule = FuzzyModule(0, 35, 10, 50)
    fuzzyModule.setFollowers(0,  10, 50,  10,  50,  100, 50,  100, 250)
    fuzzyModule.setTweetText(10, 50, 100, 100, 150, 200, 150, 200, 240)
    fuzzyModule.setPopularity(10, 20, 30, 40,  50,  60,  70,  80, 90)

    fuzzyModule.makeVariables()
    fuzzyModule.makeMemberFunctions()
    fuzzyModule.makeRules()

    fuzzyModule.simulate(50, 240)

if __name__ == '__main__':
    main()