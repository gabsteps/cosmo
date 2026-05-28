from collections import defaultdict


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type, callback):
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):

        if event_type not in self.listeners:
            return

        for callback in self.listeners[event_type]:
            callback(data)


event_bus = EventBus()

#Próximo Upgrade Futuro

#Depois:

#async event bus
#prioridades
#middlewares
#fila
#debounce
#IPC
#distributed events