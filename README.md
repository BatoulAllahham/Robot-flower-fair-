**Calculating the max load for the robot**

First, we start with max load = 0. Then we use the fact "Initial Need" to get the pavilion need of one colour, like when use write 

InitialNeed(pid="p1", flower="rose", color="red", qty=2)
InitialNeed(pid="p1", flower="rose", color="pink", qty=1)

this means the pavilion with Id = 1 (Rose) need 2 red bouquets and 1 pink bouquet. And the total need is 2+1 = 3.Then we declare a fact 

PavilionTotal(pid="p1", total=4).

and then declare a fact called "NeedCounted", which is a control fact that forbids counting the same need twice.

To count all the needs, we use add_need_to_pavilion_total fact to add a new need to the total need of the pavilion.

When going over many pavilion, if we encounter a totla need higher than the ones we found previousely, we update the max load for the robot using the rule : update_max_load 

If there are no initial need left and the max load is not marked as "ready", then mark it "ready" using the rule : mark_max_load_ready.



Note :
g = cost from the initial state to this state

h = estimated remaining cost to the goal

f = total estimated solution cost through this state

**Movement Logic**
-

Move right : 

the state must not be pruned (for A*), or the goal, and also must be selected (A*).

We check the boundry (the robot should not go out the grid) and check that the current depth can produce a next depth, so we don't exceed the max depth 

and NOT(SearchEdge(parent=MATCH.sid, action="move-right")) forbids generating the same child from the same parent. 

If these rules are true, we move right (add 1 to the cost and add 1 to the Next State Id, which is a counter for the next state).

Same logic is applied to move left, up, down>

**Loading from the Warehouse**
-

Loading is not immediately converted into a child State. First, the system creates a LoadDraft, then it extends that draft if possible, finally, it converts the draft into a real child State with cost +1.
Why ?  because loading several bouquet groups at the warehouse is still one loading operation, so it should cost only 1.

Choosing the first bouquet : 

- seed_same_flower_load :
in this rule, we get the state, check if the robot is in the warehouse,check the max load of the robot, see the remaining needs (all needs here) and seed our first choice and we check if there are no previous identical seed. when these conditions are met, we create a draft loading from the same color, for example; keep loading bouquets with the same flower type, orchid and white.
- seed_same_color_load : follows the same logic of seed_same_flower_load but deals with the colour.

Loading with remaining : when the robot visits the warehouse but it still has some bouquets
-   Load the same flower different colours
The robot is already carrying some bouquets, reaches the warehouse again, and we want to generate a new loading child where it adds more bouquets of the same flower type it is already carrying.
for example : if we have this state : 
                Robot state sid=8 ,Robot position = warehouse ,Current load = 5

    Robot is carrying:orchid white qty=5

    Remaining needs:orchid violet qty=3 orchid red qty=4 tulip white qty=2

    Max load = 12

    the robot can carry violet and red orchid. Then it checks the quantity after adding
    current_load + qty <= max_load,
    5 + 3 <= 12
    If these conditions are met, the robot loads the same flower with different colour.
- Load with the same colour, different types : follows the same logic as the previous one but focuses in different types.

Extending the loading :
- Extend loading the same type with different colour : after choosing the first bouquet, if the draft is a same-flower draft, try to add more bouquets of the same flower type, but with other colours, as long as the robot does not exceed the max load.
- Extending loading the same colour with different type :  after choosing the first bouquet, if the draft is a same-colour draft, try to add more bouquets of the same colour, but with different types , as long as the robot does not exceed the max load.

Finalize loading : 
Before this step all the states were drafted, but with the rule finalize_load_draft, we duplicate the parent state and update the important fields, add the node to the open nodes and record the connection in the search tree. The most important thing, we add 1 to the cost.
After that, the copy_loaded_item_to_child rule transfers each bouquet stored in the draft into Carrying facts belonging to the child state. Together, these rules transform a temporary loading option into an actual searchable state.

**Unloading into Pavilions**
-
- Draft Unloading : This rule starts an unloading draft when the robot reaches a pavilion and has enough bouquets to satisfy one of that pavilion’s needs, the rule checks that the robot carries the same flower type (Carrying Fact).Then it checks that the pavilion still needs the same flower and colour (RemainingNeed), then the quantity (carry_qty >= need_qty). If these conditions are met, then the robot can unload.
- Extend unloading : The extend_unload_draft rule expands an unloading draft after it has been initialized by the seed rule. It searches for additional colors of the same flower type required by the same pavilion. A color can be added only if the robot carries enough quantity to fully satisfy that pavilion need. The rule updates the total unloaded quantity stored in the UnloadDraft fact and creates a new UnloadDraftItem for the added color. The negated UnloadDraftItem condition prevents the same color from being added more than once, while NOT(UnloadDraftApplied(...)) ensures that the draft cannot be changed after it has already been converted into a child state.
- Finalizing the unloading : this rules follows the same logic mentioned in Finalize loading (creates the state, add 1 to the cost, declare an open state and apply the drafts to create the state ).

**Constraint Violation Rules**
-

There are some constraints that are already implemented in the rules. But, there are a bunch of rules dedicated to remove repeated or pruned states.

- mark_states_different_by_missing_candidate_need : marks two states as different if the source state has a remaining need that the candidate does not have.
- mark_states_different_by_extra_candidate_need : marks two states as different if the candidate has an extra remaining need not found in the source.
- mark_states_different_by_missing_candidate_carrying : marks two states as different if the source has carried bouquets not found in the candidate.
- mark_states_different_by_extra_candidate_carrying : marks two states as different if the candidate carries something not found in the source.
- mark_repeated_state_for_pruning : if two states have the same robot position, same load, same remaining needs, and same carrying facts, but one is deeper, the deeper one is marked as PrunedState.
- cascade_pruning_to_child : if a parent is pruned, its generated children are also marked as pruned.
- retract_pruned_state and the other retract_pruned_* rules : to remove pruned states and their related facts from working memory, such as SearchEdge, RemainingNeed, Carrying, OpenState, heuristic facts, drafts, and printed markers.


**Heuristic Calculation**
-
methods are for the pure mathematics.

Rules: collect the values needed by the heuristic from facts.

- ceil_divide : calculates the ceil division because if the robot still needs 15 bouquets and max load is 4, then it needs 4 trips, not 3, we use it in the trips
- trip_based_heuristic : applies this formula  h = d(robot, warehouse) + (trips - 1) * (2 * D_avg + 2) + D_avg + 2

Rules for the heuristic : 
- apply_goal_heuristic :  to handle the goal state where robot load = 0 , there are no RemainingNeed facts for this state ,there are no Carrying facts ,state is open, state is not pruned , heuristic was not already calculated => h = 0 , f = g.
- create_heuristic_remaining_total : it starts calculating the total number of remaining bouquets for a state.if we have RemainingNeed(sid=0, pid=p1, flower=rose, color=red, qty=2); The rule creates: HeuristicNeedTotal(sid=0, total=2) and HeuristicNeedCounted(sid=0, pid=p1, flower=rose, color=red)
    The HeuristicNeedCounted fact is a marker. It means this need was already added to the heuristic total.
- add_remaining_need_to_heuristic_total : after the total is started, this rule adds the rest of the remaining needs. For example : 
    Current : HeuristicNeedTotal(sid=0, total=2)
    Need : RemainingNeed(sid=0, pid=p1, flower=rose, color=pink, qty=1)
    if this need was not counted yet, the rule modifies the total: old total = 2 ,qty = 1 , new total = 3.
    then it declares another HeuristicNeedCounted marker. this repeats through rule activations until all remaining needs for that state are counted
- create_active_pavilion_distance : this rule finds pavilions that still need bouquets, a pavilion is considered active if there is at least one RemainingNeed for it. the rule calculates Manhattan distance from warehouse to that pavilion: distance = |2 - 3| + |4 - 2| = 3.
- create_active_pavilion_summary : this rule starts the summary used to calculate D_avg. if the engine has an active pavilion distance, for example: HeuristicActivePavilionDistance(sid=0, pid=p1, distance=3) and no summary exists yet, it creates:HeuristicPavilionSummary(sid=0,total_distance=3,pavilion_count=1) and HeuristicPavilionCounted(sid=0, pid="p1") which means p1 was already added to the D_avg summary.
- add_active_pavilion_to_summary : this rule adds the other active pavilions to the summary and D_avg = ceil(11 / 4) = 3
- apply_trip_based_heuristic : this is the final heuristic rule. it fires only when the needed summary facts already exist, then the rule updates both the real state and the A* open state, this is important because A* selection only chooses states whose heuristic is ready.



