# GH-Copilot-API

`GH-Copilot-API` is a reverse engineered GitHub Copilot API, for use with OpenAI API Compatible services.

Please make sure to follow GitHub copilot TOS, and try to stick to coding-related tasks, as there is a non-zero chance of being permanently restricted from using Copilot.

## Setup

- Bare metal installation:

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

      Alternatively, use the `token-refresh.sh` script to automate the above.

  2. Install and configure

      ```bash
      git clone https://github.com/RobbyV2/GH-Copilot-API.git
      cd GH-Copilot-API
      poetry install
      # Choose to use config.json or environment variables
      cp config.json.example config.json
      cp .env.example .env
      # Fill in the values for either one (or specify env at runtime)
      ```

  3. Run

      ```bash
      poetry run python -m gh_copilot_api.main
      ```

      The server will start using the host and port specified in your config.json.

- Docker Instructions 🐋

    ```bash
    git clone https://github.com/RobbyV2/GH-Copilot-API.git
    cd GH-Copilot-API
    # Run the server. Ensure you either have all the config.json.example parameters in a .env file or pass it as an environment variable.
    # Contained in .env.example
    docker-compose up --build
    ```

## Use

Any standard OpenAI API compatible service should now work with the exposed API. This works for services like Open WebUI, and Cline.

## Notes

- Despite some of the GitHub Copilot models having vision capabilities, GitHub does not provide any direct way to interface with these capabilities.
- There isn't great error handling for errors beyond rate limits.

## Credits

Creators of [copilot-more](https://github.com/jjleng/copilot-more/)