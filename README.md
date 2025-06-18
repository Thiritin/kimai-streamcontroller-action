# Kimai Time Tracking Plugin

A StreamController plugin for integrating with Kimai time tracking system.

## Features

- **Smart Start/Stop Toggle**: Single button that starts and stops time tracking
  - Shows stop icon with elapsed time when active
  - Automatically stops other active time tracking when starting a new session
  - Only displays running state on the button matching the active project/activity
- **Active Tracking Display**: Dedicated display button showing current tracking status
  - Shows customer/project/activity information
  - Displays elapsed time with immediate updates when tracking starts/stops
  - Auto-refreshes every 30 seconds and updates instantly on tracking changes
  - Visual status indicators for different states
- **Multi-Instance Coordination**: Multiple buttons work together seamlessly
  - Starting any button automatically stops the currently active timesheet
  - Visual feedback shows which project/activity is currently being tracked
- **Global Settings**: Configure Kimai URL and API token once for all actions
- **Smart Activity Selection**: Automatically selects the first available activity
- **Hierarchical Filtering**: Customer filters projects, projects filter activities

## Configuration

### Global Plugin Settings

First, configure the global settings for your Kimai instance:

1. Go to **Settings** → **Plugins**
2. Find **Kimai Time Tracking** and click **Open Settings**
3. Configure:
   - **Kimai URL**: The base URL of your Kimai installation (e.g., `https://kimai.example.com`)
   - **API Token**: Your Kimai API token (can be generated in Kimai under User Settings)

### Action Configuration

#### Start/Stop Time Tracking Action

Each Start Time Tracking button now functions as a **smart toggle button**:

**Configuration:**
- **Customer (Filter)**: Optional filter to show only projects for a specific customer
  - Select "All Customers" to see all projects
  - Select a specific customer to filter projects to only those belonging to that customer
- **Project**: Select from dropdown of available projects (filtered by customer if selected)
- **Activity**: Select from dropdown of available activities
  - When a project is selected: Shows activities specific to that project
  - When no project is selected: Shows global activities (those not tied to a specific project)
  - **Auto-selection**: Automatically selects the first available activity if none is set
- **Description**: Optional description for the time tracking entry

**Behavior:**
- **First Press**: Starts time tracking for the configured project/activity
  - Automatically stops any other active time tracking
  - Shows stop icon to indicate tracking is active
  - Displays elapsed time (HH:MM format) in the top line
- **Second Press**: Stops the active time tracking
  - Returns to normal start icon
  - Clears the elapsed time display

**Multi-Button Coordination:**
- Only the button matching the **currently active project/activity** shows the running state
- Other buttons remain in "ready to start" state
- Starting any button automatically stops the previous active timesheet
- Perfect for switching between different projects/activities

**Important**: Only the Project and Activity are sent to the Kimai API. The Customer field is used only for filtering the project list to make selection easier.

Use the "Refresh Data" button to update all dropdown lists if new customers, projects, or activities are added to Kimai.

#### Stop Time Tracking Action (Legacy)

The dedicated Stop Time Tracking action is there to stop entries when i.e. not started via the stream deck.

#### Display Active Tracking Action

A dedicated display button that shows information about the currently active time tracking session:

**Configuration:**
- No configuration required - automatically displays active tracking information
- Uses the same global Kimai URL and API token settings

**Display Information:**
- **Top Line**: Customer & Project names (truncated to fit)
- **Center Line**: Activity name
- **Bottom Line**: Elapsed time in HH:MM format
- **When Inactive**: All text is cleared (no display)

**Behavior:**
- **Auto-Update**: Refreshes every 30 seconds automatically
- **Immediate Updates**: Updates instantly when time tracking starts or stops from any StartTracking button
- **Manual Refresh**: Press the button to refresh immediately
- **Visual States**:
  - **Active Tracking**: Shows customer/project/activity info with subtle green background
  - **No Active Tracking**: Shows "No Active Tracking" message
  - **Configuration Missing**: Shows "Config Missing" with yellow background
  - **Error**: Shows "Error" with red background

**Perfect for**: Having a dedicated "status display" button on your Stream Deck to see what you're currently tracking at a glance.

## Usage

1. **Set up global settings**: Configure Kimai URL and API token in Plugin Settings
2. **Configure buttons**: For each Start Time Tracking button:
   - Select customer (optional, for filtering)
   - Select project from dropdown  
   - Select activity from dropdown (auto-selected if only one available)
   - Add optional description
3. **Use the buttons**: 
   - **First press**: Starts time tracking (shows stop icon with elapsed time in top line)
   - **Second press**: Stops time tracking (returns to start icon)
   - **Switch projects**: Press any other configured button to automatically stop current tracking and start the new one

**Visual Feedback:**
- ⏸️ stop icon indicates active time tracking
- HH:MM elapsed time display in top line
- Only the button with matching project/activity shows running state
- Brief green/red backgrounds indicate success/error

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
