import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the CrewAI log file
    const crewaiPath = process.env.CREWAI_PATH || path.resolve(process.cwd(), '../crewai');
    const logPath = path.join(crewaiPath, 'crewai_process.log');
    
    console.log(`Logs API: Checking for log file at: ${logPath}`);
    
    // Check if log file exists
    if (!fs.existsSync(logPath)) {
      console.log("Logs API: Log file not found");
      return NextResponse.json({
        success: false,
        message: 'No logs available'
      }, { status: 404 });
    }
    
    // Read the log file
    const logs = fs.readFileSync(logPath, 'utf-8');
    
    // Return the logs
    return NextResponse.json({
      success: true,
      logs
    });
  } catch (error) {
    console.error('Error reading logs:', error);
    return NextResponse.json({
      success: false,
      message: 'Failed to read logs',
      error: (error as Error).message
    }, { status: 500 });
  }
}
