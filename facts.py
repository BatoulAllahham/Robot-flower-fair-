from experta import Fact, Field


class Grid(Fact):
    width = Field(int, mandatory=True)
    height = Field(int, mandatory=True)

class Warehouse(Fact):
    x = Field(int, mandatory=True)
    y = Field(int, mandatory=True)

class FlowerType(Fact):
    name = Field(str, mandatory=True)

class BouquetColor(Fact):
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)

class Pavilion(Fact):
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    x = Field(int, mandatory=True)
    y = Field(int, mandatory=True)

class InitialNeed(Fact):
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    qty = Field(int, mandatory=True)

class PavilionTotal(Fact):
    pid = Field(str, mandatory=True)
    total = Field(int, mandatory=True)

class NeedCounted(Fact):      #like a boolean value to prevent counting the same need
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)

class MaxLoad(Fact):
    value = Field(int, mandatory=True)

class MaxLoadReady(Fact):
    status = Field(str, mandatory=True)

class DepthLimit(Fact):
    value = Field(int, mandatory=True)

class DepthStep(Fact):          #to ceck if we can move one step without exceeding the max depth
    depth_key = Field(int, mandatory=True)
    next_depth_key = Field(int, mandatory=True)

class NextStateId(Fact):           #like a counter that refers to the next state
    value = Field(int, mandatory=True)

class NextDraftId(Fact):
    value = Field(int, mandatory=True)
class NextUnloadDraftId(Fact):
    value = Field(int, mandatory=True)
class State(Fact):

    sid = Field(int, mandatory=True)
    parent = Field(object, mandatory=True)
    action = Field(str, mandatory=True)
    robot_x = Field(int, mandatory=True)
    robot_y = Field(int, mandatory=True)
    load = Field(int, mandatory=True)
    depth_key = Field(int, mandatory=True)
    g = Field(int, mandatory=True)
    h = Field(int, mandatory=True)
    f = Field(int, mandatory=True)

class RemainingNeed(Fact):
    sid = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    qty = Field(int, mandatory=True)

class Carrying(Fact):
    sid = Field(int, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    qty = Field(int, mandatory=True)

class SearchEdge(Fact):
    parent = Field(int, mandatory=True)
    child = Field(int, mandatory=True)
    action = Field(str, mandatory=True)
    cost = Field(int, mandatory=True)







class PathText(Fact):
    sid = Field(int, mandatory=True)
    path = Field(str, mandatory=True)

class StatePrinted(Fact):
    sid = Field(int, mandatory=True)

class Goal(Fact):
    sid = Field(int, mandatory=True)

class SolutionPrinted(Fact):
    sid = Field(int, mandatory=True)

class SearchFinished(Fact):
    # A* control fact: first selected goal was printed, so search can stop.
    status = Field(str, mandatory=True)

class OpenState(Fact):
    # A* frontier fact: state is discovered but not expanded yet.
    sid = Field(int, mandatory=True)
    g = Field(int, mandatory=True)
    h = Field(int, mandatory=True)
    f = Field(int, mandatory=True)

class SelectedState(Fact):
    sid = Field(int, mandatory=True)

class ClosedState(Fact):
    sid = Field(int, mandatory=True)

class HeuristicCandidate(Fact):
    # A* heuristic fact: one possible Manhattan-distance estimate for a state.
    sid = Field(int, mandatory=True)
    value = Field(int, mandatory=True)
    source = Field(str, mandatory=True)

class HeuristicReady(Fact):
    sid = Field(int, mandatory=True)

class SmallerHeuristic(Fact):
    # A* helper fact , this heuristic candidate is not the smallest one.
    sid = Field(int, mandatory=True)
    value = Field(int, mandatory=True)

class BetterOpenState(Fact):
    # A* helper fact , an open state has another open state with a smaller f.
    candidate_sid = Field(int, mandatory=True)
    better_sid = Field(int, mandatory=True)

class HeuristicNeedTotal(Fact):
    sid = Field(int, mandatory=True)
    total = Field(int, mandatory=True)

class HeuristicNeedCounted(Fact):
    sid = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)

class HeuristicActivePavilionDistance(Fact):
    sid = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    distance = Field(int, mandatory=True)

class HeuristicPavilionSummary(Fact):
    # A* helper fact, sum and count used to calculate D_avg.
    sid = Field(int, mandatory=True)
    total_distance = Field(int, mandatory=True)
    pavilion_count = Field(int, mandatory=True)

class HeuristicPavilionCounted(Fact):
    # A* helper fact, prevents adding the same active pavilion twice to D_avg.
    sid = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)

class StatesDifferent(Fact):
    source_sid = Field(int, mandatory=True)
    candidate_sid = Field(int, mandatory=True)

class PrunedState(Fact):
    sid = Field(int, mandatory=True)


class LoadDraft(Fact):  #like a boolean value to prevent loading the same draft
    parent_sid = Field(int, mandatory=True)
    draft_id = Field(int, mandatory=True)
    mode = Field(str, mandatory=True)
    seed_flower = Field(str, mandatory=True)
    seed_color = Field(str, mandatory=True)
    load = Field(int, mandatory=True)

class LoadDraftItem(Fact):
    draft_id = Field(int, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    qty = Field(int, mandatory=True)

class LoadSeeded(Fact):
    parent_sid = Field(int, mandatory=True)
    mode = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)

class LoadDraftApplied(Fact):
    draft_id = Field(int, mandatory=True)
    child_sid = Field(int, mandatory=True)

class UnloadDraft(Fact):
    parent_sid = Field(int, mandatory=True)
    draft_id = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    unload = Field(int, mandatory=True)

class UnloadDraftItem(Fact):
    draft_id = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    qty = Field(int, mandatory=True)

class UnloadSeeded(Fact):
    parent_sid = Field(int, mandatory=True)
    pid = Field(str, mandatory=True)
    flower = Field(str, mandatory=True)
    color = Field(str, mandatory=True)

class UnloadChild(Fact):
    parent_sid = Field(int, mandatory=True)
    child_sid = Field(int, mandatory=True)
    draft_id = Field(int, mandatory=True)

class UnloadDraftApplied(Fact):
    draft_id = Field(int, mandatory=True)
    child_sid = Field(int, mandatory=True)
