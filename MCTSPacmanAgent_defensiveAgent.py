from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState
from util import nearestPoint
from ivar_defensive_agent import defensiveAgent
from mcts import Node
from mcts import MCTSAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'MCTSPacmanAgent', second = 'play_defensiveAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class MCTSPacmanAgent(MCTSAgent):
    """
    A Pacman agent that uses Monte Carlo Tree Search (MCTS) to make decisions.
    """
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)


    def chooseAction(self, gameState):
        """
        Choose an action using MCTS.
        """
        gameState = GameState.deepCopy(self=gameState)
        best_action = MCTSAgent.chooseAction(self, gameState, offensive=True)
        return best_action
    
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
  