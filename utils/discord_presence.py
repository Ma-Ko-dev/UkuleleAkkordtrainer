import threading
import queue
import time
from pypresence import Presence



class DiscordRichPresence:
    def __init__(self, client_id):
        self.client_id = client_id
        self.update_queue = queue.Queue()
        self.thread = threading.Thread(target=self._presence_loop, daemon=True)
        self.rpc = None
        self.running = False

    
    def start(self):
        self.running = True
        self.thread.start()

    
    def stop(self):
        self.running = False
        if self.rpc:
            self.rpc.clear()
            self.rpc.close()

    
    def update_chord(self, chord_name):
        # TODO Upgrade with tones and intervals
        self.update_queue.put(chord_name)


    def _presence_loop(self):
        self.rpc = Presence(self.client_id)
        self.rpc.connect()
        # TODO make state dynamic. for example: display "editing chords" instead of "Current Chord" stuff
        current_chord = None
        last_update = 0

        while self.running:
            try:
                new_chord = self.update_queue.get_nowait()
                current_chord = new_chord
            except queue.Empty:
                pass

            now = time.time()
            if current_chord and now - last_update > 15:
                # TODO add translated strings
                self.rpc.update(state=f"Current chord: {current_chord}")
                last_update = now
            
            time.sleep(1)
