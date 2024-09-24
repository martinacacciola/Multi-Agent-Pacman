from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState
from util import nearestPoint
from ivar_defensive_agent import defensiveAgent
from ivar_def_reflex_agent import DefensiveReflexAgent
from mcts import Node
from mcts import MCTSAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'play_defensiveAgent', second = 'defensive_ReflexAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class play_defensiveAgent(defensiveAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
     gameState = GameState.deepCopy(self=gameState)
     best_action = defensiveAgent.chooseAction(self, gameState)
     return best_action


class defensive_ReflexAgent(DefensiveReflexAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    gameState = GameState.deepCopy(self=gameState)
    best_action = DefensiveReflexAgent.chooseAction(self, gameState)
    return best_action