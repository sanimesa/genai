import io
from contextlib import redirect_stdout
from pydantic import Field
from typing_extensions import override
import pandas as pd
from typing import Any
from pydantic.fields import PrivateAttr

from google.adk.code_executors import BaseCodeExecutor
from google.adk.agents.invocation_context import InvocationContext
from google.adk.code_executors.code_execution_utils import CodeExecutionInput
from google.adk.code_executors.code_execution_utils import CodeExecutionResult

class CustomUnsafeLocalCodeExecutor(BaseCodeExecutor):
    """A code executor that allows a DataFrame `df` to be accessible in the code execution context."""

    # Overrides the BaseCodeExecutor attribute: this executor cannot be stateful.
    stateful: bool = Field(default=False, frozen=True, exclude=True)
    # Overrides the BaseCodeExecutor attribute: this executor cannot optimize_data_file.
    optimize_data_file: bool = Field(default=False, frozen=True, exclude=True)

    _df: pd.DataFrame = PrivateAttr()

    def __init__(self, df: pd.DataFrame, **kwargs: Any):
        """Initializes the DataFrameUnsafeLocalCodeExecutor with a DataFrame.
        
        Args:
            df: The DataFrame to make available as 'df' during code execution.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        if 'stateful' in kwargs and kwargs['stateful']:
            raise ValueError('Cannot set `stateful=True` in DataFrameUnsafeLocalCodeExecutor.')
        if 'optimize_data_file' in kwargs and kwargs['optimize_data_file']:
            raise ValueError(
                'Cannot set `optimize_data_file=True` in DataFrameUnsafeLocalCodeExecutor.'
            )
        super().__init__(**kwargs)
        self._df = df

    @override
    def execute_code(
        self,
        invocation_context: InvocationContext,
        code_execution_input: CodeExecutionInput,
    ) -> CodeExecutionResult:
        """Executes the provided code with access to the DataFrame `df`."""
        output = ''
        error = ''
        try:
            # Prepare the execution environment with 'df' available in globals
            globals_dict = {'df': self._df}
            locals_dict = {}
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exec(code_execution_input.code, globals_dict, locals_dict)
            output = stdout.getvalue()
        except Exception as e:
            error = str(e)
        # Collect the final result
        return CodeExecutionResult(
            stdout=output,
            stderr=error,
            output_files=[],
        )