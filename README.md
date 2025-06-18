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

- **Customer (Filter)**: Optional filter to show only projects for a specific customer
  - Select "All Customers" to see all projects
  - Select a specific customer to filter projects to only those belonging to that customer
- **Project**: Select from dropdown of available projects (filtered by customer if selected)
- **Activity**: Select from dropdown of available activities
  - When a project is selected: Shows activities specific to that project
  - When no project is selected: Shows global activities (those not tied to a specific project)
- **Description**: Optional description for the time tracking entry

**Important**: Only the Project and Activity are sent to the Kimai API. The Customer field is used only for filtering the project list to make selection easier.

Use the "Refresh Data" button to update all dropdown lists if new customers, projects, or activities are added to Kimai.

#### Stop Time Tracking Action

The Stop Time Tracking action uses the global settings automatically - no additional configuration needed.

## Usage

1. **Set up global settings**: Configure Kimai URL and API token in Plugin Settings
2. **Configure Start buttons**: Select project and activity from dropdowns (and optional description) for each Start Time Tracking button
3. **Add Stop button**: Place a Stop Time Tracking button on your deck
4. **Use the buttons**: Press Start to begin tracking time, Stop to end the current session

The buttons will show a green background on success and red background on error.

## Finding Customers, Projects and Activities

The plugin automatically fetches and displays available customers, projects, and activities from your Kimai instance in dropdown menus with intelligent filtering:

- **Customers**: Used only for filtering projects - not sent to the API
- **Projects**: Filtered by selected customer (or all projects if "All Customers" is selected)
- **Activities**: Shows project-specific activities when a project is selected, or global activities when no project is selected

If you need to refresh the lists:

1. Click the **"Refresh Data"** button in the action configuration
2. All dropdowns will be updated with the latest data from Kimai

**Manual lookup** (if needed):
- **Customers**: Go to Customers in Kimai, the ID is shown in the URL or customer list
- **Projects**: Go to Projects in Kimai, the ID is shown in the URL or project list
- **Activities**: Go to Activities in Kimai, the ID is shown in the URL or activity list  

**API endpoints** for advanced users:
- `/api/customers` - List all customers
- `/api/projects` - List all projects (can be filtered with `?customer=ID`)
- `/api/activities` - List all activities (can be filtered with `?project=ID` or `?globals=true`)

## Requirements

- Kimai installation with API access
- Valid API token from Kimai
- Network access to your Kimai instance

## Important Notes

### Datetime Format
The plugin uses the correct HTML5 "local date and time" format (`YYYY-MM-DDTHH:mm:ss`) when creating timesheets, as required by the Kimai API. This ensures that time tracking entries are created with the correct timestamps in your local timezone.

### API Compatibility
This plugin is designed to work with Kimai's REST API and follows the official API documentation for timesheet creation and management.

For more information checkout [the StreamController docs](https://streamcontroller.github.io/docs/latest/).
