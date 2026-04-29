from models.sticky_note import StickyNote

class NoteManager:

    def __init__(self):
        self.notes: dict[str, StickyNote] = {}

    def add_note(self, id: str, text_content: str = "", color: str = "#FFEB3B") -> StickyNote:
        note = StickyNote(id=id,text_content=text_content, color=color)
        self.notes[id] = note
        return note
    
    def remove_note(self, id: str) -> bool:
        if id in self.notes:
            del self.notes[id]
            return True
        return False