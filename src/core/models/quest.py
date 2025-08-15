from pydantic import BaseModel
from enum import Enum
from typing import List


class QuestStatus(Enum):
    """Enumeration of quest statuses."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Quest(BaseModel):
    model_config = {"use_enum_values": True}
    """Quest data class with fields for title, description, objectives, and status."""
    id: str
    title: str
    description: str
    objectives: List[str]  # List of objectives to complete
    status: QuestStatus = QuestStatus.NOT_STARTED
    experience_reward: int = 0
    gold_reward: int = 0
    item_rewards: List[str] = []  # List of item IDs as rewards

    def update_status(self, new_status: QuestStatus):
        """Update the quest status."""
        self.status = new_status

    def add_objective(self, objective: str):
        """Add a new objective to the quest."""
        self.objectives.append(objective)

    def complete_objective(self, objective: str) -> bool:
        """Mark an objective as complete. Returns True if all objectives are complete."""
        # In a more complex implementation, we might track which objectives are completed
        # For now, we'll just check if all objectives are met when the quest is turned in
        return self.all_objectives_complete()

    def all_objectives_complete(self) -> bool:
        """Check if all objectives are complete."""
        # In a more complex implementation, we would check the actual status of each objective
        # For now, we'll assume the quest giver will verify the objectives
        return self.status == QuestStatus.COMPLETED

    def is_completed(self) -> bool:
        """Check if the quest is completed."""
        return self.status == QuestStatus.COMPLETED
