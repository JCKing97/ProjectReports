"""community_logic.py: the module for functionality surrounding communities: reproduction,
simulation of a whole tournament,setup of a tournament etc."""

import requests
from flask import current_app
from typing import List, Dict
from .generation_logic import Generation
import random


class CommunityCreationException(Exception):
    """Exception generated when failed to create a community"""

    def __init__(self, message):
        super().__init__("Error creating community: " + message)


class Community:
    """A community encompasses a number of generations, a first generation is selected on construction, the next
    generations are then created using a reproduction algorithm"""

    def __init__(self, strategies: List[Dict], num_of_onlookers: int = 5, num_of_generations: int = 10,
                 length_of_generations: int = 30):
        """
        Set the parameters for the community and the initial set of players to simulate the community with
        :param strategies: The initial set of players to simulate the community
        :type strategies: List[Dict]
        :param num_of_onlookers: The number of onlookers for each interaction
        :type num_of_onlookers: int
        :param num_of_generations: The number of generations the simulation will run
        :type num_of_generations: int
        :param length_of_generations: The number of rounds each generation will run for
        :type length_of_generations: int
        """
        self._community_id = requests.request("POST", current_app.config['AGENTS_URL'] + 'community').json()['id']
        if num_of_onlookers <= 0:
            raise CommunityCreationException("number of onlookers <= 0")
        if length_of_generations <= 5:
            raise CommunityCreationException("length of generations <= 5")
        if num_of_generations <= 2:
            raise CommunityCreationException("number of generations <= 2")
        self._num_of_onlookers: int = num_of_onlookers
        self._num_of_generations: int = num_of_generations
        self._length_of_generations: int = length_of_generations
        self._first_strategies = strategies
        self._generations: List[Generation] = []
        self._current_time = 0

    def get_id(self) -> int:
        """
        Get the id of the community
        :return: The id on the community
        :rtype: int
        """
        return self._community_id

    def get_num_of_onlookers(self) -> int:
        """
        Get the number of onlookers for each interaction in this community
        :return: The number of onlooker for each interaction
        :rtype: int
        """
        return self._num_of_onlookers

    def get_length_of_generations(self) -> int:
        """
        Get the number of rounds a generation runs for in this community
        :return: The number of rounds a generation runs for
        :rtype: int
        """
        return self._length_of_generations

    def get_generations(self) -> List[Generation]:
        """
        Get a list of the generations that this community encompasses
        :return: A list of the generations that belong to this community
        :rtype: List[Generation]
        """
        return self._generations

    def simulate(self):
        """
        Simulate the community, building an initial generation simulating that generation and then for the specified
        number of generations reproducing and simulating the next generation
        :return: void
        """
        for i in range(self._num_of_generations):
            generation = self._build_generation()
            generation.simulate()
            self._generations.append(generation)

    def _build_generation(self) -> Generation:
        """
        Build a generation, if is is the first generation use the initial strategies, else reproduce from the old
         generation
        :return: The next generation to simulate
        :rtype: Generation
        """
        if len(self._generations) <= 0:
            return Generation(self._first_strategies, len(self._generations), self._community_id, 0,
                              self._length_of_generations, self._num_of_onlookers)
        else:
            return self._reproduce()

    def _reproduce(self) -> Generation:
        """
        Use the last generation of players to build a new generation of players
        The higher the fitness of an overall strategy in the last generation the more likely that strategy will
        reproduce into the next generation
        :return: The new generation
        :rtype: Generation
        """
        # Gather data on the fitness of strategies
        last_gen_players = self._generations[-1].get_players()
        strategy_fitness: List = []
        overall_fitness = 0
        for player in last_gen_players:
            found_strategy = False
            for strategy in strategy_fitness:
                if strategy['strategy'] == player.get_strategy():
                    found_strategy = True
                    strategy['count'] += player.get_fitness()
            if not found_strategy:
                strategy_fitness.append({'strategy': player.get_strategy(), 'count': player.get_fitness()})
            overall_fitness += player.get_fitness()
        # Build choice intervals to get probability of a new player being a certain strategy
        choice_intervals: List[Dict] = []
        current_interval = 0
        for strategy in strategy_fitness:
            j = current_interval + strategy['count']
            while current_interval <= j:
                choice_intervals.append(strategy['strategy'])
                current_interval += 1
        # Create strategies for players in next generation
        strategies: List[Dict] = []
        for i in range(len(last_gen_players)):
            # Select a strategy for this player
            selected_index = random.randint(0, overall_fitness)
            player_choice: Dict = choice_intervals[selected_index]
            found_strategy = False
            for strategy in strategies:
                if strategy['strategy'] == player_choice:
                    strategy['count'] += 1
                    found_strategy = True
            if not found_strategy:
                strategies.append({'strategy': player_choice, 'count': 1})
        return Generation(strategies, len(self._generations), self._community_id, self._current_time,
                          self._current_time+self._length_of_generations, self._num_of_onlookers)
