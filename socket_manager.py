from threading import Event
from collections import defaultdict

class SocketManager:
    def __init__(self):
        self.call_status = defaultdict(dict)
        # Initialize call_events as defaultdict of Events
        self.call_events = defaultdict(Event)

    def mark_processing(self, call_sid):
        """Initialize processing state and create Event for this call"""
        self.call_status[call_sid]['status'] = 'processing'
        # Create new Event for this call
        self.call_events[call_sid] = Event()

    def mark_completed(self, call_sid, transcription):
        """Mark processing as complete and signal waiting processes"""
        self.call_status[call_sid]['status'] = 'completed'
        self.call_status[call_sid]['transcription'] = transcription
        # Signal completion to any waiting processes
        if call_sid in self.call_events:
            self.call_events[call_sid].set()

    def get_transcription(self, call_sid):
        return self.call_status.get(call_sid, {}).get('transcription')

    def clear_call(self, call_sid):
        if call_sid in self.call_status:
            del self.call_status[call_sid]
        if call_sid in self.call_events:
            del self.call_events[call_sid]

socket_manager = SocketManager()