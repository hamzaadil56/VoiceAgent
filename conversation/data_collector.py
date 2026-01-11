"""Data Collector - Extract and store conversation data."""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from database import create_response, get_responses_by_conversation


class DataCollector:
    """
    Collect and store data from conversations.
    
    Extracts questions and answers from conversations and stores them
    in a structured format for later analysis and export.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data collector.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        
        # Patterns to detect questions
        self.question_patterns = [
            r'\?$',  # Ends with question mark
            r'^(what|who|where|when|why|how|can|could|would|should|do|does|did|is|are|was|were)\b',  # Question words
            r'\btell me\b',  # "Tell me about..."
            r'\bdescribe\b',  # "Describe..."
            r'\bexplain\b',  # "Explain..."
        ]
    
    def collect(
        self,
        conversation_id: int,
        user_message: str,
        agent_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Collect a response from the conversation.
        
        Args:
            conversation_id: Conversation ID
            user_message: User's message (answer)
            agent_message: Agent's previous message (question, optional)
            metadata: Additional metadata
            
        Returns:
            Response ID
        """
        # Detect if agent_message is a question
        question = None
        if agent_message:
            if self._is_question(agent_message):
                question = agent_message
        
        # Create response in database
        response = create_response(
            self.db_session,
            conversation_id=conversation_id,
            answer=user_message,
            question=question,
            metadata=metadata,
        )
        
        return response.id
    
    def collect_qa_pair(
        self,
        conversation_id: int,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Collect a question-answer pair.
        
        Args:
            conversation_id: Conversation ID
            question: The question
            answer: The answer
            metadata: Additional metadata
            
        Returns:
            Response ID
        """
        response = create_response(
            self.db_session,
            conversation_id=conversation_id,
            answer=answer,
            question=question,
            metadata=metadata,
        )
        
        return response.id
    
    def _is_question(self, text: str) -> bool:
        """
        Detect if text is a question.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a question
        """
        text = text.strip().lower()
        
        for pattern in self.question_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_conversation_data(
        self,
        conversation_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get all collected data for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of response dictionaries
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        return [response.to_dict() for response in responses]
    
    def extract_structured_data(
        self,
        conversation_id: int,
    ) -> Dict[str, Any]:
        """
        Extract structured data from a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with structured data
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        
        structured_data = {
            "conversation_id": conversation_id,
            "total_responses": len(responses),
            "questions": [],
            "answers": [],
            "qa_pairs": [],
            "timestamps": [],
        }
        
        for response in responses:
            if response.question:
                structured_data["questions"].append(response.question)
                structured_data["qa_pairs"].append({
                    "question": response.question,
                    "answer": response.answer,
                    "timestamp": response.timestamp.isoformat(),
                })
            
            structured_data["answers"].append(response.answer)
            structured_data["timestamps"].append(response.timestamp.isoformat())
        
        return structured_data
    
    def get_summary_stats(
        self,
        conversation_id: int,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with summary statistics
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        
        if not responses:
            return {
                "total_responses": 0,
                "total_questions": 0,
                "avg_answer_length": 0,
                "first_response": None,
                "last_response": None,
            }
        
        questions_count = sum(1 for r in responses if r.question)
        total_answer_length = sum(len(r.answer) for r in responses)
        avg_answer_length = total_answer_length / len(responses) if responses else 0
        
        return {
            "total_responses": len(responses),
            "total_questions": questions_count,
            "avg_answer_length": round(avg_answer_length, 2),
            "first_response": responses[0].timestamp.isoformat() if responses else None,
            "last_response": responses[-1].timestamp.isoformat() if responses else None,
        }


class ConversationTracker:
    """
    Track conversation flow and extract data in real-time.
    
    This is a helper class that can be used to track the conversation
    as it happens, maintaining state between messages.
    """
    
    def __init__(self, conversation_id: int, data_collector: DataCollector):
        """
        Initialize conversation tracker.
        
        Args:
            conversation_id: Conversation ID
            data_collector: DataCollector instance
        """
        self.conversation_id = conversation_id
        self.data_collector = data_collector
        
        # Track the last agent message (potential question)
        self.last_agent_message: Optional[str] = None
        self.message_history: List[Dict[str, str]] = []
    
    def add_user_message(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a user message and collect data.
        
        Args:
            message: User's message
            metadata: Additional metadata
        """
        # Store in history
        self.message_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Collect data with the last agent message as the question
        self.data_collector.collect(
            conversation_id=self.conversation_id,
            user_message=message,
            agent_message=self.last_agent_message,
            metadata=metadata,
        )
    
    def add_agent_message(self, message: str):
        """
        Add an agent message.
        
        Args:
            message: Agent's message
        """
        # Store in history
        self.message_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Store as last agent message (potential question for next response)
        self.last_agent_message = message
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.message_history.copy()
    
    def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        Get all collected data for this conversation.
        
        Returns:
            List of response dictionaries
        """
        return self.data_collector.get_conversation_data(self.conversation_id)
