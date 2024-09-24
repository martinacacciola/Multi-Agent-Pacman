
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState
from util import nearestPoint
from mcts import Node
from mcts import MCTSAgent
from ivar_offensive_agent import offensiveAgent


def createTeam(firstIndex, secondIndex, isRed,
               first = 'MCTSPacmanAgent', second = 'play_offensiveAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

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
        best_action = MCTSAgent.chooseAction(self, gameState)
        return best_action
    
class play_offensiveAgent(offensiveAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
    
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    gameState = GameState.deepCopy(self=gameState)
    best_action = offensiveAgent.chooseAction(self, gameState)
    return best_action