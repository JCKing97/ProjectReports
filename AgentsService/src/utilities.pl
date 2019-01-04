/** <module> This file handles utility predicates for the service
 * @author James King
 */

/**
 * random_element(+List:list, -Elem:elem) is nondet
 *
 * Get a random element from the list, this element unifies with Elem.
 *
 * @arg List The list to get a random element from
 * @arg Elem The random element
 */
 
random_element(List, Elem):-
	length(List, Length),
	((Length @=< 0) -> fail ;
	(MaxIndex is Length-1,
	random_between(0, MaxIndex, Index),
	nth0(Index, List, Elem))).

/**
 * is_empty(+List:list, -IsIt:bool) is nondet
 *
 * Is the list input empty?
 * @arg List The list to check for emptiness
 * @arg IsIt Whether the list is empty or not
 */

is_empty(List, IsIt):-
	length(List, Length),
	((Length @=< 0) -> 
		IsIt = true ;
		IsIt = false
	).