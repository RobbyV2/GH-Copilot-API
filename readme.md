# GH-Copilot-API

`GH-Copilot-API` is a reverse engineered GitHub Copilot API, for use with OpenAI API Compatible services.

Please make sure to follow GitHub copilot TOS, and try to stick to coding-related tasks, as there is a non-zero chance of being permanently restricted from using Copilot.

## Setup

1. Get the "refresh token"

   The refresh token is pretty much your account token, but in this case it's restricted to Copilot use.

    - Run the following command and note down the returned `device_code` and `user_code`.:

    ```bash
    # 01ab8ac9400c4e429b23 is the client_id for VS Code
    curl https://github.com/login/device/code -X POST -d 'client_id=01ab8ac9400c4e429b23&scope=user:email'
    ```

    - Open <https://github.com/login/device/> and enter the `user_code`.

    - Replace `YOUR_DEVICE_CODE` with the `device_code` obtained earlier and run:

    ```bash
    curl https://github.com/login/oauth/access_token -X POST -d 'client_id=01ab8ac9400c4e429b23&scope=user:email&device_code=YOUR_DEVICE_CODE&grant_type=urn:ietf:params:oauth:grant-type:device_code'
    ```

    - Note down the `access_token` starting with `gho_`.

2. Install and configure

    ```bash
    git clone https://github.com/RobbyV2/GH-Copilot-API.git
    cd GH-Copilot-API
    poetry install
    cp config.json.example config.json
    # Edit config.json with your refresh token, host, port, and auth tokens.
    ```

3. Run

    ```bash
    poetry run python -m gh_copilot_api.main
    ```

    The server will start using the host and port specified in your config.json.

## Use

Any standard OpenAI API compatible service should now work with the exposed API. This works for services like Open WebUI, and Cline.

## Notes

- Despite some of the GitHub Copilot models having vision capabilities, GitHub does not provide any direct way to interface with these capabilities.
