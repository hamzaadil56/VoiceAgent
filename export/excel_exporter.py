"""Excel Exporter - Export conversation data to Excel/CSV."""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from io import BytesIO
from sqlalchemy.orm import Session

from database import (
    get_agent,
    get_all_responses_with_agent_info,
    get_conversations_by_agent,
    get_responses_by_conversation,
)


class ExcelExporter:
    """
    Export conversation data to Excel/CSV format.
    
    Similar to Google Forms export functionality.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize exporter.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
    
    def export_agent_data(
        self,
        agent_id: int,
        output_format: str = "excel",
    ) -> bytes:
        """
        Export all data for an agent to Excel/CSV.
        
        Args:
            agent_id: Agent ID
            output_format: 'excel' or 'csv'
            
        Returns:
            File bytes
        """
        # Get agent info
        agent = get_agent(self.db_session, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get all responses with agent info
        data = get_all_responses_with_agent_info(self.db_session, agent_id)
        
        if not data:
            # Return empty DataFrame
            df = pd.DataFrame(columns=[
                "Conversation ID",
                "Session ID",
                "Mode",
                "Question",
                "Answer",
                "Timestamp",
            ])
        else:
            # Convert to DataFrame
            rows = []
            for item in data:
                response = item["response"]
                conversation = item["conversation"]
                
                rows.append({
                    "Conversation ID": conversation["id"],
                    "Session ID": conversation["session_id"],
                    "Mode": conversation["mode"],
                    "Question": response["question"] or "",
                    "Answer": response["answer"],
                    "Timestamp": response["timestamp"],
                })
            
            df = pd.DataFrame(rows)
        
        # Export to bytes
        if output_format == "csv":
            buffer = BytesIO()
            df.to_csv(buffer, index=False, encoding='utf-8')
            buffer.seek(0)
            return buffer.getvalue()
        else:
            # Excel format
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Responses', index=False)
                
                # Add agent info sheet
                agent_info = pd.DataFrame([{
                    "Agent Name": agent.name,
                    "Description": agent.description,
                    "Category": agent.category,
                    "Total Conversations": len(get_conversations_by_agent(self.db_session, agent_id)),
                    "Total Responses": len(df),
                    "Created At": agent.created_at.isoformat() if agent.created_at else "",
                    "Export Date": datetime.utcnow().isoformat(),
                }])
                agent_info.to_excel(writer, sheet_name='Agent Info', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
    
    def export_conversation_data(
        self,
        conversation_id: int,
        output_format: str = "excel",
    ) -> bytes:
        """
        Export data for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            output_format: 'excel' or 'csv'
            
        Returns:
            File bytes
        """
        # Get responses
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        
        if not responses:
            df = pd.DataFrame(columns=["Question", "Answer", "Timestamp"])
        else:
            rows = []
            for response in responses:
                rows.append({
                    "Question": response.question or "",
                    "Answer": response.answer,
                    "Timestamp": response.timestamp.isoformat(),
                })
            
            df = pd.DataFrame(rows)
        
        # Export to bytes
        if output_format == "csv":
            buffer = BytesIO()
            df.to_csv(buffer, index=False, encoding='utf-8')
            buffer.seek(0)
            return buffer.getvalue()
        else:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Conversation', index=False)
            buffer.seek(0)
            return buffer.getvalue()
    
    def export_wide_format(
        self,
        agent_id: int,
        output_format: str = "excel",
    ) -> bytes:
        """
        Export in wide format (Google Forms style).
        
        Each row is a conversation, columns are questions.
        
        Args:
            agent_id: Agent ID
            output_format: 'excel' or 'csv'
            
        Returns:
            File bytes
        """
        # Get agent info
        agent = get_agent(self.db_session, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get all conversations
        conversations = get_conversations_by_agent(self.db_session, agent_id)
        
        if not conversations:
            df = pd.DataFrame()
        else:
            # Build wide format data
            rows = []
            all_questions = set()
            
            # First pass: collect all unique questions
            conversation_data = {}
            for conv in conversations:
                responses = get_responses_by_conversation(self.db_session, conv.id)
                qa_dict = {}
                
                for i, response in enumerate(responses, 1):
                    question = response.question or f"Response {i}"
                    all_questions.add(question)
                    qa_dict[question] = response.answer
                
                conversation_data[conv.id] = {
                    "conversation": conv,
                    "qa_dict": qa_dict,
                }
            
            # Sort questions for consistent column order
            sorted_questions = sorted(all_questions)
            
            # Second pass: build rows
            for conv_id, data in conversation_data.items():
                conv = data["conversation"]
                qa_dict = data["qa_dict"]
                
                row = {
                    "Conversation ID": conv.id,
                    "Session ID": conv.session_id,
                    "Mode": conv.mode,
                    "Started At": conv.started_at.isoformat(),
                    "Ended At": conv.ended_at.isoformat() if conv.ended_at else "",
                }
                
                # Add answers for each question
                for question in sorted_questions:
                    row[question] = qa_dict.get(question, "")
                
                rows.append(row)
            
            df = pd.DataFrame(rows)
        
        # Export to bytes
        if output_format == "csv":
            buffer = BytesIO()
            df.to_csv(buffer, index=False, encoding='utf-8')
            buffer.seek(0)
            return buffer.getvalue()
        else:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Responses (Wide)', index=False)
                
                # Add agent info
                agent_info = pd.DataFrame([{
                    "Agent Name": agent.name,
                    "Description": agent.description,
                    "Category": agent.category,
                    "Total Conversations": len(conversations),
                    "Export Date": datetime.utcnow().isoformat(),
                }])
                agent_info.to_excel(writer, sheet_name='Agent Info', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
    
    def export_to_file(
        self,
        agent_id: int,
        output_path: str,
        output_format: str = "excel",
        wide_format: bool = False,
    ):
        """
        Export data to file.
        
        Args:
            agent_id: Agent ID
            output_path: Output file path
            output_format: 'excel' or 'csv'
            wide_format: Use wide format (Google Forms style)
        """
        if wide_format:
            data = self.export_wide_format(agent_id, output_format)
        else:
            data = self.export_agent_data(agent_id, output_format)
        
        with open(output_path, "wb") as f:
            f.write(data)


def export_agent_data(
    db_session: Session,
    agent_id: int,
    output_format: str = "excel",
    wide_format: bool = False,
) -> bytes:
    """
    Convenience function to export agent data.
    
    Args:
        db_session: Database session
        agent_id: Agent ID
        output_format: 'excel' or 'csv'
        wide_format: Use wide format
        
    Returns:
        File bytes
    """
    exporter = ExcelExporter(db_session)
    
    if wide_format:
        return exporter.export_wide_format(agent_id, output_format)
    else:
        return exporter.export_agent_data(agent_id, output_format)


def export_conversation_data(
    db_session: Session,
    conversation_id: int,
    output_format: str = "excel",
) -> bytes:
    """
    Convenience function to export conversation data.
    
    Args:
        db_session: Database session
        conversation_id: Conversation ID
        output_format: 'excel' or 'csv'
        
    Returns:
        File bytes
    """
    exporter = ExcelExporter(db_session)
    return exporter.export_conversation_data(conversation_id, output_format)


def generate_filename(agent_name: str, output_format: str = "excel") -> str:
    """
    Generate a filename for export.
    
    Args:
        agent_name: Agent name
        output_format: 'excel' or 'csv'
        
    Returns:
        Filename
    """
    # Sanitize agent name
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in agent_name)
    safe_name = safe_name.replace(' ', '_')
    
    # Add timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Add extension
    extension = "xlsx" if output_format == "excel" else "csv"
    
    return f"{safe_name}_export_{timestamp}.{extension}"

