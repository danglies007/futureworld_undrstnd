import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import { spawn } from 'child_process'
import util from 'util'

// Path to the plan review file
const PLAN_REVIEW_FILE = process.env.PLAN_REVIEW_FILE || 
  path.resolve(process.cwd(), '..', 'crewai', 'plan_for_review.json')

// Path to the CrewAI script for resuming the flow
const CREWAI_DIR = process.env.CREWAI_DIR || 
  path.join(process.cwd(), '..', 'crewai')

// GET handler to retrieve the current plan for review
export async function GET() {
  try {
    console.log("Plan API: Checking for plan file at:", PLAN_REVIEW_FILE);
    
    // Check if plan review file exists
    if (!fs.existsSync(PLAN_REVIEW_FILE)) {
      console.error("Plan API: Plan file not found at path:", PLAN_REVIEW_FILE);
      
      // Check the status to provide better context
      try {
        const statusFilePath = path.join(CREWAI_DIR, 'status.json');
        if (fs.existsSync(statusFilePath)) {
          const statusData = JSON.parse(fs.readFileSync(statusFilePath, 'utf-8'));
          console.log("Plan API: Current status is:", statusData.status, "- Message:", statusData.message);
        } else {
          console.log("Plan API: Status file not found, system may still be initializing");
        }
      } catch (statusError) {
        console.error("Plan API: Error checking status file:", statusError);
      }
      
      return NextResponse.json({
        success: false,
        message: 'No plan available for review'
      }, { status: 404 })
    }

    console.log("Plan API: Plan file found, reading contents");
    
    // Read the plan file
    const planData = fs.readFileSync(PLAN_REVIEW_FILE, 'utf-8')
    
    try {
      // Parse the JSON to validate it
      const parsedPlan = JSON.parse(planData);
      console.log("Plan API: Successfully parsed plan data with", 
        parsedPlan.sections ? parsedPlan.sections.length : 0, "sections");
      
      return NextResponse.json({
        success: true,
        data: parsedPlan
      })
    } catch (parseError) {
      console.error("Plan API: Error parsing plan JSON:", parseError);
      return NextResponse.json({
        success: false,
        message: 'Invalid plan format',
        error: parseError instanceof Error ? parseError.message : String(parseError)
      }, { status: 500 })
    }
  } catch (error) {
    console.error('Plan API: Error reading plan file:', error)
    return NextResponse.json({
      success: false,
      message: 'Error reading plan file',
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}

// POST handler to update the plan with user edits and resume the flow
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    if (!body || !body.plan) {
      return NextResponse.json({
        success: false,
        message: 'No plan data provided'
      }, { status: 400 })
    }

    console.log("Plan API: Received plan update request");
    
    // Write the edited plan to the plan review file
    fs.writeFileSync(PLAN_REVIEW_FILE, JSON.stringify(body.plan, null, 2))
    
    console.log("Plan API: Updated plan file with user edits");
    
    // Also write to the plan_approved.json file
    const PLAN_APPROVED_FILE = path.join(CREWAI_DIR, 'plan_approved.json')
    fs.writeFileSync(PLAN_APPROVED_FILE, JSON.stringify(body.plan, null, 2))
    
    console.log("Plan API: Created plan_approved.json file");
    
    // Update the status file to indicate plan is approved
    const statusFilePath = path.join(CREWAI_DIR, 'status.json')
    
    try {
      // Read current status
      const statusData = JSON.parse(fs.readFileSync(statusFilePath, 'utf-8'))
      
      // Update status to plan_approved
      statusData.status = 'plan_approved'
      statusData.message = 'Plan has been reviewed and approved'
      statusData.timestamp = new Date().toISOString()
      
      // Write updated status
      fs.writeFileSync(statusFilePath, JSON.stringify(statusData, null, 2))
      console.log("Plan API: Updated status to plan_approved");
    } catch (statusError) {
      console.error("Plan API: Error updating status file:", statusError);
      // Continue even if status update fails
    }
    
    // The flow will automatically resume on the next status check
    // due to the router method in the ForesightFlow class
    
    return NextResponse.json({
      success: true,
      message: 'Plan updated successfully and flow will resume automatically'
    })
  } catch (error) {
    console.error('Plan API: Error updating plan:', error)
    return NextResponse.json({
      success: false,
      message: 'Error updating plan',
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}
