import json
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path


import httpx
import pytest
from respx import MockRouter

import litellm
from litellm import Choices, Message, ModelResponse
from litellm import completion


@pytest.mark.respx
def test_completion_nvidia_nim(respx_mock: MockRouter):
    litellm.set_verbose = True
    mock_response = ModelResponse(
        id="cmpl-mock",
        choices=[Choices(message=Message(content="Mocked response", role="assistant"))],
        created=int(datetime.now().timestamp()),
        model="databricks/dbrx-instruct",
    )
    model_name = "nvidia_nim/databricks/dbrx-instruct"

    mock_request = respx_mock.post(
        "https://integrate.api.nvidia.com/v1/chat/completions"
    ).mock(return_value=httpx.Response(200, json=mock_response.dict()))
    try:
        response = completion(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in Boston today in Fahrenheit?",
                }
            ],
            presence_penalty=0.5,
            frequency_penalty=0.1,
        )
        # Add any assertions here to check the response
        print(response)
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

        assert mock_request.called
        request_body = json.loads(mock_request.calls[0].request.content)

        print("request_body: ", request_body)

        assert request_body == {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather like in Boston today in Fahrenheit?",
                }
            ],
            "model": "databricks/dbrx-instruct",
            "frequency_penalty": 0.1,
            "presence_penalty": 0.5,
        }
    except litellm.exceptions.Timeout as e:
        pass
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
