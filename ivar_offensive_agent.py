
from captureAgents import CaptureAgent

class offensiveAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
    
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def get_safe_direction(self):

    if self.red:
      return "West"
    else:
      return "East"

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
      if position[0] >= len(food[0])+1:
        return False
      else:
        return True
  
  def chooseAction(self, gameState):
    """
    Chooses the action that get us closer to the food pallets while maximising the distance from the opponents
    If an opponent is too close, we should run away to our side to score the points for foodpallets held
    @param gameState: the current game state
    @return: the action to take
    """
    
    self.distancer.getMazeDistances()

    legal_actions = gameState.getLegalActions(self.index)
    legal_actions.remove("Stop")

    food_locations = self.find_food(gameState)
    opponents_location = self.find_opponents(gameState)
    our_location = self.find_self(gameState)

    action = self.best_action(our_location=our_location, food_locations=food_locations, opponents_location=opponents_location, threshold=5, legal_actions=legal_actions, gameState=gameState)

    return action
  
  def find_food(self, gameState):
    """
    Finds the location of all our food pallets in the game
    @param gameState: the current game state
    @return: a list of all the food pallets in the game
    """
    food_locations = []

    food = self.getFood(gameState)
    x = 0
    for row in food:
      y = 0
      for cel in row:
        if cel:
          food_locations.append((x, y))
        y += 1
      x += 1
    
    return food_locations
  
  def find_food_opponent(self, gameState):
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

  def closest_food_distance(self, our_location, food_locations):
    min_distance = float('inf')
    for food_loc in food_locations:
        dist = self.getMazeDistance(our_location, food_loc)
        if dist < min_distance:
            min_distance = dist
    return min_distance

  def closest_opponent_distance(self, our_location, opponents_location):
    min_distance = float('inf')
    for opp_loc in opponents_location:
        dist = self.getMazeDistance(our_location, opp_loc)
        if dist < min_distance:
            min_distance = dist
    return min_distance

  def food_captured(self, food_locations, opp_food_locations, gameState):
    """
    Finds the minimum number of food pallets captured 
        NOTE: Based on score and remaining food we cannot definitively say how many food pallets we have
        EXAMPLE: 15 food pallets left, opponent has 15 food pallets left, score is 0 --> We don't know if we hold 5 
            food pallets or both teams have delivered 5 food pallets
    @param food_locations: the food pallets we have
    @param opp_food_locations: the food pallets the opponents have
    @param gameState: the current game state
    @return: the minimum number of food pallets captured
    """
    score = self.getScore(gameState)
    min_captured = 20 - score - len(food_locations) + 20 - len(opp_food_locations)
    return min_captured
  
  def will_get_stuck(self, gameState, action, depth, locations=None):
    """
    Checks if a move will get the agent stuck, i.e., if the agent has a minimum of 3 unique locations to move to.
    Uses a set for tracking unique locations to improve performance.
    """
    if locations is None:
        locations = set()


    if depth == 0:
        # Check the number of unique locations directly
        return False
    else:
        state = gameState.generateSuccessor(self.index, action)
        my_location = state.getAgentPosition(self.index)

        new_locations = locations.copy()
        new_locations.add(my_location)

        if len(new_locations) == len(locations):
            # If the set has not grown, we are stuck
            return True

        else:
          next_legal_actions = state.getLegalActions(self.index)
          actions_without_revisiting = []
          for next_action in next_legal_actions:
              if self.will_get_stuck(state, next_action, depth - 1, new_locations):
                continue
              actions_without_revisiting.append(next_action)

          if len(actions_without_revisiting)==0:
            return True
          else:
            return False
          
  def best_action(self, our_location, food_locations, opponents_location, threshold, legal_actions, gameState):
    best_action_value = float(10000)
    current_best_action = "Stop"

    if self.red:
      plus = 1
    else:
      plus = -1

    if self.food_captured(food_locations, self.find_food_opponent(gameState), gameState) >= 5:
      return self.run_away(our_location, opponents_location, legal_actions, gameState)

    elif self.closest_opponent_distance(our_location, opponents_location) < threshold and self.is_over_half(position=(our_location[0]+plus, our_location[1]), gameState=gameState):
      return self.run_away(our_location, opponents_location, legal_actions, gameState)
    
    else:
      for action in legal_actions:
        next_location = self.difference_after_movement(our_location, action)
        closest_food_dist = self.closest_food_distance(next_location, food_locations)
        closest_opponent_dist = self.closest_opponent_distance(next_location, opponents_location)
        action_value = 3*closest_food_dist - closest_opponent_dist

        if action_value < best_action_value:
          best_action_value = action_value
          current_best_action = action

      return current_best_action

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

  def run_away(self, our_location, opponents_location, legal_actions, gameState):
    #python capture.py -r myTeam -b MCTSPacmanAgent_MCTSPacmanAgent
    max_distance = float('-inf')
    best_action = "Stop"
    locations = set() 
    locations.add(our_location)
    for action in legal_actions:
        if self.will_get_stuck(gameState, action, 4, locations):
            continue
        next_location = self.difference_after_movement(our_location, action)
        distance_to_opponents = [self.getMazeDistance(next_location, opp_loc) for opp_loc in opponents_location]
        min_distance = min(distance_to_opponents)
        if min_distance > max_distance or (min_distance >= max_distance and action == self.get_safe_direction()):
            max_distance = min_distance
            best_action = action

    return best_action