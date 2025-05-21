import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

// Define the status interface
interface ForesightStatus {
  status: string
  message: string
  timestamp: string
  agent?: string
  task?: string
  tools?: string[] | string
  query?: string
  subtasks?: string[]
  progress?: number
  flow_state?: string
}

// Path to the status file
const STATUS_FILE_PATH = process.env.STATUS_FILE_PATH || path.join(process.cwd(), '..', 'crewai', 'status.json')

// Path to the outputs directory
const OUTPUTS_DIR = process.env.OUTPUTS_DIR || path.join(process.cwd(), '..', 'crewai', 'outputs')

export async function GET(request: Request) {
  try {
    console.log("Status API: Looking for status file at:", STATUS_FILE_PATH);
    
    // Check if status file exists
    if (!fs.existsSync(STATUS_FILE_PATH)) {
      console.log("Status API: Status file not found, creating default status");
      
      // Create a default status file if it doesn't exist
      const defaultStatus: ForesightStatus = {
        status: "initializing",
        message: "Initializing Foresight process",
        timestamp: new Date().toISOString(),
        agent: "SystemAgent",
        task: "InitializationTask"
      };
      
      // Write the default status to the file
      fs.writeFileSync(STATUS_FILE_PATH, JSON.stringify(defaultStatus, null, 2));
      
      return NextResponse.json({ success: true, data: defaultStatus });
    }
    
    // Read the status file
    const statusData = fs.readFileSync(STATUS_FILE_PATH, 'utf-8')
    const status: ForesightStatus = JSON.parse(statusData)
    
    console.log("Status API: Current status from file:", status.status)
    
    // If status is not already complete and not awaiting_review, check if we should mark it as complete
    if (status.status !== 'complete' && status.status !== 'awaiting_review' && status.status !== 'plan_approved') {
      // Check if there are any final report files in the outputs directory
      const finalReportFound = checkForFinalReport()
      
      if (finalReportFound) {
        console.log("Status API: Final report found, but status is:", status.status)
      }
      
      // Check if flow_state indicates completion
      if (status.flow_state === 'complete') {
        console.log("Status API: Flow state indicates completion")
        status.status = 'complete'
        status.message = 'Foresight report generation complete'
        status.progress = 100
      }
      // If we found a final report and the last status update was more than 30 seconds ago,
      // we can assume the process is complete but the status wasn't updated
      else if (finalReportFound) {
        console.log("Status API: Updating status to complete due to final report")
        status.status = 'complete'
        status.message = 'Foresight report generation complete'
        status.flow_state = 'complete'
        status.progress = 100
      }
    }
    
    // Enhance status with additional information if available
    enhanceStatusWithAdditionalInfo(status)

    return NextResponse.json({ success: true, data: status })
  } catch (error) {
    console.error('Error fetching status:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch status' },
      { status: 500 }
    )
  }
}

// Helper function to check if there are any final report files in the outputs directory
function checkForFinalReport() {
  try {
    if (!fs.existsSync(OUTPUTS_DIR)) {
      return false
    }
    
    const files = fs.readdirSync(OUTPUTS_DIR)
    const reportFiles = files.filter(file => 
      file.startsWith('Foresight_') && file.endsWith('.md')
    )
    
    console.log("Found final report files:", reportFiles)
    
    return reportFiles.length > 0
  } catch (error) {
    console.error('Error checking for final report:', error)
    return false
  }
}

// Helper function to enhance status with additional information
function enhanceStatusWithAdditionalInfo(status: ForesightStatus) {
  // Add query information if available
  try {
    const queryFilePath = path.join(process.cwd(), '..', 'crewai', 'query.json')
    if (fs.existsSync(queryFilePath)) {
      const queryData = JSON.parse(fs.readFileSync(queryFilePath, 'utf-8'))
      status.query = queryData.query
    }
  } catch (error) {
    console.error('Error reading query file:', error)
  }

  // Add tools information if available
  try {
    const toolsFilePath = path.join(process.cwd(), '..', 'crewai', 'tools.json')
    if (fs.existsSync(toolsFilePath)) {
      const toolsData = JSON.parse(fs.readFileSync(toolsFilePath, 'utf-8'))
      status.tools = toolsData.tools
    }
  } catch (error) {
    console.error('Error reading tools file:', error)
  }

  // Add default tools if not already set
  if (!status.tools) {
    if (status.status === 'researching') {
      status.tools = ['Search', 'Web Browsing', 'Content Analysis']
    } else if (status.status === 'writing') {
      status.tools = ['Content Generation', 'Fact Checking']
    } else if (status.status === 'editing') {
      status.tools = ['Grammar Check', 'Style Analysis']
    } else if (status.status === 'analyzing') {
      status.tools = ['Data Analysis', 'Trend Detection']
    }
  }
  
  // Set default progress values if not provided
  if (status.progress === undefined) {
    // Map status to progress percentage
    const progressMap: Record<string, number> = {
      initializing: 5,
      planning: 15,
      awaiting_review: 20,
      plan_approved: 25,
      researching: 40,
      analyzing: 60,
      insights: 70,
      writing: 80,
      editing: 85,
      reviewing: 90,
      compiling: 95,
      complete: 100,
      error: 0
    };
    
    status.progress = progressMap[status.status] || 0;
  }
  
  // Log enhanced status for debugging
  console.log("Status API: Enhanced status:", {
    status: status.status,
    progress: status.progress,
    flow_state: status.flow_state
  });
}
