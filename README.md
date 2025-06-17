# Kimai Time Tracking Plugin

A StreamController plugin for integrating with Kimai time tracking system.

## Features

- **Start Time Tracking**: Start tracking time for a specific project, activity, and customer
- **Stop Time Tracking**: Stop the currently active time tracking session
- **Global Settings**: Configure Kimai URL and API token once for all actions

## Configuration

### Global Plugin Settings

First, configure the global settings for your Kimai instance:

1. Go to **Settings** → **Plugins**
2. Find **Kimai Time Tracking** and click **Open Settings**
3. Configure:
   - **Kimai URL**: The base URL of your Kimai installation (e.g., `https://kimai.example.com`)
   - **API Token**: Your Kimai API token (can be generated in Kimai under User Settings)

### Action Configuration

#### Start Time Tracking Action

For each Start Time Tracking button, configure:

- **Project ID**: The ID of the project to track time for
- **Activity ID**: The ID of the activity to track time for  
- **Description**: Optional description for the time tracking entry

#### Stop Time Tracking Action

The Stop Time Tracking action uses the global settings automatically - no additional configuration needed.

## Usage

1. **Set up global settings**: Configure Kimai URL and API token in Plugin Settings
2. **Configure Start buttons**: Set project and activity IDs (and optional description) for each Start Time Tracking button
3. **Add Stop button**: Place a Stop Time Tracking button on your deck
4. **Use the buttons**: Press Start to begin tracking time, Stop to end the current session

The buttons will show a green background on success and red background on error.

## Finding IDs

To find the Project and Activity IDs in Kimai:

- **Projects**: Go to Projects in Kimai, the ID is shown in the URL or project list
- **Activities**: Go to Activities in Kimai, the ID is shown in the URL or activity list  

Alternatively, you can use Kimai's API endpoints to list available IDs:
- `/api/projects` - List all projects
- `/api/activities` - List all activities

## Requirements

- Kimai installation with API access
- Valid API token from Kimai
- Network access to your Kimai instance

For more information checkout [the StreamController docs](https://streamcontroller.github.io/docs/latest/).
