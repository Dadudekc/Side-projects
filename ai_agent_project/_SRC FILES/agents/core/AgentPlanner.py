from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentPlanner:
    """
    The AgentPlanner class organizes tasks by dividing them into prioritized subtasks and creating milestones
    based on customizable criteria or predefined intervals.
    """

    def solve_task(self, task: str, priority: Optional[str] = "Medium", milestone_criteria: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Plans the main task by dividing it into subtasks with assigned priorities and identifying milestones.

        Args:
            task (str): The primary task to organize.
            priority (Optional[str]): Priority level for subtasks (default is 'Medium').
            milestone_criteria (Optional[str]): Keyword to designate specific subtasks as milestones.

        Returns:
            Dict[str, List[Dict[str, str]]]: Contains 'subtasks' with priorities and 'milestones'.
        """
        logger.info(f"Starting task planning for: '{task}' with priority: {priority}")
        
        subtasks = self.divide_task(task, priority)
        milestones = self.generate_milestones(subtasks, milestone_criteria)

        result = {
            'subtasks': subtasks,
            'milestones': milestones
        }
        logger.debug(f"Completed task planning with result: {result}")
        return result

    def divide_task(self, task: str, priority: str) -> List[Dict[str, str]]:
        """
        Splits the main task into a list of subtasks, each assigned a specified priority.

        Args:
            task (str): The main task to split.
            priority (str): Priority level for each subtask.

        Returns:
            List[Dict[str, str]]: List of subtasks with their assigned priorities.
        """
        subtasks = [{'task': subtask.strip(), 'priority': priority} 
                    for subtask in task.split('. ') if subtask.strip()]
        logger.debug(f"Divided task into subtasks: {subtasks}")
        return subtasks

    def generate_milestones(self, subtasks: List[Dict[str, str]], milestone_criteria: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Identifies milestones among subtasks based on the criteria or default settings.

        Args:
            subtasks (List[Dict[str, str]]): List of subtasks with assigned priorities.
            milestone_criteria (Optional[str]): Keyword for defining milestones.

        Returns:
            List[Dict[str, str]]: List of milestone subtasks.
        """
        if milestone_criteria:
            milestones = [subtask for subtask in subtasks if milestone_criteria in subtask['task']]
            logger.debug(f"Milestones selected based on criteria '{milestone_criteria}': {milestones}")
        else:
            milestones = [subtasks[i] for i in range(2, len(subtasks), 3)]
            logger.debug(f"Default milestone selection (every third task): {milestones}")

        return milestones

if __name__ == "__main__":
    # Example usage of the AgentPlanner
    planner = AgentPlanner()
    task_description = "Initialize the project environment. Set up the database. Develop the API. Integrate frontend and backend. Run initial tests. Deploy to staging."
    result = planner.solve_task(task_description, priority="High", milestone_criteria="Deploy")
    print("Planned Subtasks and Milestones:", result)
