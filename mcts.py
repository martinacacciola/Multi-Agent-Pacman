from captureAgents import CaptureAgent
from capture import GameState
import random, time, util
from game import Directions
import game
import numpy as np
from util import nearestPoint
import copy

import math
import random
import sys
#python capture.py -r baselineTeam  -b myTeamTry_lorenzo

class Node:
    def __init__(self, gamestate, agent, action, state = None, parent=None, root=False):
        # by default, nodes are initialised as leaves and as non-terminal states
        self.leaf = True
        self.is_terminal = False
        self.successor_is_terminal = False
        self.root = root

        self.gamestate = gamestate.deepCopy()
        self.parent = parent
        self.action = action  # action that led to this state
        self.children = []
        self.agent = agent
        self.index = agent.index
        if state is None:
            self.state = self.gamestate.getAgentPosition(self.index)
        else:
            self.state = state
        self.legalActions = [act for act in gamestate.getLegalActions(agent.index) if act != 'Stop']   # legal actions from this state
        self.unexploredActions = copy.deepcopy(self.legalActions)
        self.visits = 1
        self.total_score = 0
        self.depth = 0 if parent is None else parent.depth + 1
        self.ucb = 0
        
    def is_leaf(self):
        return len(self.children) == 0
    
    # Return True if all actions from the current state have been explored
    def is_fully_expanded(self):
        return len(self.children) == len(self.legalActions)
    
    def add_child(self, child):
        self.children.append(child)
    
    # Select the child with the lowest UCB score
    def select_child(self):
        #exploration_factor = 1.4  # Adjust this parameter as needed
        exploration_factor = self.agent.exploration_factor
        best_child = None
        best_score = float('inf')
        
        for child in self.children:
            # UCB formula
            exploitation = child.total_score / child.visits if child.visits != 0 else 0  
            exploration = math.sqrt(math.log(self.visits) / child.visits) if child.visits != 0 else float('-inf')  
            score = exploitation - exploration * exploration_factor  
            self.ucb = score
            
            if score < best_score:  # Lower score is better because we are trying to minimize the score
                best_score = score
                best_child = child
        
        return best_child
    

    def get_best_action(self): 
        # Select the child with the lowest UCB score and return the action that from the root node led to that child
        best_child = min(self.children, key=lambda x: x.ucb)
        return best_child.action
    
        
    def get_Rewards(self,action=None):
        # Get the reward for the action taken from the current state
        our_location = self.agent.find_self(self.gamestate) 
        successor = self.agent.difference_after_movement(our_location, action)

        capsule_loc = self.agent.getCapsules(self.gamestate)   # Get the location of the power capsule that we want reaching
        capsule_defending = self.agent.getCapsulesYouAreDefending(self.gamestate)   # Get the location of the power capsule that we want to defend
        opponents = self.find_opponents(self.gamestate)   # Get the location of all the opponents in the game
        
        food_list = self.agent.getFood(self.gamestate).asList()   # Get the location of all the food pallets in the game 
        foodLeft = len(food_list)   # Get the number of food pallets left in the game

        distance = self.agent.getMazeDistance(successor, self.gamestate.getInitialAgentPosition(self.index))  # Get the distance to the initial position of the agent
        reward = 0
        # # If the successor is the initial position of the agent
        if successor == self.gamestate.getInitialAgentPosition(self.index) and self.agent.offensive:
            reward = 1000
            return reward
        
        # If the agent is supposed to be offensive
        if self.agent.offensive:
            # If the state of the agent is Pacman
            agent_state = self.gamestate.getAgentState(self.index)
            if agent_state.isPacman:
                
                # If the agent has reached a power capsule located on the enemy field
                if successor in capsule_loc:
                    reward = -1000000
                    self.successor_is_terminal = True
                    return reward
                
                # If there are 18 or fewer food pellets left and the power capsule has been eaten
                if foodLeft <= 18 and capsule_loc == []:  
                    
                    # Get the distance to the power capsule in our field and try to minimize it to come back to our field
                    if not self.agent.red:  
                        bestDist = self.agent.getMazeDistance(our_location, (25,10))   # We are in the blue team
                    else:   
                        bestDist = self.agent.getMazeDistance(our_location, (6,5))   # We are in the red team
                    next = self.gamestate.generateSuccessor(self.index, action)
                    pos2 = next.getAgentPosition(self.index)
                    if not self.agent.red:
                        dist = self.agent.getMazeDistance(pos2, (25,10))   # We are in the blue team
                    else:
                        dist = self.agent.getMazeDistance(pos2, (6,5))   # We are in the red team

                    if dist < bestDist:   # If the distance to the power capsule is less than the best distance
                        reward = -10000000
                    return reward
                
                # If we can catch the food
                if successor in food_list:
                    reward = -500000
                    self.successor_is_terminal = True
                    return reward
            
            # If the offensive agent is still on our side we want to move towards the enemy side
            return - distance
        
        # If the agent is supposed to be defensive
        else:
            # If we are ghost
            agent_state = self.gamestate.getAgentState(self.index)
            if not agent_state.isPacman: 
                opponents = self.find_opponents(self.gamestate)
                
                #If we can eat the opponent
                if successor in opponents:
                    reward = -100000
                    self.successor_is_terminal = True
                    return reward
                
                # If we are moving towards the opponent
                if self.agent.getMazeDistance(successor, opponents[0]) < 3 or self.agent.getMazeDistance(successor, opponents[1]) < 3:
                    reward = -500
                    return reward
                
                reward = - distance  // 3   # We are moving far from the initial position of the agent
                return reward
            
            # If we are on the enemy side as defensive agent we want to come back to our side
            return 3000
        


    def next_is_terminal(self, action=None):
        # Check if the next state is a terminal state
        our_location = self.agent.find_self(self.gamestate)
        successor = self.agent.difference_after_movement(our_location, action)
        opponents = self.find_opponents(self.gamestate)
        capsule_loc = self.agent.getCapsules(self.gamestate)
        foodLeft = len(self.agent.getFood(self.gamestate).asList())

        ## Three cases where the next state is terminal:
        
        # If the agent is ghost and has reached the opponent
        if successor in opponents and not self.agent.offensive:
            self.successor_is_terminal = True
            return True
        # If the agent is Pacman and has reached a power capsule located on the enemy field
        if self.agent.offensive and successor in capsule_loc:
            self.successor_is_terminal = True
            return True
        # If the agent is Pacman and it can return to its field after eating at least 2 food pallets and the power capsule has been eaten
        if self.agent.offensive and foodLeft <= 18 and capsule_loc == []:
            if not self.agent.is_over_half(successor, self.gamestate):
                self.successor_is_terminal = True
                return True
        return False
    
    def find_opponents(self, gameState):
        """
        Finds the location of all the opponents in the game
        @param gameState: the current game state
        @return: a list of all the opponents in the game
        """
        opponents = []
        opponent_index = self.agent.getOpponents(gameState)
        for index in opponent_index:
            opponents.append(gameState.getAgentPosition(index))

        return opponents
    

class MCTSAgent(CaptureAgent):

    def chooseAction(self, gameState, offensive=False, exploration_factor=2.5, num_iterations=10, max_depth=10):

        # The root node of the tree contains the current game state
        root = Node(gameState, agent=self, action = None, state = None, parent=None, root = True)
        self.offensive = offensive   # If the agent is offensive or defensive
        self.exploration_factor = exploration_factor   # The exploration factor for the UCB formula
        self.max_depth = max_depth   # The maximum depth of the tree

        for _ in range(num_iterations):
            
            selected_node = self.select(root)
            expanded_node = self.expand(selected_node)
            # If the successor of the root is terminal, we do not need to simulate because we already found the best action
            if root.successor_is_terminal and expanded_node in root.children:   
                return expanded_node.action
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)
            #print("iteration: {} with total reward: {}".format(_, simulation_result))

        best_action = root.get_best_action()
        #print("best action: {} for agent: {}".format(best_action, self.index))
        return best_action
    
    def select(self, node):
        node_selected = node
        while not node_selected.is_leaf():
            if not node_selected.is_fully_expanded():
                return node_selected
            else:
                node_selected = node_selected.select_child()
        return node_selected
    
    def expand(self, node):
        
        if node.is_terminal:
            return node
        
        actions = node.unexploredActions
        if actions == []:
            return node
        random_action = random.choice(actions)
        node.unexploredActions.remove(random_action)
        our_location = self.find_self(node.gamestate)
        if random_action in node.gamestate.getLegalActions(self.index):   # Check again if the action is legal
            new_state = self.difference_after_movement(our_location, random_action)
            new_gamestate = node.gamestate.generateSuccessor(self.index, random_action)
            if node.next_is_terminal(random_action) and node.root is True:   # Case where the successor of the root is terminal
                child_node = Node(gamestate = new_gamestate, state = new_state, agent = self, action = random_action, parent=node)
                child_node.is_terminal = True
                node.add_child(child_node)
                return child_node
            child_node = Node(gamestate = new_gamestate, state = new_state, agent = self, action = random_action, parent=node)
            node.add_child(child_node)
        else:
            child_node = node
        return child_node
    

    def simulate(self, node):
        current_node = node
        total_reward = 0
        food_left = len(self.getFood(current_node.gamestate).asList())

        # Simulate the game until a terminal state is reached or a maximum depth is reached
        while not current_node.is_terminal and current_node.depth < self.max_depth:

            # We are considering the enemy agent's actions in the simulation
            for index in self.getOpponents(current_node.gamestate):
                opponent_actions = current_node.gamestate.getLegalActions(index)
                opponent_action = random.choice(opponent_actions)
                current_node.gamestate = current_node.gamestate.generateSuccessor(index, opponent_action)

            # We don't the simulation completely random, we want to move towards the opponent or towards the power capsule
            actions = current_node.gamestate.getLegalActions(self.index)
            our_location = self.find_self(current_node.gamestate)  # Get the location of our agent
            capsule_loc = self.getCapsules(current_node.gamestate)
            random_action = random.choice(actions)
            if self.offensive and capsule_loc != []:
                # If we are Pacman and we are not on the enemy side, we want to move towards the enemy side and the power capsule
                best_action = random_action
                successor = self.difference_after_movement(our_location, best_action)
                best_distance = self.getMazeDistance(successor, capsule_loc[0])
                for act in actions:
                    successor = self.difference_after_movement(our_location, act)
                    distance = self.getMazeDistance(successor, capsule_loc[0])
                    if distance < best_distance:
                        best_distance = distance
                        best_action = act
                random_action = best_action
            
            if self.offensive and  capsule_loc == [] and food_left <= 18:
                # If we are Pacman and we are on the enemy side and the power capsule has been eaten, we want to move towards our side with the food pallets
                best_action = random_action
                if self.is_over_half(our_location, current_node.gamestate):
                    if "East" in actions:
                        best_action = "East"
                else:
                    if "West" in actions:
                        best_action = "West"
                random_action = best_action

            if not self.offensive:
                # If we are ghost, we want to move towards one of the opponents
                opponents = current_node.find_opponents(current_node.gamestate)
                best_action = random_action
                successor = self.difference_after_movement(our_location, best_action)
                best_distance = min(self.getMazeDistance(successor, opponents[0]), self.getMazeDistance(successor, opponents[1]))
                for act in actions:
                    successor = self.difference_after_movement(our_location, act)
                    distance = min(self.getMazeDistance(successor, opponents[0]), self.getMazeDistance(successor, opponents[1]))
                    if distance < best_distance:
                        best_distance = distance
                        best_action = act
                random_action = best_action

            # Update total_reward based on the reward obtained from the current action
            reward = current_node.get_Rewards(action=random_action)
            total_reward += reward

            # If the successor of the current node is terminal, we create the terminal node and stop the simulation
            if current_node.successor_is_terminal:
                new_state = self.difference_after_movement(our_location, random_action)
                new_gamestate = current_node.gamestate.generateSuccessor(self.index, random_action)
                current_node = Node(gamestate=new_gamestate, state=new_state, agent=node.agent, action=random_action, parent=current_node)
                current_node.is_terminal = True
                break
            new_state = self.difference_after_movement(our_location, random_action)
            new_gamestate = current_node.gamestate.generateSuccessor(self.index, random_action)
            current_node = Node(gamestate=new_gamestate, state=new_state, agent=node.agent, action=random_action, parent=current_node)

        return total_reward


    def backpropagate(self, node, score):
        # Update the total score and the number of visits of the current node and its ancestors until the root node
        current_node = node 
        while current_node.root is False:
            current_node.visits += 1
            current_node.total_score += score
            current_node = current_node.parent
            
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

    def find_self(self, gameState):
        """
        Finds the location of our agent in the game
        @param gameState: the current game state
        @return: the location of our agent
        """
        return gameState.getAgentPosition(self.index)
       


