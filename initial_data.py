from facts import (
    BouquetColor,
    DepthLimit,
    DepthStep,
    FlowerType,
    Grid,
    InitialNeed,
    MaxLoad,
    NextDraftId,
    NextStateId,
    NextUnloadDraftId,
    OpenState,
    PathText,
    Pavilion,
    RemainingNeed,
    State,
    Warehouse,)


def declare_initial_facts(engine):
    engine.declare(Grid(width=5, height=5))
    engine.declare(Warehouse(x=3, y=2))
    engine.declare(DepthLimit(value=60))
    engine.declare(NextStateId(value=1))
    engine.declare(NextDraftId(value=1))
    engine.declare(NextUnloadDraftId(value=1))
    engine.declare(DepthStep(depth_key=0, next_depth_key=1))
    engine.declare(DepthStep(depth_key=1, next_depth_key=2))
    engine.declare(DepthStep(depth_key=2, next_depth_key=3))
    engine.declare(DepthStep(depth_key=3, next_depth_key=4))
    engine.declare(DepthStep(depth_key=4, next_depth_key=5))
    engine.declare(DepthStep(depth_key=5, next_depth_key=6))
    engine.declare(DepthStep(depth_key=6, next_depth_key=7))
    engine.declare(DepthStep(depth_key=7, next_depth_key=8))
    engine.declare(DepthStep(depth_key=8, next_depth_key=9))
    engine.declare(DepthStep(depth_key=9, next_depth_key=10))
    engine.declare(DepthStep(depth_key=10, next_depth_key=11))
    engine.declare(DepthStep(depth_key=11, next_depth_key=12))
    engine.declare(DepthStep(depth_key=12, next_depth_key=13))
    engine.declare(DepthStep(depth_key=13, next_depth_key=14))
    engine.declare(DepthStep(depth_key=14, next_depth_key=15))
    engine.declare(DepthStep(depth_key=15, next_depth_key=16))
    engine.declare(DepthStep(depth_key=16, next_depth_key=17))
    engine.declare(DepthStep(depth_key=17, next_depth_key=18))
    engine.declare(DepthStep(depth_key=18, next_depth_key=19))
    engine.declare(DepthStep(depth_key=19, next_depth_key=20))
    engine.declare(DepthStep(depth_key=20, next_depth_key=21))
    engine.declare(DepthStep(depth_key=21, next_depth_key=22))
    engine.declare(DepthStep(depth_key=22, next_depth_key=23))
    engine.declare(DepthStep(depth_key=23, next_depth_key=24))
    engine.declare(DepthStep(depth_key=24, next_depth_key=25))
    engine.declare(DepthStep(depth_key=25, next_depth_key=26))
    engine.declare(DepthStep(depth_key=26, next_depth_key=27))
    engine.declare(DepthStep(depth_key=27, next_depth_key=28))
    engine.declare(DepthStep(depth_key=28, next_depth_key=29))
    engine.declare(DepthStep(depth_key=29, next_depth_key=30))
    engine.declare(DepthStep(depth_key=30, next_depth_key=31))
    engine.declare(DepthStep(depth_key=31, next_depth_key=32))
    engine.declare(DepthStep(depth_key=32, next_depth_key=33))
    engine.declare(DepthStep(depth_key=33, next_depth_key=34))
    engine.declare(DepthStep(depth_key=34, next_depth_key=35))
    engine.declare(DepthStep(depth_key=35, next_depth_key=36))
    engine.declare(DepthStep(depth_key=36, next_depth_key=37))
    engine.declare(DepthStep(depth_key=37, next_depth_key=38))
    engine.declare(DepthStep(depth_key=38, next_depth_key=39))
    engine.declare(DepthStep(depth_key=39, next_depth_key=40))
    engine.declare(DepthStep(depth_key=40, next_depth_key=41))
    engine.declare(DepthStep(depth_key=41, next_depth_key=42))
    engine.declare(DepthStep(depth_key=42, next_depth_key=43))
    engine.declare(DepthStep(depth_key=43, next_depth_key=44))
    engine.declare(DepthStep(depth_key=44, next_depth_key=45))
    engine.declare(DepthStep(depth_key=45, next_depth_key=46))
    engine.declare(DepthStep(depth_key=46, next_depth_key=47))
    engine.declare(DepthStep(depth_key=47, next_depth_key=48))
    engine.declare(DepthStep(depth_key=48, next_depth_key=49))
    engine.declare(DepthStep(depth_key=49, next_depth_key=50))
    engine.declare(DepthStep(depth_key=50, next_depth_key=51))
    engine.declare(DepthStep(depth_key=51, next_depth_key=52))
    engine.declare(DepthStep(depth_key=52, next_depth_key=53))
    engine.declare(DepthStep(depth_key=53, next_depth_key=54))
    engine.declare(DepthStep(depth_key=54, next_depth_key=55))
    engine.declare(DepthStep(depth_key=55, next_depth_key=56))
    engine.declare(DepthStep(depth_key=56, next_depth_key=57))
    engine.declare(DepthStep(depth_key=57, next_depth_key=58))
    engine.declare(DepthStep(depth_key=58, next_depth_key=59))
    engine.declare(DepthStep(depth_key=59, next_depth_key=60))

    engine.declare(MaxLoad(value=0))

    # Flower type facts keep the valid domain explicit inside working memory.
    engine.declare(FlowerType(name="rose"))
    engine.declare(FlowerType(name="tulip"))
    engine.declare(FlowerType(name="orchid"))
    engine.declare(FlowerType(name="goliat_rose"))

    #  rose colors.
    engine.declare(BouquetColor(flower="rose", color="red"))
    engine.declare(BouquetColor(flower="rose", color="pink"))
    engine.declare(BouquetColor(flower="rose", color="white"))
    engine.declare(BouquetColor(flower="rose", color="yellow"))
    engine.declare(BouquetColor(flower="rose", color="burgundy"))

    #  tulip colors.
    engine.declare(BouquetColor(flower="tulip", color="red"))
    engine.declare(BouquetColor(flower="tulip", color="yellow"))
    engine.declare(BouquetColor(flower="tulip", color="violet"))
    engine.declare(BouquetColor(flower="tulip", color="orange"))
    engine.declare(BouquetColor(flower="tulip", color="green"))
    engine.declare(BouquetColor(flower="tulip", color="mauve"))
    engine.declare(BouquetColor(flower="tulip", color="purple"))

    #  orchid colors.
    engine.declare(BouquetColor(flower="orchid", color="purple"))
    engine.declare(BouquetColor(flower="orchid", color="white"))
    engine.declare(BouquetColor(flower="orchid", color="pink"))
    engine.declare(BouquetColor(flower="orchid", color="light_pink"))

    #  goliat rose colors.
    engine.declare(BouquetColor(flower="goliat_rose", color="gold"))
    engine.declare(BouquetColor(flower="goliat_rose", color="light_pink"))
    engine.declare(BouquetColor(flower="goliat_rose", color="yellow"))

    # Pavilion facts describe fixed targets on the grid.
    engine.declare(Pavilion(pid="p1", flower="rose", x=2, y=4))
    engine.declare(Pavilion(pid="p2", flower="tulip", x=4, y=3))
    engine.declare(Pavilion(pid="p3", flower="orchid", x=4, y=5))
    engine.declare(Pavilion(pid="p4", flower="goliat_rose", x=5, y=2))

    # Initial needs are kept as static facts.
    engine.declare(InitialNeed(pid="p1", flower="rose", color="red", qty=2))
    engine.declare(InitialNeed(pid="p1", flower="rose", color="pink", qty=1))
    engine.declare(InitialNeed(pid="p1", flower="rose", color="white", qty=1))
    engine.declare(InitialNeed(pid="p2", flower="tulip", color="red", qty=3))
    engine.declare(InitialNeed(pid="p2", flower="tulip", color="yellow", qty=1))
    engine.declare(InitialNeed(pid="p3", flower="orchid", color="purple", qty=2))
    engine.declare(InitialNeed(pid="p3", flower="orchid", color="pink", qty=1))
    engine.declare(InitialNeed(pid="p4", flower="goliat_rose", color="gold", qty=2))
    engine.declare(InitialNeed(pid="p4", flower="goliat_rose", color="light_pink", qty=2))

    engine.declare(State(sid=0, parent=None,action="initial",robot_x=1,robot_y=3,load=0,depth_key=0,g=0,h=0,f=0,))

    engine.declare(PathText(sid=0, path="initial"))

    # A* starts with only the root state in the open frontier.
    engine.declare(OpenState(sid=0, g=0, h=0, f=0))

    # RemainingNeed facts belong to state sid=0.
    engine.declare(RemainingNeed(sid=0, pid="p1", flower="rose", color="red", qty=2))
    engine.declare(RemainingNeed(sid=0, pid="p1", flower="rose", color="pink", qty=1))
    engine.declare(RemainingNeed(sid=0, pid="p1", flower="rose", color="white", qty=1))
    engine.declare(RemainingNeed(sid=0, pid="p2", flower="tulip", color="red", qty=3))
    engine.declare(RemainingNeed(sid=0, pid="p2", flower="tulip", color="yellow", qty=1))
    engine.declare(RemainingNeed(sid=0, pid="p3", flower="orchid", color="purple", qty=2))
    engine.declare(RemainingNeed(sid=0, pid="p3", flower="orchid", color="pink", qty=1))
    engine.declare(RemainingNeed(sid=0, pid="p4", flower="goliat_rose", color="gold", qty=2))
    engine.declare(RemainingNeed(sid=0, pid="p4", flower="goliat_rose", color="light_pink", qty=2))
