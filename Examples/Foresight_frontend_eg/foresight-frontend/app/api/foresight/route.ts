import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec, spawn } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

// Configure for Node.js runtime instead of Edge
export const runtime = 'nodejs';

interface ForesightConfig {
  sector: string;
  report_type: string;
  topic?: string;
  year: number;
  audience_level?: string;
  company?: string;
  company_short?: string;
  geography: string;
  specified_sources: string[];
}

export async function POST(request: NextRequest) {
  try {
    // Parse the request body
    const config: ForesightConfig = await request.json();
    
    // Format the config for Python
    const pythonConfig = `# Configuration variables for Foresight flow

FLOW_VARIABLES = {
    "sector": "${config.sector}",  # Can be changed to any sector focus
    "report_type": "${config.report_type}",
    "topic": "${config.topic || ''}", # OPTIONAL, Any areas or important themes that should be considered
    "year": ${config.year}, # What is the current year
    "audience_level": "${config.audience_level || ''}", # OPTIONAL, Can be changed to any audience level focus
    "company": "${config.company || ''}", # OPTIONAL, Can be changed to any company focus
    "company_short": "${config.company_short || ''}", # OPTIONAL, Short name used for naming
    "geography": "${config.geography}", # Can be changed to any geography focus
    "specified_sources": [  # List of required sources to be consulted (can be names or URLs)
        ${config.specified_sources.map(source => `"${source}"`).join(',\n        ')}
    ]
}`;

    // Get absolute paths using process.cwd()
    const rootDir = process.cwd();
    const projectRoot = path.resolve(rootDir, '..');
    const configPath = path.join(projectRoot, 'crewai/src/foresight/config.py');
    
    console.log('Writing config to:', configPath);
    
    // Ensure directory exists
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
      return NextResponse.json(
        { 
          success: false, 
          message: `Config directory not found: ${configDir}`
        },
        { status: 500 }
      );
    }
    
    // Write the config to the file
    fs.writeFileSync(configPath, pythonConfig);
    
    // Create outputs directory if it doesn't exist
    const crewaiDir = path.join(projectRoot, 'crewai');
    const outputsDir = path.join(crewaiDir, 'outputs');
    if (!fs.existsSync(outputsDir)) {
      fs.mkdirSync(outputsDir, { recursive: true });
      console.log('Created outputs directory:', outputsDir);
    }
    
    // Create a file to store process information
    const processInfoPath = path.join(crewaiDir, 'process_info.json');
    
    // Kill any existing process if it exists
    if (fs.existsSync(processInfoPath)) {
      try {
        const processInfo = JSON.parse(fs.readFileSync(processInfoPath, 'utf8'));
        if (processInfo.pid) {
          try {
            // On Unix/Mac, negative PID kills the process group
            process.kill(-processInfo.pid, 'SIGTERM');
            console.log(`Terminated previous process with PID: ${processInfo.pid}`);
          } catch (killError) {
            console.error(`Error terminating previous process: ${killError}`);
          }
        }
      } catch (readError) {
        console.error(`Error reading process info: ${readError}`);
      }
    }
    
    // Start the CrewAI process using spawn to see real-time output
    console.log('Starting CrewAI process...');
    
    // Create a shell script to run the process
    const shellScriptPath = path.join(crewaiDir, 'run_foresight.sh');
    const shellScriptContent = `#!/bin/bash
cd "${crewaiDir}"
source .venv/bin/activate
python -m src.foresight.main
`;
    
    fs.writeFileSync(shellScriptPath, shellScriptContent);
    fs.chmodSync(shellScriptPath, '755'); // Make executable
    
    // Use spawn with process group to make it easier to kill all child processes
    const crewProcess = spawn(shellScriptPath, [], {
      stdio: 'inherit',
      detached: true, // Create a new process group
    });
    
    // Save the process information
    const processInfo = {
      pid: crewProcess.pid,
      startTime: new Date().toLocaleString('en-US', { timeZone: 'Europe/Paris' }),
      config: config
    };
    
    fs.writeFileSync(processInfoPath, JSON.stringify(processInfo, null, 2));
    console.log(`CrewAI process started with PID: ${crewProcess.pid}`);
    
    // Unref the child process to allow the Node.js process to exit independently
    crewProcess.unref();
    
    // Return immediate success response
    return NextResponse.json({ 
      success: true, 
      message: 'Foresight process started successfully',
      pid: crewProcess.pid
    });
    
  } catch (error) {
    console.error('Error processing foresight request:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: 'Failed to process foresight request',
        error: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Get absolute paths using process.cwd()
    const rootDir = process.cwd();
    const projectRoot = path.resolve(rootDir, '..');
    const outputDir = path.join(projectRoot, 'crewai/outputs');
    
    console.log('Looking for reports in:', outputDir);
    
    // Check if output directory exists
    if (!fs.existsSync(outputDir)) {
      // Create the directory if it doesn't exist
      fs.mkdirSync(outputDir, { recursive: true });
      console.log('Created output directory:', outputDir);
      
      return NextResponse.json({ 
        success: false, 
        message: 'No foresight reports found yet, please wait while the report is being generated'
      });
    }
    
    // List files in the output directory
    const files = fs.readdirSync(outputDir);
    
    // Find Markdown files
    const mdFiles = files.filter(file => file.endsWith('.md') && (file.startsWith('Foresight_') || file.includes('research') || file.includes('analysis')));
    
    if (mdFiles.length === 0) {
      return NextResponse.json({ 
        success: false, 
        message: 'No foresight reports found yet, please wait while the report is being generated' 
      });
    }
    
    // Get the latest file based on modification time
    const latestFile = mdFiles.reduce((latest, file) => {
      const filePath = path.join(outputDir, file);
      const stats = fs.statSync(filePath);
      
      if (!latest || stats.mtime > fs.statSync(path.join(outputDir, latest)).mtime) {
        return file;
      }
      
      return latest;
    }, '');
    
    // Read the file content
    const content = fs.readFileSync(path.join(outputDir, latestFile), 'utf8');
    
    return NextResponse.json({ 
      success: true, 
      filename: latestFile,
      content
    });
    
  } catch (error) {
    console.error('Error retrieving foresight report:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: 'Failed to retrieve foresight report',
        error: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

// Add a new DELETE endpoint to cancel the running process
export async function DELETE() {
  try {
    const rootDir = process.cwd();
    const projectRoot = path.resolve(rootDir, '..');
    const processInfoPath = path.join(projectRoot, 'crewai/process_info.json');
    
    if (fs.existsSync(processInfoPath)) {
      try {
        const processInfo = JSON.parse(fs.readFileSync(processInfoPath, 'utf8'));
        
        if (processInfo.pid) {
          console.log(`Attempting to terminate CrewAI process group with PID: ${processInfo.pid}`);
          
          try {
            // On Unix/Mac, negative PID kills the process group
            process.kill(-processInfo.pid, 'SIGTERM');
            
            // Also try to kill directly in case it's not in a process group
            process.kill(processInfo.pid, 'SIGTERM');
            
            console.log(`Sent SIGTERM to process group with PID: ${processInfo.pid}`);
            
            // Also try to find and kill any Python processes related to foresight
            const { stdout } = await execPromise('ps aux | grep "python -m src.foresight.main" | grep -v grep | awk \'{print $2}\'');
            
            if (stdout.trim()) {
              const pids = stdout.trim().split('\n');
              for (const pid of pids) {
                if (pid) {
                  try {
                    process.kill(parseInt(pid), 'SIGKILL');
                    console.log(`Killed Python process with PID: ${pid}`);
                  } catch (killError) {
                    console.error(`Error killing Python process ${pid}: ${killError}`);
                  }
                }
              }
            }
            
            // As a last resort, try to kill all Python processes related to foresight
            await execPromise('pkill -f "python -m src.foresight.main"').catch(() => {});
            
          } catch (killError) {
            console.error(`Error terminating process group: ${killError}`);
            
            // Try a more aggressive approach with SIGKILL
            try {
              process.kill(-processInfo.pid, 'SIGKILL');
              console.log(`Sent SIGKILL to process group with PID: ${processInfo.pid}`);
            } catch (killError2) {
              console.error(`Error sending SIGKILL: ${killError2}`);
            }
          }
        }
        
        // Remove the process info file
        fs.unlinkSync(processInfoPath);
        
      } catch (parseError) {
        console.error(`Error parsing process info: ${parseError}`);
      }
      
      return NextResponse.json({ 
        success: true, 
        message: 'CrewAI process termination commands sent successfully'
      });
    } else {
      return NextResponse.json({ 
        success: false, 
        message: 'No running CrewAI process information found'
      });
    }
  } catch (error) {
    console.error('Error canceling CrewAI process:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: 'Failed to cancel CrewAI process',
        error: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}
