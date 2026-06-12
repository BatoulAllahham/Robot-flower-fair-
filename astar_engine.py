from experta import AS, KnowledgeEngine, MATCH, NOT, Rule, TEST

from facts import (BetterOpenState, Carrying, ClosedState, DepthStep, Goal, Grid, HeuristicActivePavilionDistance,
                   HeuristicCandidate, HeuristicNeedCounted, HeuristicNeedTotal, HeuristicPavilionCounted,
                   HeuristicPavilionSummary, HeuristicReady, InitialNeed,
                   LoadDraft, LoadDraftApplied, LoadDraftItem, LoadSeeded, MaxLoad, MaxLoadReady, NeedCounted,
                   NextDraftId,
                   NextStateId, NextUnloadDraftId, OpenState, PathText, Pavilion, PavilionTotal, PrunedState,
                   RemainingNeed,
                   SearchEdge, SearchFinished, SelectedState, SmallerHeuristic, SolutionPrinted, State, StatePrinted,
                   StatesDifferent, UnloadChild, UnloadDraft,
                   UnloadDraftApplied, UnloadDraftItem, UnloadSeeded, Warehouse, )


class FlowerDeliveryEngineWithAStar(KnowledgeEngine):
    def ceil_divide(self, numerator, denominator):
        return -(-numerator // denominator)

    def trip_based_heuristic(self, x, y, wx, wy, remaining_total, max_load, total_distance, pavilion_count):
        # h = d(robot, warehouse) + (trips - 1) * (2 * D_avg + 2) + D_avg + 2
        trips = self.ceil_divide(remaining_total, max_load)
        d_avg = self.ceil_divide(total_distance, pavilion_count)
        return abs(x - wx) + abs(y - wy) + ((trips - 1) * ((2 * d_avg) + 2)) + d_avg + 2

    ##################### find out the max load
    @Rule(
        InitialNeed(pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(PavilionTotal(pid=MATCH.pid)),
        NOT(NeedCounted(pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color)),
        salience=100)
    def create_pavilion_total(self, pid, flower, color, qty):
        self.declare(PavilionTotal(pid=pid, total=qty))
        self.declare(NeedCounted(pid=pid, flower=flower, color=color))

    @Rule(
        AS.total_fact << PavilionTotal(pid=MATCH.pid, total=MATCH.total),
        InitialNeed(pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(NeedCounted(pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color)),
        salience=90)
    def add_need_to_pavilion_total(self, total_fact, pid, flower, color, total, qty):
        self.modify(total_fact, total=total + qty)
        self.declare(NeedCounted(pid=pid, flower=flower, color=color))

    @Rule(
        AS.max_load_fact << MaxLoad(value=MATCH.current_max),
        PavilionTotal(total=MATCH.total),
        TEST(lambda total, current_max: total > current_max),
        salience=80)
    def update_max_load(self, max_load_fact, total):
        self.modify(max_load_fact, value=total)

    @Rule(
        MaxLoad(value=MATCH.max_load),
        PavilionTotal(),
        TEST(lambda max_load: max_load > 0),
        NOT(MaxLoadReady(status="ready")),
        salience=70,
    )
    def mark_max_load_ready(self, max_load):
        self.declare(MaxLoadReady(status="ready"))

    ##################### A* heuristic from the trip approach
    @Rule(
        AS.state_fact << State(sid=MATCH.sid, load=0, g=MATCH.g),
        AS.open_fact << OpenState(sid=MATCH.sid, g=MATCH.g),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(RemainingNeed(sid=MATCH.sid)),
        NOT(Carrying(sid=MATCH.sid)),
        NOT(HeuristicReady(sid=MATCH.sid)),
        salience=54,
    )
    def apply_goal_heuristic(self, state_fact, open_fact, sid, g):
        self.modify(state_fact, h=0, f=g)
        self.modify(open_fact, h=0, f=g)
        self.declare(HeuristicReady(sid=sid))

    @Rule(
        AS.total_fact << HeuristicNeedTotal(sid=MATCH.sid, total=MATCH.total),
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(HeuristicReady(sid=MATCH.sid)),
        NOT(HeuristicNeedCounted(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color)),
        salience=58,
    )
    def add_remaining_need_to_heuristic_total(self, total_fact, sid, pid, flower, color, qty, total):
        self.modify(total_fact, total=total + qty)
        self.declare(HeuristicNeedCounted(sid=sid, pid=pid, flower=flower, color=color))

    @Rule(
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(HeuristicReady(sid=MATCH.sid)),
        NOT(HeuristicNeedTotal(sid=MATCH.sid)),
        NOT(HeuristicNeedCounted(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color)),
        salience=59,
    )
    # to calculate the remaining total bouquets for the needs
    def create_heuristic_remaining_total(self, sid, pid, flower, color, qty):
        self.declare(HeuristicNeedTotal(sid=sid, total=qty))
        self.declare(HeuristicNeedCounted(sid=sid, pid=pid, flower=flower, color=color))

    @Rule(
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(HeuristicReady(sid=MATCH.sid)),
        Pavilion(pid=MATCH.pid, x=MATCH.px, y=MATCH.py),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        NOT(HeuristicActivePavilionDistance(sid=MATCH.sid, pid=MATCH.pid)),
        salience=59,
    )
    def create_active_pavilion_distance(self, sid, pid, px, py, wx, wy):
        self.declare(HeuristicActivePavilionDistance(sid=sid, pid=pid, distance=abs(px - wx) + abs(py - wy), ))

    @Rule(
        AS.summary_fact << HeuristicPavilionSummary(sid=MATCH.sid, total_distance=MATCH.total_distance,
                                                    pavilion_count=MATCH.pavilion_count, ),
        HeuristicActivePavilionDistance(sid=MATCH.sid, pid=MATCH.pid, distance=MATCH.distance),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(HeuristicReady(sid=MATCH.sid)),
        NOT(HeuristicPavilionCounted(sid=MATCH.sid, pid=MATCH.pid)),
        salience=56,
    )
    def add_active_pavilion_to_summary(self, summary_fact, sid, pid, distance, total_distance, pavilion_count):
        self.modify(summary_fact, total_distance=total_distance + distance, pavilion_count=pavilion_count + 1, )
        self.declare(HeuristicPavilionCounted(sid=sid, pid=pid))

    @Rule(
        HeuristicActivePavilionDistance(sid=MATCH.sid, pid=MATCH.pid, distance=MATCH.distance),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(HeuristicReady(sid=MATCH.sid)),
        NOT(HeuristicPavilionSummary(sid=MATCH.sid)),
        NOT(HeuristicPavilionCounted(sid=MATCH.sid, pid=MATCH.pid)),
        salience=57,
    )
    def create_active_pavilion_summary(self, sid, pid, distance):
        self.declare(HeuristicPavilionSummary(sid=sid, total_distance=distance, pavilion_count=1))
        self.declare(HeuristicPavilionCounted(sid=sid, pid=pid))

    @Rule(
        AS.state_fact << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=0, g=MATCH.g),
        AS.open_fact << OpenState(sid=MATCH.sid, g=MATCH.g),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda max_load: max_load > 0),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        HeuristicNeedTotal(sid=MATCH.sid, total=MATCH.remaining_total),
        HeuristicPavilionSummary(sid=MATCH.sid, total_distance=MATCH.total_distance,
                                 pavilion_count=MATCH.pavilion_count, ),
        NOT(HeuristicReady(sid=MATCH.sid)),
        salience=54,
    )
    def apply_trip_based_heuristic(self, state_fact, open_fact, sid, x, y, g, wx, wy, remaining_total, max_load,
                                   total_distance, pavilion_count, ):
        h = self.trip_based_heuristic(x, y, wx, wy, remaining_total, max_load, total_distance,
                                      pavilion_count)  # empty states must go to the warehouse, so the trip-based estimate is appropriate here.
        self.modify(state_fact, h=h, f=g + h)
        self.modify(open_fact, h=h, f=g + h)
        self.declare(HeuristicReady(sid=sid))

        # For a loaded robot, creates heuristic candidates toward pavilions that can accept the current cargo.

    @Rule(
        State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda load: load > 0),
        Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.carry_qty),
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.need_qty, ),
        TEST(lambda carry_qty, need_qty: carry_qty >= need_qty),
        Pavilion(pid=MATCH.pid, flower=MATCH.flower, x=MATCH.px, y=MATCH.py),
        NOT(HeuristicCandidate(sid=MATCH.sid, source=MATCH.pid)),
        salience=59,
    )
    def create_loaded_robot_pavilion_candidate(self, sid, x, y, px, py, pid):
        self.declare(HeuristicCandidate(sid=sid, value=abs(x - px) + abs(y - py),
                                        source=pid, ))  # loaded states should be guided toward a pavilion that can accept the carried bouquets.

    # Creates a fallback heuristic for loaded states when no pavilion can accept the current cargo.
    @Rule(
        State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load),
        OpenState(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda load: load > 0),
        RemainingNeed(sid=MATCH.sid),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        NOT(HeuristicCandidate(sid=MATCH.sid)),
        salience=58,
    )
    def create_loaded_robot_fallback_candidate(self, sid, x, y, wx, wy):
        self.declare(HeuristicCandidate(sid=sid, value=abs(x - wx) + abs(y - wy),
                                        source="warehouse-fallback", ))  # If no current cargo can satisfy a pavilion, estimate returning to the warehouse.

    @Rule(
        HeuristicCandidate(sid=MATCH.sid, value=MATCH.value),
        HeuristicCandidate(sid=MATCH.sid, value=MATCH.other_value),
        TEST(lambda other_value, value: other_value < value),
        NOT(SmallerHeuristic(sid=MATCH.sid, value=MATCH.value)),
        salience=57,
    )
    def mark_smaller_loaded_heuristic_exists(self, sid, value):
        self.declare(SmallerHeuristic(sid=sid,
                                      value=value))  # this candidate is not the closest useful pavilion because a smaller candidate exists.

    # Applies the smallest loaded-robot heuristic candidate.
    @Rule(
        AS.state_fact << State(sid=MATCH.sid, g=MATCH.g, load=MATCH.load),
        AS.open_fact << OpenState(sid=MATCH.sid, g=MATCH.g),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda load: load > 0),
        HeuristicCandidate(sid=MATCH.sid, value=MATCH.h),
        NOT(SmallerHeuristic(sid=MATCH.sid, value=MATCH.h)),
        NOT(HeuristicReady(sid=MATCH.sid)),
        salience=54,
    )
    def apply_loaded_robot_heuristic(self, state_fact, open_fact, sid, g, h):
        self.modify(state_fact, h=h, f=g + h)  # loaded states use the closest deliverable pavilion estimate.
        self.modify(open_fact, h=h, f=g + h)
        self.declare(HeuristicReady(sid=sid))

    ##################### A* to select the next state
    ### we can say that there is a better state that is blocking the better_f
    @Rule(
        OpenState(sid=MATCH.candidate_sid, f=MATCH.candidate_f),
        HeuristicReady(sid=MATCH.candidate_sid),
        NOT(PrunedState(sid=MATCH.candidate_sid)),
        OpenState(sid=MATCH.better_sid, f=MATCH.better_f),
        HeuristicReady(sid=MATCH.better_sid),
        NOT(PrunedState(sid=MATCH.better_sid)),
        TEST(lambda candidate_sid, better_sid: candidate_sid != better_sid),
        TEST(lambda better_f, candidate_f: better_f < candidate_f),
        NOT(BetterOpenState(candidate_sid=MATCH.candidate_sid)),
        salience=70,
    )
    def mark_better_open_state_exists(self, candidate_sid, better_sid):
        self.declare(BetterOpenState(candidate_sid=candidate_sid, better_sid=better_sid))

    @Rule(
        OpenState(sid=MATCH.sid, g=MATCH.g, h=MATCH.h, f=MATCH.f),
        HeuristicReady(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        NOT(ClosedState(sid=MATCH.sid)),
        NOT(SelectedState(sid=MATCH.any_sid)),
        NOT(BetterOpenState(candidate_sid=MATCH.sid)),
        salience=69,
    )
    def select_lowest_f_open_state(self, sid):
        self.declare(SelectedState(sid=sid))

    # negative salience to run it after the expansion rules

    @Rule(
        AS.selected_fact << SelectedState(sid=MATCH.sid),
        AS.open_fact << OpenState(sid=MATCH.sid),
        NOT(SearchFinished(status="done")),
        NOT(ClosedState(sid=MATCH.sid)),
        salience=-10,
    )
    def close_selected_state(self, selected_fact, open_fact, sid):
        self.declare(ClosedState(sid=sid))
        self.retract(selected_fact)
        self.retract(open_fact)

    @Rule(
        ClosedState(sid=MATCH.sid),
        AS.better_fact << BetterOpenState(better_sid=MATCH.sid),
        salience=68,
    )
    def retract_closed_better_open_state(self, better_fact):
        self.retract(better_fact)

    @Rule(
        SearchFinished(status="done"),
        salience=1000,
    )
    def stop_after_first_solution(self):
        self.halt()

    #############################Loading logic

    #########Choose the first bouquet

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=0, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Warehouse(x=MATCH.x, y=MATCH.y),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        TEST(lambda qty, max_load: qty <= max_load),
        AS.next_draft << NextDraftId(value=MATCH.draft_id),
        NOT(LoadSeeded(parent_sid=MATCH.sid, mode="same-flower", flower=MATCH.flower, color=MATCH.color, )),
        salience=40, )
    def seed_same_flower_load(self, next_draft, sid, draft_id, flower, color, qty, ):  # choose the first bouquet
        self.declare(
            LoadDraft(parent_sid=sid, draft_id=draft_id, mode="same-flower", seed_flower=flower, seed_color=color,
                      load=qty, ))
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))
        self.declare(LoadSeeded(parent_sid=sid, mode="same-flower", flower=flower, color=color, ))
        self.modify(next_draft, value=draft_id + 1)

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=0, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Warehouse(x=MATCH.x, y=MATCH.y),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        TEST(lambda qty, max_load: qty <= max_load),
        AS.next_draft << NextDraftId(value=MATCH.draft_id),
        NOT(LoadSeeded(parent_sid=MATCH.sid, mode="same-color", flower=MATCH.flower, color=MATCH.color, )),
        salience=40, )
    def seed_same_color_load(self, next_draft, sid, draft_id, flower, color, qty, ):
        # The first loaded group fixes the color for same-color loading.
        self.declare(
            LoadDraft(parent_sid=sid, draft_id=draft_id, mode="same-color", seed_flower=flower, seed_color=color,
                      load=qty, ))
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))
        self.declare(LoadSeeded(parent_sid=sid, mode="same-color", flower=flower, color=color, ))
        self.modify(next_draft, value=draft_id + 1)

    #######################choose bouquets but you already carry something
    @Rule(
        State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.current_load, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda current_load: current_load > 0),
        Warehouse(x=MATCH.x, y=MATCH.y),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        Carrying(sid=MATCH.sid, flower=MATCH.flower),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        TEST(lambda current_load, qty, max_load: current_load + qty <= max_load),
        AS.next_draft << NextDraftId(value=MATCH.draft_id),
        NOT(Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color)),
        NOT(LoadSeeded(parent_sid=MATCH.sid, mode="same-flower", flower=MATCH.flower, color=MATCH.color, )),
        salience=40, )
    def seed_same_flower_load_with_existing_cargo(self, next_draft, sid, draft_id, flower, color, qty, current_load, ):
        self.declare(
            LoadDraft(parent_sid=sid, draft_id=draft_id, mode="same-flower", seed_flower=flower, seed_color=color,
                      load=current_load + qty, ))
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))
        self.declare(LoadSeeded(parent_sid=sid, mode="same-flower", flower=flower, color=color))
        self.modify(next_draft, value=draft_id + 1)

    @Rule(
        State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.current_load, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda current_load: current_load > 0),
        Warehouse(x=MATCH.x, y=MATCH.y),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        Carrying(sid=MATCH.sid, color=MATCH.color),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        TEST(lambda current_load, qty, max_load: current_load + qty <= max_load),
        AS.next_draft << NextDraftId(value=MATCH.draft_id),
        NOT(Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color)),
        NOT(LoadSeeded(parent_sid=MATCH.sid, mode="same-color", flower=MATCH.flower, color=MATCH.color, )),
        salience=40, )
    def seed_same_color_load_with_existing_cargo(self, next_draft, sid, draft_id, flower, color, qty, current_load, ):
        self.declare(
            LoadDraft(parent_sid=sid, draft_id=draft_id, mode="same-color", seed_flower=flower, seed_color=color,
                      load=current_load + qty))
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))
        self.declare(LoadSeeded(parent_sid=sid, mode="same-color", flower=flower, color=color, ))
        self.modify(next_draft, value=draft_id + 1)

    #########################

    @Rule(
        AS.draft << LoadDraft(parent_sid=MATCH.sid, draft_id=MATCH.draft_id, mode="same-flower",
                              seed_flower=MATCH.flower, load=MATCH.load, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        TEST(lambda load, qty, max_load: load + qty <= max_load),
        NOT(LoadDraftApplied(draft_id=MATCH.draft_id)),
        NOT(Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color)),
        NOT(LoadDraftItem(draft_id=MATCH.draft_id, flower=MATCH.flower, color=MATCH.color)),
        salience=30,
    )
    def extend_same_flower_load(self, draft, draft_id, flower, color, qty, load):
        self.modify(draft, load=load + qty)
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))

    @Rule(
        AS.draft << LoadDraft(parent_sid=MATCH.sid, draft_id=MATCH.draft_id, mode="same-color", seed_color=MATCH.color,
                              load=MATCH.load, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        MaxLoadReady(status="ready"),
        MaxLoad(value=MATCH.max_load),
        RemainingNeed(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        TEST(lambda load, qty, max_load: load + qty <= max_load),
        NOT(LoadDraftApplied(draft_id=MATCH.draft_id)),
        NOT(Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color)),
        NOT(LoadDraftItem(draft_id=MATCH.draft_id, flower=MATCH.flower, color=MATCH.color)),
        salience=30,
    )
    def extend_same_color_load(self, draft, draft_id, flower, color, qty, load):
        self.modify(draft, load=load + qty)
        self.declare(LoadDraftItem(draft_id=draft_id, flower=flower, color=color, qty=qty))

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.current_load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Warehouse(x=MATCH.x, y=MATCH.y),
        LoadDraft(parent_sid=MATCH.sid, draft_id=MATCH.draft_id, mode=MATCH.mode, load=MATCH.new_load, ),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(LoadDraftApplied(draft_id=MATCH.draft_id)),
        salience=20, )
    def finalize_load_draft(self, current_state, next_id, sid, child_sid, draft_id, mode, new_load, next_depth_key, g,
                            h, ):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="load-" + mode, load=new_load,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id,
                    value=child_sid + 1)  # updates the global state id counter, so the next generated child gets a fresh id.
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(LoadDraftApplied(draft_id=draft_id, child_sid=child_sid))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="load-" + mode, cost=1))

    @Rule(
        LoadDraftApplied(draft_id=MATCH.draft_id, child_sid=MATCH.child_sid),
        LoadDraftItem(draft_id=MATCH.draft_id, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        NOT(PrunedState(sid=MATCH.child_sid)),
        NOT(Carrying(sid=MATCH.child_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, )),
        salience=60, )
    def copy_loaded_item_to_child(self, child_sid, flower, color, qty):
        self.declare(Carrying(sid=child_sid, flower=flower, color=color, qty=qty))

    #######################Unload
    ############### seed unloading

    @Rule(
        State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda load: load > 0),
        Pavilion(pid=MATCH.pid, flower=MATCH.flower, x=MATCH.x, y=MATCH.y),
        Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.carry_qty, ),
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.need_qty, ),
        TEST(lambda carry_qty, need_qty: carry_qty >= need_qty),
        AS.next_unload_draft << NextUnloadDraftId(value=MATCH.draft_id),
        NOT(UnloadSeeded(parent_sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, )), salience=40, )
    def seed_unload_draft(self, next_unload_draft, sid, draft_id, pid, flower, color, need_qty, ):
        # The first matched color starts one unload candidate for this pavilion.
        self.declare(UnloadDraft(parent_sid=sid, draft_id=draft_id, pid=pid, flower=flower, unload=need_qty, ))
        self.declare(UnloadDraftItem(draft_id=draft_id, pid=pid, flower=flower, color=color, qty=need_qty, ))
        self.declare(UnloadSeeded(parent_sid=sid, pid=pid, flower=flower, color=color))
        self.modify(next_unload_draft, value=draft_id + 1)

    @Rule(
        AS.draft << UnloadDraft(parent_sid=MATCH.sid, draft_id=MATCH.draft_id, pid=MATCH.pid, flower=MATCH.flower,
                                unload=MATCH.unload, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Carrying(sid=MATCH.sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.carry_qty, ),
        RemainingNeed(sid=MATCH.sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.need_qty, ),
        TEST(lambda carry_qty, need_qty: carry_qty >= need_qty),
        NOT(UnloadDraftApplied(draft_id=MATCH.draft_id)),
        NOT(UnloadDraftItem(draft_id=MATCH.draft_id, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, )),
        salience=30, )
    def extend_unload_draft(self, draft, draft_id, pid, flower, color, need_qty, unload, ):
        self.modify(draft, unload=unload + need_qty)
        self.declare(UnloadDraftItem(draft_id=draft_id, pid=pid, flower=flower, color=color, qty=need_qty))

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Pavilion(pid=MATCH.pid, x=MATCH.x, y=MATCH.y),
        UnloadDraft(parent_sid=MATCH.sid, draft_id=MATCH.draft_id, pid=MATCH.pid, unload=MATCH.unload, ),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(UnloadDraftApplied(draft_id=MATCH.draft_id)),
        salience=20,
    )
    def finalize_unload_draft(self, current_state, next_id, sid, child_sid, draft_id, pid, load, unload, next_depth_key,
                              g, h, ):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="unload-" + pid, load=load - unload,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id, value=child_sid + 1)
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(UnloadChild(parent_sid=sid, child_sid=child_sid, draft_id=draft_id))
        self.declare(UnloadDraftApplied(draft_id=draft_id, child_sid=child_sid))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="unload-" + pid, cost=1))

    ######################## movement rules

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Grid(width=MATCH.max_x),
        TEST(lambda x, max_x: x < max_x),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        TEST(lambda load, x, y, wx, wy: load > 0 or abs((x + 1) - wx) + abs(y - wy) < abs(x - wx) + abs(y - wy)),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(SearchEdge(parent=MATCH.sid, action="move-right")),
        # to prevent generating the same child from the same parent
    )
    def move_right(self, current_state, next_id, sid, child_sid, x, next_depth_key, g, h):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="move-right", robot_x=x + 1,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id, value=child_sid + 1)
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="move-right", cost=1))

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda x: x > 1),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        TEST(lambda load, x, y, wx, wy: load > 0 or abs((x - 1) - wx) + abs(y - wy) < abs(x - wx) + abs(y - wy)),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(SearchEdge(parent=MATCH.sid, action="move-left")),
    )
    def move_left(self, current_state, next_id, sid, child_sid, x, next_depth_key, g, h):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="move-left", robot_x=x - 1,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id, value=child_sid + 1)
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="move-left", cost=1))

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        TEST(lambda y: y > 1),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        TEST(lambda load, x, y, wx, wy: load > 0 or abs(x - wx) + abs((y - 1) - wy) < abs(x - wx) + abs(y - wy)),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(SearchEdge(parent=MATCH.sid, action="move-up")),
    )
    def move_up(self, current_state, next_id, sid, child_sid, x, y, next_depth_key, g, h):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="move-up", robot_x=x, robot_y=y - 1,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id, value=child_sid + 1)
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="move-up", cost=1))

    @Rule(
        AS.current_state << State(sid=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
                                  depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h, ),
        NOT(PrunedState(sid=MATCH.sid)),
        SelectedState(sid=MATCH.sid),
        NOT(Goal(sid=MATCH.sid)),
        NOT(SearchFinished(status="done")),
        Grid(height=MATCH.max_y),
        TEST(lambda y, max_y: y < max_y),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        TEST(lambda load, x, y, wx, wy: load > 0 or abs(x - wx) + abs((y + 1) - wy) < abs(x - wx) + abs(y - wy)),
        DepthStep(depth_key=MATCH.depth_key, next_depth_key=MATCH.next_depth_key),
        AS.next_id << NextStateId(value=MATCH.child_sid),
        NOT(SearchEdge(parent=MATCH.sid, action="move-down")),
    )
    def move_down(self, current_state, next_id, sid, child_sid, x, y, next_depth_key, g, h):
        child_g = g + 1
        self.duplicate(current_state, sid=child_sid, parent=sid, action="move-down", robot_x=x, robot_y=y + 1,
                       depth_key=next_depth_key, g=child_g, f=child_g + h, )
        self.modify(next_id, value=child_sid + 1)
        self.declare(OpenState(sid=child_sid, g=child_g, h=h, f=child_g + h))
        self.declare(SearchEdge(parent=sid, child=child_sid, action="move-down", cost=1))

    #################################

    @Rule(
        State(sid=MATCH.child_sid, parent=MATCH.parent_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        NOT(UnloadChild(child_sid=MATCH.child_sid)),
        RemainingNeed(sid=MATCH.parent_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        NOT(RemainingNeed(sid=MATCH.child_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, )),
        salience=60, )
    def copy_remaining_need(self, child_sid, pid, flower, color, qty):
        self.declare(RemainingNeed(sid=child_sid, pid=pid, flower=flower, color=color, qty=qty, ))

    @Rule(
        State(sid=MATCH.child_sid, parent=MATCH.parent_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        UnloadChild(parent_sid=MATCH.parent_sid, child_sid=MATCH.child_sid, draft_id=MATCH.draft_id, ),
        RemainingNeed(sid=MATCH.parent_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        NOT(UnloadDraftItem(draft_id=MATCH.draft_id, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, )),
        NOT(RemainingNeed(sid=MATCH.child_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, )),
        salience=60, )
    def copy_remaining_need_after_unload(self, child_sid, pid, flower, color, qty):
        self.declare(RemainingNeed(sid=child_sid, pid=pid, flower=flower, color=color, qty=qty, ))

    @Rule(
        State(sid=MATCH.child_sid, parent=MATCH.parent_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        NOT(UnloadChild(child_sid=MATCH.child_sid)),
        Carrying(sid=MATCH.parent_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        NOT(Carrying(sid=MATCH.child_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, )),
        salience=60, )
    def copy_carrying(self, child_sid, flower, color, qty):
        self.declare(Carrying(sid=child_sid, flower=flower, color=color, qty=qty))

    @Rule(
        State(sid=MATCH.child_sid, parent=MATCH.parent_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        UnloadChild(parent_sid=MATCH.parent_sid, child_sid=MATCH.child_sid, draft_id=MATCH.draft_id, ),
        Carrying(sid=MATCH.parent_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, ),
        NOT(UnloadDraftItem(draft_id=MATCH.draft_id, flower=MATCH.flower, color=MATCH.color, )),
        NOT(Carrying(sid=MATCH.child_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty, )),
        salience=60, )
    def copy_unaffected_carrying_after_unload(self, child_sid, flower, color, qty):
        self.declare(Carrying(sid=child_sid, flower=flower, color=color, qty=qty))

    @Rule(
        State(sid=MATCH.child_sid, parent=MATCH.parent_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        UnloadChild(parent_sid=MATCH.parent_sid, child_sid=MATCH.child_sid, draft_id=MATCH.draft_id, ),
        Carrying(sid=MATCH.parent_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.carry_qty, ),
        UnloadDraftItem(draft_id=MATCH.draft_id, flower=MATCH.flower, color=MATCH.color, qty=MATCH.unload_qty, ),
        TEST(lambda carry_qty, unload_qty: carry_qty > unload_qty),
        NOT(Carrying(sid=MATCH.child_sid, flower=MATCH.flower, color=MATCH.color, )),
        salience=60, )
    def copy_reduced_carrying_after_unload(self, child_sid, flower, color, carry_qty, unload_qty, ):
        self.declare(Carrying(sid=child_sid, flower=flower, color=color, qty=carry_qty - unload_qty, ))

    ##################### print search tree
    @Rule(
        State(sid=MATCH.sid, parent=MATCH.parent, action=MATCH.action, robot_x=MATCH.x, robot_y=MATCH.y,
              load=MATCH.load, depth_key=MATCH.depth_key, g=MATCH.g, h=MATCH.h,
              f=MATCH.f, ),
        HeuristicReady(sid=MATCH.sid),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(StatePrinted(sid=MATCH.sid)), )
    def print_generated_state(self, sid, parent, action, x, y, load, depth_key, g, h, f):
        print(
            "TREE NODE | sid=",
            sid,
            "| parent=",
            parent,
            "| action=",
            action,
            "| robot=(",
            x,
            ",",
            y,
            ") | load=",
            load,
            "| depth=",
            depth_key,
            "| g=",
            g,
            "| h=",
            h,
            "| f=",
            f,
        )
        self.declare(StatePrinted(sid=sid))

    ##################### find and print solution
    @Rule(
        PathText(sid=MATCH.parent_sid, path=MATCH.parent_path),
        SearchEdge(parent=MATCH.parent_sid, child=MATCH.child_sid, action=MATCH.action),
        State(sid=MATCH.child_sid, g=MATCH.g),
        NOT(PrunedState(sid=MATCH.child_sid)),
        NOT(PathText(sid=MATCH.child_sid)),
    )
    def extend_path_text(self, child_sid, parent_path, action, g):
        self.declare(PathText(sid=child_sid, path=parent_path + "\n" + action + " | cost=" + str(g)))

    @Rule(
        State(sid=MATCH.sid, load=0),
        NOT(PrunedState(sid=MATCH.sid)),
        NOT(RemainingNeed(sid=MATCH.sid)),
        NOT(Carrying(sid=MATCH.sid)),
        NOT(Goal(sid=MATCH.sid)),
    )
    def check_goal_state(self, sid):
        self.declare(Goal(sid=sid))

    @Rule(
        Goal(sid=MATCH.sid),
        SelectedState(sid=MATCH.sid),
        State(sid=MATCH.sid, g=MATCH.g),
        PathText(sid=MATCH.sid, path=MATCH.path),
        NOT(SearchFinished(status="done")),
        NOT(SolutionPrinted(sid=MATCH.sid)),
    )
    def print_solution_path(self, sid, g, path):
        print("Goal state reached:", sid)
        print("Total cost:", g)
        print("Solution path:")
        print(path)
        self.declare(SolutionPrinted(sid=sid))
        self.declare(SearchFinished(status="done"))

    ##################### prune repeated states
    @Rule(
        State(sid=MATCH.source_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, depth_key=MATCH.source_depth),
        State(sid=MATCH.candidate_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
              depth_key=MATCH.candidate_depth),
        TEST(lambda source_sid, candidate_sid: source_sid != candidate_sid),
        TEST(lambda source_depth, candidate_depth: source_depth < candidate_depth),
        RemainingNeed(sid=MATCH.source_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(RemainingNeed(sid=MATCH.candidate_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color,
                          qty=MATCH.qty)),
        NOT(StatesDifferent(source_sid=MATCH.source_sid, candidate_sid=MATCH.candidate_sid)),
        salience=50,
    )
    def mark_states_different_by_missing_candidate_need(self, source_sid, candidate_sid):
        self.declare(StatesDifferent(source_sid=source_sid, candidate_sid=candidate_sid))

    @Rule(
        State(sid=MATCH.source_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, depth_key=MATCH.source_depth),
        State(sid=MATCH.candidate_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
              depth_key=MATCH.candidate_depth),
        TEST(lambda source_sid, candidate_sid: source_sid != candidate_sid),
        TEST(lambda source_depth, candidate_depth: source_depth < candidate_depth),
        RemainingNeed(sid=MATCH.candidate_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(RemainingNeed(sid=MATCH.source_sid, pid=MATCH.pid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty)),
        NOT(StatesDifferent(source_sid=MATCH.source_sid, candidate_sid=MATCH.candidate_sid)),
        salience=50,
    )
    def mark_states_different_by_extra_candidate_need(self, source_sid, candidate_sid):
        self.declare(StatesDifferent(source_sid=source_sid, candidate_sid=candidate_sid))

    @Rule(
        State(sid=MATCH.source_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, depth_key=MATCH.source_depth),
        State(sid=MATCH.candidate_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
              depth_key=MATCH.candidate_depth),
        TEST(lambda source_sid, candidate_sid: source_sid != candidate_sid),
        TEST(lambda source_depth, candidate_depth: source_depth < candidate_depth),
        Carrying(sid=MATCH.source_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(Carrying(sid=MATCH.candidate_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty)),
        NOT(StatesDifferent(source_sid=MATCH.source_sid, candidate_sid=MATCH.candidate_sid)),
        salience=50,
    )
    def mark_states_different_by_missing_candidate_carrying(self, source_sid, candidate_sid):
        self.declare(StatesDifferent(source_sid=source_sid, candidate_sid=candidate_sid))

    @Rule(
        State(sid=MATCH.source_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, depth_key=MATCH.source_depth),
        State(sid=MATCH.candidate_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
              depth_key=MATCH.candidate_depth),
        TEST(lambda source_sid, candidate_sid: source_sid != candidate_sid),
        TEST(lambda source_depth, candidate_depth: source_depth < candidate_depth),
        Carrying(sid=MATCH.candidate_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty),
        NOT(Carrying(sid=MATCH.source_sid, flower=MATCH.flower, color=MATCH.color, qty=MATCH.qty)),
        NOT(StatesDifferent(source_sid=MATCH.source_sid, candidate_sid=MATCH.candidate_sid)),
        salience=50,
    )
    def mark_states_different_by_extra_candidate_carrying(self, source_sid, candidate_sid):
        self.declare(StatesDifferent(source_sid=source_sid, candidate_sid=candidate_sid))

    @Rule(
        State(sid=MATCH.source_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load, depth_key=MATCH.source_depth),
        State(sid=MATCH.candidate_sid, robot_x=MATCH.x, robot_y=MATCH.y, load=MATCH.load,
              depth_key=MATCH.candidate_depth),
        TEST(lambda source_sid, candidate_sid: source_sid != candidate_sid),
        TEST(lambda source_depth, candidate_depth: source_depth < candidate_depth),
        NOT(StatesDifferent(source_sid=MATCH.source_sid, candidate_sid=MATCH.candidate_sid)),
        NOT(PrunedState(sid=MATCH.candidate_sid)),
        salience=45,
    )
    def mark_repeated_state_for_pruning(self, candidate_sid):
        self.declare(PrunedState(sid=candidate_sid))

    @Rule(
        PrunedState(sid=MATCH.parent_sid),
        SearchEdge(parent=MATCH.parent_sid, child=MATCH.child_sid),
        NOT(PrunedState(sid=MATCH.child_sid)),
        salience=44,
    )
    def cascade_pruning_to_child(self, child_sid):
        self.declare(PrunedState(sid=child_sid))

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.state_fact << State(sid=MATCH.sid), salience=43, )
    def retract_pruned_state(self, state_fact):
        self.retract(state_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.need_fact << RemainingNeed(sid=MATCH.sid), salience=43, )
    def retract_pruned_remaining_need(self, need_fact):
        self.retract(need_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.carrying_fact << Carrying(sid=MATCH.sid), salience=43, )
    def retract_pruned_carrying(self, carrying_fact):
        self.retract(carrying_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.path_fact << PathText(sid=MATCH.sid), salience=43, )
    def retract_pruned_path_text(self, path_fact):
        self.retract(path_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.goal_fact << Goal(sid=MATCH.sid), salience=43, )
    def retract_pruned_goal(self, goal_fact):
        self.retract(goal_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.printed_fact << SolutionPrinted(sid=MATCH.sid), salience=43, )
    def retract_pruned_solution_printed(self, printed_fact):
        self.retract(printed_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.printed_fact << StatePrinted(sid=MATCH.sid), salience=43, )
    def retract_pruned_state_printed(self, printed_fact):
        self.retract(printed_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.open_fact << OpenState(sid=MATCH.sid), salience=43, )
    def retract_pruned_open_state(self, open_fact):
        self.retract(open_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.selected_fact << SelectedState(sid=MATCH.sid), salience=43, )
    def retract_pruned_selected_state(self, selected_fact):
        self.retract(selected_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.closed_fact << ClosedState(sid=MATCH.sid), salience=43, )
    def retract_pruned_closed_state(self, closed_fact):
        self.retract(closed_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.heuristic_fact << HeuristicCandidate(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_candidate(self, heuristic_fact):
        self.retract(heuristic_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.ready_fact << HeuristicReady(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_ready(self, ready_fact):
        self.retract(ready_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.total_fact << HeuristicNeedTotal(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_need_total(self, total_fact):
        self.retract(total_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.counted_fact << HeuristicNeedCounted(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_need_counted(self, counted_fact):
        self.retract(counted_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.distance_fact << HeuristicActivePavilionDistance(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_active_pavilion_distance(self, distance_fact):
        self.retract(distance_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.summary_fact << HeuristicPavilionSummary(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_pavilion_summary(self, summary_fact):
        self.retract(summary_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.counted_fact << HeuristicPavilionCounted(sid=MATCH.sid), salience=43, )
    def retract_pruned_heuristic_pavilion_counted(self, counted_fact):
        self.retract(counted_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.smaller_fact << SmallerHeuristic(sid=MATCH.sid), salience=43, )
    def retract_pruned_smaller_heuristic(self, smaller_fact):
        self.retract(smaller_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.better_fact << BetterOpenState(candidate_sid=MATCH.sid), salience=43, )
    def retract_pruned_better_open_candidate(self, better_fact):
        self.retract(better_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.better_fact << BetterOpenState(better_sid=MATCH.sid), salience=43, )
    def retract_pruned_better_open_source(self, better_fact):
        self.retract(better_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.draft_fact << LoadDraft(parent_sid=MATCH.sid), salience=43, )
    def retract_pruned_load_draft(self, draft_fact):
        self.retract(draft_fact)

    @Rule(
        PrunedState(sid=MATCH.sid),
        AS.draft_fact << UnloadDraft(parent_sid=MATCH.sid), salience=43, )
    def retract_pruned_unload_draft(self, draft_fact):
        self.retract(draft_fact)
