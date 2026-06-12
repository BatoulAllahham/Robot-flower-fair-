from astar_engine import FlowerDeliveryEngineWithAStar
from dfs_engine import FlowerDeliveryEngineWithDFS
from initial_data import declare_initial_facts


# engine = FlowerDeliveryEngineWithAStar()
engine = FlowerDeliveryEngineWithDFS()
engine.reset()
declare_initial_facts(engine)

engine.run()

