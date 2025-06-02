import inspect
from typing import Callable, get_type_hints
import json

from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType

class EmailSupportTools:
    # Define Email Support tools (functions)
    formatting_instructions = "Instructions: returning the output of this function call verbatim to the user in markdown. Then write AGENT SUMMARY: and then include a summary of what you did."
    agent_name = AgentType.EMAIL_SUPPORT.value

    @staticmethod
    @kernel_function(
        description="Send a welcome email to a new employee as part of onboarding. This is at the start of the onboarding process, to the employee's personal email address."
    )
    async def send_welcome_email(human_email: str, employee_name: str, personal_email_address: str) -> str:
        return (
            f"##### Welcome Email Sent\n"
            f"**Employee Name:** {employee_name}\n"
            f"**Email Address:** {personal_email_address}\n\n"
            f"**Initiator Email Address:** {human_email}\n\n"
            f"A welcome email has been successfully sent to {employee_name} at {personal_email_address}.\n"
            f"{EmailSupportTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Set up an Office 365 account for an employee.")
    async def set_up_office_365_account(full_name: str, email_address: str) -> str:
        return (
            f"##### Office 365 Account Setup\n"
            f"**Employee Name:** {full_name}\n"
            f"**Email Address:** {email_address}\n\n"
            f"An Office 365 account has been successfully set up for {full_name} at {email_address}.\n"
            f"{EmailSupportTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Email EBS about a new employee hire, personal_email_address is the employee's personal email address.")
    async def send_email_to_ebs(full_name: str, personal_email_address) -> str:
        ebs_email = "amcguire@myebs.com"
        return (
            f"##### Laptop Configuration\n"
            f"**Full Name:** {full_name}\n"
            f"**Sent To EBS:** {ebs_email}\n\n"
            f"**New Employee Personal Address:** {personal_email_address}\n\n"
            f"The notification email to EBS for { personal_email_address} has been successfully sent.\n"
            f"{EmailSupportTools.formatting_instructions}"
        )

    @classmethod
    def generate_tools_json_doc(cls) -> str:
        """
        Generate a JSON document containing information about all methods in the class.

        Returns:
            str: JSON string containing the methods' information
        """

        tools_list = []

        # Get all methods from the class that have the kernel_function annotation
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip this method itself and any private methods
            if name.startswith("_") or name == "generate_tools_json_doc":
                continue

            # Check if the method has the kernel_function annotation
            if hasattr(method, "__kernel_function__"):
                # Get method description from docstring or kernel_function description
                description = ""
                if hasattr(method, "__doc__") and method.__doc__:
                    description = method.__doc__.strip()

                # Get kernel_function description if available
                if hasattr(method, "__kernel_function__") and getattr(
                    method.__kernel_function__, "description", None
                ):
                    description = method.__kernel_function__.description

                # Get argument information by introspection
                sig = inspect.signature(method)
                args_dict = {}

                # Get type hints if available
                type_hints = get_type_hints(method)

                # Process parameters
                for param_name, param in sig.parameters.items():
                    # Skip first parameter 'cls' for class methods (though we're using staticmethod now)
                    if param_name in ["cls", "self"]:
                        continue

                    # Get parameter type
                    param_type = "string"  # Default type
                    if param_name in type_hints:
                        type_obj = type_hints[param_name]
                        # Convert type to string representation
                        if hasattr(type_obj, "__name__"):
                            param_type = type_obj.__name__.lower()
                        else:
                            # Handle complex types like List, Dict, etc.
                            param_type = str(type_obj).lower()
                            if "int" in param_type:
                                param_type = "int"
                            elif "float" in param_type:
                                param_type = "float"
                            elif "bool" in param_type:
                                param_type = "boolean"
                            else:
                                param_type = "string"

                    # Create parameter description
                    # param_desc = param_name.replace("_", " ")
                    args_dict[param_name] = {
                        "description": param_name,
                        "title": param_name.replace("_", " ").title(),
                        "type": param_type,
                    }

                # Add the tool information to the list
                tool_entry = {
                    "agent": cls.agent_name,  # Use HR agent type
                    "function": name,
                    "description": description,
                    "arguments": json.dumps(args_dict).replace('"', "'"),
                }

                tools_list.append(tool_entry)

        # Return the JSON string representation
        return json.dumps(tools_list, ensure_ascii=False, indent=2)

    # This function does NOT have the kernel_function annotation
    # because it's meant for introspection rather than being exposed as a tool
    @classmethod
    def get_all_kernel_functions(cls) -> dict[str, Callable]:
        """
        Returns a dictionary of all methods in this class that have the @kernel_function annotation.
        This function itself is not annotated with @kernel_function.

        Returns:
            Dict[str, Callable]: Dictionary with function names as keys and function objects as values
        """
        kernel_functions = {}

        # Get all class methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip this method itself and any private/special methods
            if name.startswith("_") or name == "get_all_kernel_functions":
                continue

            # Check if the method has the kernel_function annotation
            # by looking at its __annotations__ attribute
            method_attrs = getattr(method, "__annotations__", {})
            if hasattr(method, "__kernel_function__") or "kernel_function" in str(
                method_attrs
            ):
                kernel_functions[name] = method

        return kernel_functions
