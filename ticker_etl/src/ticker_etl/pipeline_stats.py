import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid


class PipelineRun:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = None
        self.end_time = None
        self.storage_dir = Path("/storage")
        
    def __enter__(self):
        self.start_time = datetime.now()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO we want to set the status to failed if there is an exception
        self.end_time = datetime.now()
        self.persist()

    @property
    def pth_dir(self):
        pth = Path.cwd() / "storage" / "runs" / self.run_id
        pth.mkdir(parents=True, exist_ok=True)
        return pth

    @property
    def pth_file(self):
        return self.pth_dir / "this.json"
        
    @property
    def duration(self) -> float:
        """Calculate duration in seconds if both start and end times are set"""
        return (self.end_time - self.start_time).total_seconds()
    
    def persist(self):        
        run_stats = {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration,
            "status": "completed"
        }
        
        with self.pth_file.open("w", encoding="utf-8") as f:
            json.dump(run_stats, f)