from stage.world import World

class TestWorld(World) :
    def __init__(self) :
        World.__init__(self)
        self.add_entity(Node(0))
