from abc import ABC, abstractmethod

class CanvasItem(ABC):

    def __init__(self, id: str, color: str = "#FFFFFF", dimensions: tuple = (100,100)):
        self.id = id
        self.color = color
        self.dimensions = dimensions

    @abstractmethod
    def edit_properties(self, **kwargs):
        pass
    
