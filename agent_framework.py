from typing import Optional, Dict, Any, List, Callable
from pydantic import BaseModel, ValidationError
import json
import logging
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")



# BUILDING BLOCK 1: INTELLIGENCE

class Intelligence:
    """This handles AI reasoning and makes decision"""
    
    def _init_(self, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_decision(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate AI response"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content

    def structured_output(self, prompt: str, response_model: type[BaseModel], system_prompt: Optional[str] = None) -> BaseModel:
        """Generate structured output using Pydantic model"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=response_model
        )

        return response.choices[0].message.parsed



# BUILDING BLOCK 2: MEMORY

class Memory:
    """Stores and retrieves conversation history"""
    
    def _init_(self, max_history: int = 100):
        self.conversation_history: List[Dict[str, Any]] = []
        self.long_term_storage: Dict[str, Any] = {}
        self.max_history = max_history

    def add_interaction(self, user_input: str, agent_response: str, metadata: Optional[Dict] = None):
        """Store an interaction in memory"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }

        self.conversation_history.append(interaction)
        
        # Keep only recent conversation history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

    def get_context(self, last_n: Optional[int] = None) -> str:
        """Get conversation context as a string"""
        history = self.conversation_history[-(last_n or len(self.conversation_history)):]

        context_parts = []
        for interaction in history:
            context_parts.append(f"User: {interaction['user_input']}")
            context_parts.append(f"Agent: {interaction['agent_response']}")
        
        return "\n".join(context_parts)

    def store_fact(self, key: str, value: Any):
        """Stores long-term information"""
        self.long_term_storage[key] = value

    def retrieve_fact(self, key: str) -> Optional[Any]:
        """Retrieve stored information"""
        return self.long_term_storage.get(key)

    def clear_short_term(self):
        """Clear conversation history"""
        self.conversation_history.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "conversation_count": len(self.conversation_history),
            "stored_facts": len(self.long_term_storage),
            "memory_keys": list(self.long_term_storage.keys())
        }



# BUILDING BLOCK 3: TOOLS

class Tool:
    """Base class for agent tools"""
    
    def _init_(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> Any:
        """Execute the tool - override in subclasses"""
        raise NotImplementedError("Tool must implement execute method.")


class ToolRegistry:
    """Takes care of available tools for the agent"""
    
    def _init_(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute tool by name"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        tool = self.tools[tool_name]
        print(f" Executing tool: {tool_name}")

        try:
            result = tool.execute(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_tool_description(self) -> str:
        """Get description of all available tools"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")

        return "\n".join(descriptions)

    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())



# BUILDING BLOCK 4: VALIDATION
class ValidationSchema:
    """Handles data validation"""
    
    def _init_(self):
        self.schemas: Dict[str, type[BaseModel]] = {}

    def register_schema(self, name: str, schema: type[BaseModel]):
        """Register a validation schema"""
        self.schemas[name] = schema
        print(f" Registered schema: {name}")

    def validate(self, data: Any, schema_name: str) -> BaseModel:
        """Validates data against a registered schema"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found.")

        schema = self.schemas[schema_name]

        try:
            if isinstance(data, dict):
                validated = schema(**data)
            elif isinstance(data, str):
                data_dict = json.loads(data)
                validated = schema(**data_dict)
            elif isinstance(data, schema):
                validated = data
            else:
                raise ValueError(f"Cannot validate data of type {type(data)}")

            print(f" Validation passed: {schema_name}")
            return validated

        except ValidationError as e:
            print(f" Validation failed: {schema_name}")
            raise e



# BUILDING BLOCK 5: RECOVERY

class Recovery:
    """Handles errors and provides fallback mechanism"""
    
    def _init_(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_log: List[Dict] = []

    def execute_with_retry(self, func: Callable, *args, fallback: Optional[Callable] = None, **kwargs) -> Any:
        """Executes a function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                print(f" Attempt {attempt + 1}/{self.max_retries}")
                result = func(*args, **kwargs)
                print(f" Success on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_error = e
                print(f" Attempt {attempt + 1} failed: {str(e)}")

                self.error_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "function": func._name_,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
        
        
        print(f" All {self.max_retries} attempts failed.")

        if fallback:
            print("Executing fallback...")
            try:
                return fallback(*args, **kwargs)
            except Exception as e:
                print(f"Fallback also failed: {str(e)}")

        raise last_error

    def graceful_failure(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Return a graceful failure response"""
        return {
            "status": "error",
            "message": "I ran into an issue and could not finish the task",
            "error_type": type(error)._name_,
            "context": context,
            "suggestion": "Please try rephrasing your request or try again later"
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            "total_errors": len(self.error_log),
            "recent_errors": self.error_log[-5:]
        }



# BUILDING BLOCK 6: FEEDBACK CONTROL

class FeedbackControl:
    """Manages human-in-the-loop approval workflows"""
    
    def _init_(self, auto_approve_threshold: float = 0.0):
        self.auto_approve_threshold = auto_approve_threshold
        self.approval_log: List[Dict] = []

    def requires_approval(self, action: str, confidence: float = 1.0, risk_level: str = "low") -> bool:
        """Determines if an action requires human approval"""
        # High risk always requires approval
        if risk_level in ["high", "critical"]:
            return True

        # Low confidence requires approval
        if confidence < self.auto_approve_threshold:
            return True
        
        return False

    def request_approval(self, action: str, details: Dict[str, Any], confidence: float = 1.0) -> bool:
        """Request human approval for an action to be taken"""
        print("\n" + "=" * 60)
        print(" HUMAN APPROVAL REQUIRED")
        print("=" * 60)
        print(f"Action: {action}")
        print(f"Confidence: {confidence * 100:.1f}%")
        print(f"\nDetails:")
        for key, value in details.items():
            print(f"  {key}: {value}")
        print("=" * 60)

        response = input("Approve this action? (y/n): ").strip().lower()
        approved = response.startswith('y')

        self.approval_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "confidence": confidence,
            "approved": approved
        })

        if approved:
            print(" Action approved by human")
        else:
            print("Action rejected by human")

        return approved

    def get_approval_history(self) -> List[Dict]:
        """Get history of approval decisions"""
        return self.approval_log



# THE AGENT CLASS

class Agent:
    """Universal AI Agent with all 6 building blocks"""
    
    def _init_(self, name: str, system_prompt: str, model: str = "gpt-4o", require_approval: bool = False, max_retries: int = 3, max_history: int = 100):
        self.name = name
        self.system_prompt = system_prompt
        self.require_approval = require_approval
        
        print(f"\n Initializing Agent: {name}")
        print("=" * 60)
        
        self.intelligence = Intelligence(model=model)
        print("Intelligence initialized")
        
        self.memory = Memory(max_history=max_history)
        print(" Memory initialized")
        
        self.tools = ToolRegistry()
        print("Tools initialized")
        
        self.validation = ValidationSchema()
        print(" Validation initialized")
        
        self.recovery = Recovery(max_retries=max_retries)
        print(" Recovery initialized")
        
        self.feedback = FeedbackControl()
        print(" Feedback Control initialized")
        
        self.logger = logging.getLogger(f"Agent.{name}")
        
        print("=" * 60)
        print(f" Agent '{name}' ready!\n")

    def run(self, user_input: str, use_memory: bool = True, require_approval: Optional[bool] = None) -> str:
        """Main method to process user input through all building blocks"""
        print(f"\n{'=' * 60}")
        print(f"Processing: {user_input[:50]}...")
        print(f"{'=' * 60}\n")

        try:
            context = ""
            if use_memory and len(self.memory.conversation_history) > 0:
                print("Retrieving context from memory...")
                context = self.memory.get_context(last_n=3)
                print(f"   Found {len(self.memory.conversation_history)} previous interactions")

            print("\nGenerating AI response...")

            full_prompt = user_input
            if context:
                full_prompt = f"Previous conversation:\n{context}\n\nCurrent request: {user_input}"

            if self.tools.list_tools():
                tools_info = self.tools.get_tool_description()
                full_prompt += f"\n\nAvailable tools:\n{tools_info}"
                full_prompt += """\n\nTo use a tool, respond with EXACTLY this format:
USE_TOOL: tool_name
PARAMS: param1=value1, param2=value2

Example:
USE_TOOL: get_weather
PARAMS: city=Lagos

After using a tool, provide a natural response to the user."""

            response = self.recovery.execute_with_retry(
                self.intelligence.generate_decision,
                prompt=full_prompt,
                system_prompt=self.system_prompt,
                temperature=0.7
            )

            print(f"   Response generated ({len(response)} chars)")

            # Check if AI wants to use a tool
            if "USE_TOOL:" in response:
                lines = response.split('\n')
                tool_name = None
                params = {}

                for line in lines:
                    if line.startswith("USE_TOOL:"):
                        tool_name = line.replace("USE_TOOL:", "").strip()
                    elif line.startswith("PARAMS:"):
                        params_str = line.replace("PARAMS:", "").strip()
                        for param in params_str.split(','):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                params[key.strip()] = value.strip()

                if tool_name:
                    print(f"\nAI requested tool: {tool_name}")
                    print(f"   Parameters: {params}")

                    try:
                        tool_result = self.execute_tool(tool_name, **params)

                        final_prompt = f"""Original user request: {user_input}

Tool used: {tool_name}
Tool result: {json.dumps(tool_result, indent=2)}

Based on this data, provide a clear, natural language response to the user.
Don't mention the tool or technical details - just give them the information they asked for."""

                        response = self.recovery.execute_with_retry(
                            self.intelligence.generate_decision,
                            prompt=final_prompt,
                            system_prompt=self.system_prompt,
                            temperature=0.7
                        )
                    except Exception as e:
                        response = f"I tried to get that information but encountered an error: {str(e)}"

            needs_approval = require_approval if require_approval is not None else self.require_approval

            if needs_approval:
                print("\n Checking if human approval required...")
                approved = self.feedback.request_approval(
                    action="Generate response",
                    details={
                        "user_input": user_input,
                        "response_preview": response[:100] + "..."
                    },
                    confidence=0.85
                )

                if not approved:
                    print("\n Response rejected by human")
                    return "Response was not approved. Please try a different approach."

            if use_memory:
                print("\n Storing interaction in memory...")
                self.memory.add_interaction(
                    user_input=user_input,
                    agent_response=response
                )

            print("\n Processing complete!")
            print(f"{'=' * 60}\n")

            return response

        except Exception as e:
            print(f"\n Error encountered: {type(e)._name_}")
            error_response = self.recovery.graceful_failure(e, context="run method")
            return json.dumps(error_response, indent=2)

    def register_tool(self, tool: Tool):
        """Register a new tool for the agent"""
        self.tools.register(tool)

    def register_schema(self, name: str, schema: type[BaseModel]):
        """Register a validation schema"""
        self.validation.register_schema(name, schema)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        return self.tools.execute(tool_name, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and statistics"""
        return {
            "name": self.name,
            "memory": self.memory.get_summary(),
            "tools": self.tools.list_tools(),
            "errors": self.recovery.get_error_summary(),
            "approvals": len(self.feedback.approval_log)
        }