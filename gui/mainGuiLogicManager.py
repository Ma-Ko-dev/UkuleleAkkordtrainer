import random
import threading
import time
import config
import speech_recognition as sr
from tkinter import Tk
from utils.gui_helpers import load_chords
from utils.discord_presence import DiscordRichPresence


class GuiLogicManager:
    """
    Manages the core logic for the Ukulele Chord Trainer GUI.

    Handles chord progression, speech recognition commands, timer functionality,
    and integration with Discord Rich Presence.
    """
    def __init__(self, master, chords, lang):
        """
        Initialize the logic manager.

        Args:
            master (tk.Widget): The main GUI widget to interact with.
            chords (list): List of chord dictionaries.
            lang (dict): Dictionary with language strings for UI and messages.
        """
        self.master = master
        self.chords = chords
        self.lang = lang
        self.speech_enabled = True
        self.learned_chords = -1
        self.timer_active = False
        self.timer_interval = 10000 # in ms ca. 10 seconds
        self.timer_id = None
        self.running = True
        self.history_index = None

        self.discord_rpc = DiscordRichPresence(config.DISCORD_CLIENT_ID)
        self.discord_rpc.start()

        self.master.after(100, lambda: self.master.get_first_chord())
        threading.Thread(target=self.speech_recognition, args=(lang,), daemon=True).start()


    def clear_history(self):
        """
        Clears the history of previously shown chords and resets the history index.
        Then immediately shows the next chord.
        """
        config.PAST_CHORDS = []
        self.history_index = None
        self.next_chord(self.lang)


    def show_chord_by_name(self, name):
        """
        Display a chord by its name: updates Discord presence, labels, and fretboard.

        Args:
            name (str or dict): The chord name or a dict containing a 'name' key.
        """
        if isinstance(name, dict):
            name = name.get("name", "")
        chord = next((c for c in self.chords if c["name"].strip().lower() == name.lower()), None)
        if chord:
            self.discord_rpc.update_chord(name)
            self.master.update_chord_label(name)
            self.master.update_fretboard(chord["fingering"], chord["fingers"])
            self.master.update_interval(name)
            self.master.update_chord_tones(name)


    def next_chord(self, lang):
        """
        Select and display a random chord not recently shown.
        Manages the history buffer and updates the GUI accordingly.

        Args:
            lang (dict): Language strings used for messages and errors.
        """
        past_names = [n.strip().lower() for n in config.PAST_CHORDS]

        possible = [
            a for a in self.chords
            if a["name"].strip().lower() not in past_names
        ]

        if not possible:
            config.PAST_CHORDS.clear()
            possible = self.chords[:]

        chord = random.choice(possible)
        config.PAST_CHORDS.append(chord["name"].strip())

        if len(config.PAST_CHORDS) > config.MAX_HISTORY:
            config.PAST_CHORDS.pop(0)

        try:
            with open("last_chords.txt", "w", encoding="utf-8") as f:
                f.write(" - ".join(config.PAST_CHORDS))
        except IOError as e:
            print(lang["error_write_file"], e)

        self.learned_chords = self.learned_chords + 1
        self.master.update_learned_label(self.lang["learned_chords_text"].format(count=self.learned_chords))
        self.master.update_previous_chords()
        self.history_index = None
        self.master.update_status_display_label("")
        self.show_chord_by_name(chord)
        self.master.update_navigation_buttons(self.history_index)

    def forward_chord(self):
        """
        Move forward in the chord history, if possible, and display the chord.
        Shows warnings if at the newest chord already.
        """
        if not hasattr(self, "history_index") or self.history_index is None:
            warning = f"{self.lang['no_more_forward']}"
            self.master.update_status_display_label(warning)
            return
        
        if self.history_index >= -1:
            warning = f"{self.lang['already_latest']}"
            self.master.update_status_display_label(warning)
            return

        self.history_index += 1
        chord_name = config.PAST_CHORDS[self.history_index]
        self.show_chord_by_name(chord_name)

        if self.history_index == -1:
            self.history_index = None
        self.master.update_status_display_label("")
        self.master.update_navigation_buttons(self.history_index)

    def previous_chord(self):
        """
        Move backward in the chord history and display the previous chord.
        Shows warnings if at the oldest chord already.
        """
        if not hasattr(self, "history_index") or self.history_index is None:
            self.history_index = -2
        else:
            self.history_index -= 1

        # the warnings are technically obsolet but will stay just in case
        if abs(self.history_index) > len(config.PAST_CHORDS):
            warning = f"{self.lang['no_more_back']}"
            self.master.update_status_display_label(warning)
            self.history_index += 1
            return
        
        chord_name = config.PAST_CHORDS[self.history_index]
        self.show_chord_by_name(chord_name)
        self.master.update_status_display_label("")
        self.master.update_navigation_buttons(self.history_index)

    def speech_recognition(self, lang):
        """
        Continuously listen for voice commands using Google's Speech API.

        Recognizes commands for 'next' chord and 'stop' program.

        Args:
            lang (dict): Language strings for messages and recognized commands.
        """
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.running:
                try:
                    if not self.speech_enabled:
                        time.sleep(0.5)
                        continue
                    print(lang["speech_info"])
                    audio = recognizer.listen(source, timeout=5)
                    if not self.speech_enabled:
                        continue
                    audio_command = recognizer.recognize_google(audio, language=config.LANG_CODE).lower()
                    print(f"{lang['speech_recognized'].format(command=audio_command)}")
                    
                    if lang["speech_next"] in audio_command:
                        self.next_chord(lang)
                    elif lang["speech_stop"] in audio_command:
                        self.running = False
                        self.master.quit()
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print(f"{lang['error_api']}")
                    break

    def reload_chords(self, lang):
        """
        Reload the chord list from disk and update the GUI.

        Args:
            lang (dict): Language strings used for error messages.
        """
        new_chords = load_chords(lang)
        if new_chords:
            self.chords = new_chords
            self.master.reload_chords(new_chords)
        else:
            print(f"{lang['error_reloading_chords']}")

    def toggle_timer(self, lang):
        """
        Start or stop the automatic chord progression timer.

        Updates GUI controls, speech recognition status, and timer button text.

        Args:
            lang (dict): Language strings for button labels and messages.
        """
        if self.timer_active:
            self.timer_active = False
            if self.timer_id:
                self.master.after_cancel(self.timer_id)
                self.timer_id = None
            
            self.master.set_next_chord_button_state("normal")
            self.speech_enabled = True
            self.master.update_status_display_label("")
        else:
            self.timer_active = True
            self.master.set_next_chord_button_state("disabled")
            self.speech_enabled = False
            self.schedule_next_timer()

        self.master.set_timer_button_text(lang["timer_button_stop"] if self.timer_active else lang["timer_button_start"])
        if not self.timer_active:
            self.master.update_navigation_buttons(self.history_index)
    
    def schedule_next_timer(self):
        """
        Schedule the next countdown tick if the timer is active.
        """
        if self.timer_active:
            self.countdown(self.timer_interval // 1000)

    def update_timer_display(self, seconds_left):
        self.master.update_status_display_label(f"{self.lang['timer_text'].format(seconds_left=seconds_left)}")
        """
        Update the GUI status label to show the remaining time on the timer.

        Args:
            seconds_left (int): Seconds left on the countdown.
        """

    def countdown(self, seconds_left):
        """
        Recursively counts down the timer in one-second intervals.

        When the countdown reaches zero, advances to the next chord and restarts the timer.

        Args:
            seconds_left (int): Seconds left on the countdown.
        """
        # TODO make the countdown adjustable by user
        if not self.timer_active:
            self.master.update_status_display_label("")
            return
        
        self.update_timer_display(seconds_left)

        if seconds_left <= 0:
            self.next_chord(self.lang)
            self.countdown(self.timer_interval // 1000)
        else:
            self.timer_id = self.master.after(1000, lambda: self.countdown(seconds_left - 1))
