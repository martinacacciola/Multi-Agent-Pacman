from captureAgents import CaptureAgent
from util import nearestPoint


class defensiveAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def is_over_half(self, position, gameState):
    """
    Checks if the agent is over the half of the board
    @param position: the position of the agent
    @param gameState: the current game state
    @return: True if the agent is over the half of the board, False otherwise
    """
    food = self.getFood(gameState)
    if self.red:
      if position[0] <= len(food[0])-1:
        return False
      else:
        return True
    else:
      if position[0] >= len(food[0]):
        return False
      else:
        return True

  def chooseAction(self, gameState):
    #python capture.py -r baselineTeam -b myTeam
    #python capture.py -r myTeam -b baselineTeam

    self.distancer.getMazeDistances()

    legal_actions = gameState.getLegalActions(self.index)

    food_locations = self.find_food(gameState)
    opponents_location = self.find_opponents(gameState)
    our_location = self.find_self(gameState)
    
    action = self.best_action(our_location=our_location, food_locations=food_locations, opponents_location=opponents_location, legal_actions=legal_actions, gameState=gameState)

    return action
  
  def find_food(self, gameState):

    """
    Finds the location of all our food pallets in the game
    @param gameState: the current game state
    @return: a list of all the food pallets in the game
    """
    food_locations = []

    food = self.getFoodYouAreDefending(gameState)
    x = 0
    for row in food:
      y = 0
      for cel in row:
        if cel:
          food_locations.append((x, y))
        y += 1
      x += 1
    
    return food_locations
  
  def find_opponents(self, gameState):
    """
    Finds the location of all the opponents in the game
    @param gameState: the current game state
    @return: a list of all the opponents in the game
    """
    opponents = []
    opponent_index = self.getOpponents(gameState)
    for index in opponent_index:
      opponents.append(gameState.getAgentPosition(index))

    return opponents
  
  def find_self(self, gameState):
    """
    Finds the location of our agent in the game
    @param gameState: the current game state
    @return: the location of our agent
    """
    return gameState.getAgentPosition(self.index)
  
  def difference_after_movement(self, pos1, action):
    if action == "North":
      return (pos1[0], pos1[1] + 1)
    elif action == "South":
      return (pos1[0], pos1[1] - 1)
    elif action == "East":
      return (pos1[0] + 1, pos1[1])
    elif action == "West":
      return (pos1[0] - 1, pos1[1])
    else:
      return pos1

  def closest_opponent_to_food(self, food_locations, opponents_location):
    min_distance = float('inf')
    closest_opponent = None
    closes_food = None
    for food_loc in food_locations:
      for opp_loc in opponents_location:
        dist = self.getMazeDistance(food_loc, opp_loc)
        if dist < min_distance:
          min_distance = dist
          closest_opponent = opp_loc
          closest_food = food_loc

    return closest_opponent, closest_food

  def best_action(self, our_location, food_locations, opponents_location, legal_actions, gameState):
    current_best_action = "Stop"
    best_action_value = float('inf')

    for action in legal_actions:
      next_location = self.difference_after_movement(our_location, action)
      closest_opponent, their_closest_food = self.closest_opponent_to_food(food_locations, opponents_location)
      action_value = self.getMazeDistance(next_location, closest_opponent) - 0.2 * self.getMazeDistance(next_location, their_closest_food)

      
      if action_value < best_action_value and self.is_over_half(next_location, gameState) == False:
        best_action_value = action_value
        current_best_action = action
    
    return current_best_action

  
