class InvalidUserInputError(Exception):
    """Raised when user input is invalid"""

    def __init__(self, message="User input invalid"):
        self.message = message
        super().__init__(self.message)


def transform_user_input_to_binary(user_input: str) -> bool:
    user_input = user_input.lower()
    if user_input == "y":
        return True
    elif user_input == "n":
        return False
    else:
        raise InvalidUserInputError(f"Input {user_input} not valid. Choose 'y' or 'n'.")
