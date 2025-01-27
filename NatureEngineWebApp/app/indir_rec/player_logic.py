
from typing import Dict, List, NoReturn
import requests
from .action_logic import Action, InteractionAction, GossipAction, IdleAction, GossipContent, InteractionContent
from .indir_rec_config import Config
from .strategy_logic import Strategy


class PlayerCreationException(Exception):
    """An error has occurred when creating a player"""

    def __init__(self, message):
        super().__init__("Error creating player: " + message)


class DecisionException(Exception):
    """An error has occurred when asking a player for a decision"""

    def __init__(self, message):
        super().__init__("Error getting decision from player: " + message)


class PerceptionException(Exception):
    """An error has occurred when sending a percept to a player"""

    def __init__(self, message):
        super().__init__("Error perceiving: " + message)


class PlayerState:
    """Records the state of the player to observe (new actions, fitness updates, etc.)"""

    def __init__(self, generation: int, player: int, observers: List = None):
        """
        Set up player state changes to a lack of change
        :param generation: the id of the generation the player belongs to
        :type generation: int
        :param player: the id of the player who has this state
        :type player: int
        :param observers: The observers to update when state changes occur
        """
        self._generation = generation
        self._player = player
        self._new_action: Action = None
        self._fitness_update = 0
        self._observers: List = observers if observers is not None else []

    def attach(self, observer) -> NoReturn:
        """
        Attach an observer to notify of state changes
        :param observer: The observer to attach
        :type observer: Observer
        :return: NoReturn
        """
        self._observers.append(observer)

    def detach(self, observer) -> NoReturn:
        """
        Detach an observer from the player state to stop notifying them
        :param observer: The observer to detach
        :type observer: Observer
        :return: NoReturn
        """
        self._observers.remove(observer)

    def _notify(self) -> NoReturn:
        """
        Notify all attached observers that there has been a change of state
        :return: NoReturn
        """
        for observer in self._observers:
            observer.update(self)

    @property
    def generation(self) -> int:
        """
        Get the id of the generation the player whose state this object is belongs to
        :return: the player's generation id
        :rtype: int
        """
        return self._generation

    @property
    def player(self) -> int:
        """
        The id of the player whose state this object tracks
        :return: the id of the player
        :rtype: int
        """
        return self._player

    @property
    def new_action(self) -> Action:
        """
        Get the new action that has been committed by the player, that observers have just been notified of
        :return: The new action
        :rtype: Action
        """
        return self._new_action

    @new_action.setter
    def new_action(self, action: Action) -> NoReturn:
        """
        Set the new action that the player has just decided, and notify all observers of a state change. The once
         notified set the new action to None
        :param action: The action that player has just committed to
        :type action: Action
        :return: NoReturn
        """
        self._new_action = action
        self._notify()
        self._new_action = None

    @property
    def fitness_update(self) -> int:
        """
        Get the latest change in the fitness of the player
        :return: the latest change in the player's fitness
        :rtype: int
        """
        return self._fitness_update

    @fitness_update.setter
    def fitness_update(self, fitness: int) -> NoReturn:
        """
        Set the latest change of the fitness of the player, notify all observers and then set the fitness change to zero
        once it has been read
        :param fitness: The latest fitness change
        :type fitness: int
        :return: NoReturn
        """
        self._fitness_update = fitness
        self._notify()
        self._fitness_update = 0


class Player:
    """The body of a player in the environment"""

    def __init__(self, player_id: int, strategy: Strategy, community_id: int, generation_id: int,
                 observers: List = None):
        """
        Create a player in the environment and their mind in the agent mind service.
        :param player_id: The player's id
        :type player_id: int
        :param strategy: The player's strategy, including the name, options and description
        :type strategy: Dict
        :param community_id: The id of the community this player belongs to
        :type community_id: int
        :param generation_id: The id of the generation this player belongs to
        :type generation_id: int
        """
        # Set up relevant player data
        self._player_id: int = player_id
        self._fitness: int = 0
        self._strategy: Strategy = strategy
        self._community_id: int = community_id
        self._generation_id: int = generation_id
        self._percepts: Dict = {}
        self.player_state = PlayerState(generation_id, player_id, observers)
        # Attempt to create the player in the agents service, if failure raise exception
        try:
            creation_payload: Dict = {"donor_strategy": strategy.donor_strategy,
                                      "non_donor_strategy": strategy.non_donor_strategy,
                                      "trust_model": strategy.trust_model, "options": strategy.options,
                                      "community": community_id, "generation": generation_id, "player": player_id}
            creation_response = requests.request("POST", Config.AGENTS_URL + 'agent',
                                                 json=creation_payload)
            if creation_response.status_code != 200:
                raise PlayerCreationException("bad status code " + str(creation_response.status_code))
            if not creation_response.json()['success']:
                raise PlayerCreationException(creation_response.json()['message'])
        except KeyError:
            raise PlayerCreationException("Incorrect strategy keys")

    @property
    def id(self) -> int:
        """
        Get the id of the player.
        :return: The id of this player
        :rtype: int
        """
        return self._player_id

    @property
    def fitness(self) -> int:
        """
        Get the fitness of the player.
        :return: The fitness of the player
        :rtype: int
        """
        return self._fitness

    def update_fitness(self, change: int) -> NoReturn:
        """
        Update the fitness of the player, it cannot go below zero.
        :param change: The change in fitness to be applied
        :return: void
        """
        start_fitness = self._fitness
        self._fitness += change
        if self._fitness < 0:
            self._fitness = 0
        change = self._fitness - start_fitness
        self.player_state.fitness_update = change

    @property
    def strategy(self) -> Strategy:
        """
        Get the strategy (name, description and options) of this player
        :return: the strategy of this player
        :rtype: Strategy
        """
        return self._strategy

    def decide(self, timepoint: int) -> Action:
        """
        Get the agents decision on an action to commit to in a certain turn.
        :param timepoint: The timepoint at which the agent is deciding
        :type timepoint: int
        :return: A dictionary representation of the data of the action the player has decided on
        :rtype: Dict
        """
        # Request a decision from the agents mind
        action_payload: Dict = {"timepoint": timepoint, "community": self._community_id,
                                "generation": self._generation_id, "player": self._player_id}
        action_response = requests.request("GET", Config.AGENTS_URL + 'action',
                                           params=action_payload)
        # Check if decision failed, throw exception if so
        if action_response.status_code != 200:
            raise DecisionException("bad status code " + action_response.status_code)
        if not action_response.json()['success']:
            raise DecisionException(action_response.json()['message'])
        # Create a representation of the action for the environment to use
        action_representation = action_response.json()['action']
        if action_representation['type'] == "gossip":
            gossip: GossipContent = GossipContent.POSITIVE if action_representation['value'] == 'positive'\
                else GossipContent.NEGATIVE
            action: GossipAction = GossipAction(timepoint, self.id, self._generation_id,
                                                action_representation["reason"], action_representation['about'],
                                                action_representation['recipient'], gossip)
        elif action_representation['type'] == "action":
            action_content: InteractionContent = InteractionContent.COOPERATE if \
                action_representation['value'] == 'cooperate' else InteractionContent.DEFECT
            action: InteractionAction = InteractionAction(timepoint, self.id, self._generation_id,
                                                          action_representation["reason"],
                                                          action_representation['recipient'], action_content)
        elif action_representation['type'] == 'idle':
            action: IdleAction = IdleAction(timepoint, self.id, self._generation_id, action_representation["reason"])
        else:
            raise DecisionException("Action did not match idle, gossip or action")
        # Update the player state with a new action
        self.player_state.new_action = action
        return action

    def set_perception(self, perception) -> NoReturn:
        """
        Set a perception into the player's perception bank, ready to be perceived
        :param perception: The perception to set into the player's perception bank
        :return: NoReturn
        """
        if perception['timepoint'] not in self._percepts.keys():
            self._percepts[perception['timepoint']] = [perception]
        else:
            self._percepts[perception['timepoint']].append(perception)

    def perceive(self, timepoint: int) -> NoReturn:
        """
        Tell the agent to perceive the percepts set for the previous timepoint from this one
        :param timepoint: The timepoint we are currently at so is one in front of the percepts to perceive
        :type timepoint: int
        :return: NoReturn
        """
        if timepoint > 0 and timepoint-1 in self._percepts:
            # Send all percepts for the relevant timepoint to the agents mind
            percept_dict = {'percepts': self._percepts[timepoint-1]}
            percept_response = requests.request("POST", Config.AGENTS_URL + 'percept/action/group',
                                                json=percept_dict)
            if percept_response.status_code != 200:
                raise PerceptionException("Failed to send percept bad status code: " +
                                          str(percept_response.status_code))
            for success_response in percept_response.json()['success']:
                if not success_response['success']:
                    raise PerceptionException(success_response['success'])
