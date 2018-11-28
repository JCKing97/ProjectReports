/*--------------------------------------
Author:		James King
Title:		strategies.pl
Created:	4th Nov 2018
Desc:		Contains the logic related to querying agents beliefs
--------------------------------------*/

% Get the value of a belief at a given timepoint

/*-------------------------
------ Donor Beliefs ------
-------------------------*/

% When did this agent last believe they were a donor?
get_donor_belief(CommunityID, GenerationID, AgentID, Timepoint, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	findall(interaction{'timepoints': InteractionTimepoints, 'recipient': RecipientID},
		holds_at(interaction_timepoints(agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID), 
			agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), RecipientID))=InteractionTimepoints, Timepoint+1), 
		Value),
	Success = true, !.
% When agent has no belief about it's last donor timepoint
get_donor_belief(CommunityID, GenerationID, AgentID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	Success = true, Value = [].
% Fail nicely when no such community
get_donor_belief(CommunityID, _, _, _, Success, Value):-
	\+community(CommunityID),
	Success = 'No such community',
	Value = [].
% Fail nicely when no such generation for this community
get_donor_belief(CommunityID, GenerationID, _, _, Success, Value):-
	community(CommunityID),
	\+generation(community(CommunityID), GenerationID),
	Success = 'No such generation for this community',
	Value = [].
% Fail nicely when no such agent for the donor
get_donor_belief(CommunityID, GenerationID, AgentID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	Success = 'No such agent in this generation and community',
	Value = [].



/*-----------------------------
------ Recipient Beliefs ------
-----------------------------*/

% When did this agent last believe they were a recipient
get_recipient_belief(CommunityID, GenerationID, AgentID, Timepoint, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	findall(interaction{'timepoints': InteractionTimepoints, 'donor': DonorID},
		holds_at(interaction_timepoints(agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), DonorID), 
			agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID))=InteractionTimepoints, Timepoint+1), 
		Value),
	Success = true, !.
% When agent has no belief about it's last recipient timepoint
get_recipient_belief(CommunityID, GenerationID, AgentID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	Success = true, Value = [].
% fail nicely when there is no community
get_recipient_belief(CommunityID, _, _, _,  Success, Value):-
	\+community(CommunityID),
	Success = 'No such community',
	Value = [].
% Fail nicely when no such generation for this community
get_recipient_belief(CommunityID, GenerationID, _, _,  Success, Value):-
	community(CommunityID),
	\+generation(community(CommunityID), GenerationID),
	Success = 'No such generation for this community',
	Value = [].
% Fail nicely when no such agent for the recipient
get_recipient_belief(CommunityID, GenerationID, AgentID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AgentID),
	Success = 'No such agent in this generation and community',
	Value = [].

/*-------------------------------
------ Interaction Beliefs ------
-------------------------------*/

% When did these agents last believe they were part of an interaction together?
get_interaction_belief(CommunityID, GenerationID, Timepoint, Agent1ID, Agent2ID, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent1ID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent2ID),
	findall(interaction{'timepoints': InteractionTimepoints, 'donor': Agent1ID, 'recipient': Agent2ID},
		holds_at(interaction_timepoints(agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent1ID),
			agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent2ID))=InteractionTimepoints, Timepoint+1),
		Interactions1),
	findall(interaction{'timepoints': InteractionTimepoints, 'donor': Agent2ID, 'recipient': Agent1ID},
		holds_at(interaction_timepoints(agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent2ID),
			agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent1ID))=InteractionTimepoints, Timepoint+1),
		Interactions2),
	append(Interactions1, Interactions2, Value),
	Success = true, !.
% Fail nicely when there is no such community
get_interaction_belief(CommunityID, _, _, _, _, Success, Value):-
	\+community(CommunityID),
	Success = 'No such community',
	Value = [].
% Fail nicely when no such generation for this community
get_interaction_belief(CommunityID, GenerationID, _, _, _, Success, Value):-
	community(CommunityID),
	\+generation(community(CommunityID), GenerationID),
	Success = 'No such generation for this community',
	Value = [].
% Fail nicely when no such agent for both agents
get_interaction_belief(CommunityID, GenerationID, _, Agent1ID, Agent2ID, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent1ID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent2ID),
	Success = 'No such agents for this generation and community',
	Value = [].
% Fail nicely when no such agent for player1
get_interaction_belief(CommunityID, GenerationID, _, Agent1ID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent1ID),
	Success = 'No such agent for player1 for this generation and community',
	Value = [].
% Fail nicely when no such agent for player2
get_interaction_belief(CommunityID, GenerationID, _, _, Agent2ID, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), Agent2ID),
	Success = 'No such agent for player2 for this generation and community',
	Value = [].

/*----------------------------
------ Standing Beliefs ------
----------------------------*/

% What did the perceiver believe about the standing of this other agent?
get_standing_belief(CommunityID, GenerationID, Timepoint, PerceiverID, AboutID, Success, Value):-
	agent(strategy("Standing Discriminator", StratDesc, StratOptions), community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
	agent(Strat, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID),
	holds_at(standing(agent(strategy("Standing Discriminator", StratDesc, StratOptions), community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
		agent(Strat, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID))=Value, Timepoint+1),
	Success = true, !.
% If there is no holds_at value but the perceiver uses the standing strategy they will autobelieve them to be of a good standing
get_standing_belief(CommunityID, GenerationID, _, PerceiverID, AboutID, Success, Value):-
	agent(strategy("Standing Discriminator", _, _), community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID),
	Success = true, Value=good, !.
% Fail nicely if the perceiver is not using the standing strategy
get_standing_belief(CommunityID, GenerationID, _, PerceiverID, AboutID, Success, Value):-
	agent(strategy(StrategyName, _, _), community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
	agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID),
	StrategyName \== "Standing Discriminator",
	Success = 'The perceiver is not using the standing strategy so has no beliefs on other players standings', Value=false, !.
% Fail nicely if there is no such community
get_standing_belief(CommunityID, _, _, _, _, Success, Value):-
	\+community(CommunityID),
	Success = 'No such community',
	Value= false.
% Fail nicely is no such generation for this community
get_standing_belief(CommunityID, GenerationID, _, _, _, Success, Value):-
	community(CommunityID),
	\+generation(community(CommunityID), GenerationID),
	Success='No such generation for this community',
	Value=false.
% Fail nicely if no such agent as perceiver or about
get_standing_belief(CommunityID, GenerationID, _, PerceiverID, AboutID, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID),
	Success = 'No such agent as perceiver or about for this generation of this community',
	Value=false.
% Fails nicely if no such agent as perceiver
get_standing_belief(CommunityID, GenerationID, _, PerceiverID, _, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), PerceiverID),
	Success='No such agent as perceiver for this generation of this community',
	Value=false.
% Fail nicely if no such agent as about
get_standing_belief(CommunityID, GenerationID, _, _, AboutID, Success, Value):-
	community(CommunityID),
	generation(community(CommunityID), GenerationID),
	\+agent(_, community(CommunityID), generation(community(CommunityID), GenerationID), AboutID),
	Success = 'No such agent as about for this generation of this community',
	Value=false.
