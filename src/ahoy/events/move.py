from ahoy.event import Event

class EntityMoveEvent(Event) :
    def __init__(self, entity, lat, long, agl, bearing, forward_vel=None, lin_vel=None) :
        Event.__init__(self)
        self._entity_uid = entity.get_uid()
        self._entity_type = entity.__class__.__name__
        self._entity_agents = map(lambda a : a.__class__.__name__, entity.get_agents().values())
        self._lat = lat
        self._long = long
        self._agl = agl
        self._forward_vel = forward_vel
        self._lin_vel = lin_vel
        self._bearing = bearing

    def get_uid(self) :
        return self._entity_uid

    def get_lat(self) :
        return self._lat

    def get_long(self) :
        return self._long

    def get_agl(self) :
        return self._agl

    def get_type(self) :
        return self._entity_type

    def get_forward_vel(self) :
        return self._forward_vel

    def get_lin_vel(self) :
        return self._lin_vel

    def get_bearing(self) :
        return self._bearing

    def get_agents(self) :
        return self._entity_agents
