import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';
import { promisify } from 'util';
import fs from 'fs';

const execAsync = promisify(exec);

export async function POST() {
  try {
    // Path to the CrewAI main script
    const crewaiPath = process.env.CREWAI_PATH || path.resolve(process.cwd(), '../crewai');
    const scriptPath = path.join(crewaiPath, 'src/foresight/main.py');
    const logPath = path.join(crewaiPath, 'crewai_process.log');
    
    console.log(`Continuing flow execution with script at: ${scriptPath}`);
    console.log(`Process logs will be available at: ${logPath}`);
    
    // Execute the script in the background and redirect output to a log file
    const command = `cd ${crewaiPath} && python -m src.foresight.main > ${logPath} 2>&1`;
    
    // Start the process but don't wait for it to complete
    execAsync(command).catch(err => {
      console.error('Error in background process execution:', err);
    });
    
    return NextResponse.json({
      success: true,
      message: 'Flow continuation initiated',
      logPath: logPath
    });
  } catch (error) {
    console.error('Error continuing flow:', error);
    return NextResponse.json({
      success: false,
      message: 'Failed to continue flow',
      error: (error as Error).message
    }, { status: 500 });
  }
}
