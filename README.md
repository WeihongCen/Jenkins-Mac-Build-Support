# Jenkins Mac Build Support
Jenkins Mac Build Support is a discord bot for remotely triggering the Jenkins Saleblazers Mac build

# Local Hosting
To run the bot, you need to run the following commands in terminal
```Zsh
source env/bin/activate
cd /Users/airstrafeconference/Documents/GitHub/Jenkins-Mac-Build-Support
python3 main.py 
```

# Commands
## /mac_status ```build_id```
```build_id``` -1 returns the latest build

Get the build status.

## /mac_log ```build_id```
```build_id``` -1 returns the latest build

Get the build console log and uploads it as a file to a Google Drive folder.

## /mac_start_build
Build the latest Saleblazers Default Build.

## /mac_abort_build
Abort the latest Saleblazers Default Build.


# .env Tokens/IDs
## DISCORD_TOKEN
Token from William Cen's Discord bot. Contact 21cenweihong@gmail.com if you lost the token.

## API_TOKEN
Token for a Jenkins user to make authenticated CLI or REST API calls. <br/>
Location: Jenkins main page -> Manage Jenkins -> Manage Users -> select a user (jenkins_as) -> Configure -> API Token

## BUILD_TOKEN
Token granting access for a build to be triggered remotely. <br/>
Location: Jenkins main page -> select one of the builds -> Configure -> Build Triggers -> Trigger builds remotely -> Authentication Token

## DEFAULT_BUILD_LOG_FOLDER_ID
The ID of the Google Drive folder used to store the build logs. The folders are currently under the william.cen@airstrafeinteractive.com account.


# Python Dependencies
These packages need to be installed before running the bot
```
dotenv
discord
requests
pydrive
```
