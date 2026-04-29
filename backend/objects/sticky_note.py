from email.mime import text

from models.canvas_item import CanvasItem

class StickyNote(CanvasItem):

    def __init__(self, id: str, text_content: str= "", color: str = "#FFEB3B", dimensions: tuple = (150,100)):
        super().__init__(id, color, dimensions)
        self.text_content = text_content

    def edit_properties(self, text_content: str = None, color: str = None):
        if text_content is not None:
            self.text_content = text_content
        if color is not None:
            self.color = color
            