"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, FileText, Download, XCircle, AlertCircle, CheckCircle2, ClipboardList, UserCircle, Clock, Wrench, Search } from "lucide-react"
import { getForesightReport, getForesightStatus, cancelForesightProcess } from "@/lib/actions"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { Progress } from "@/components/ui/progress"
import PlanReview from "@/components/plan-review"
import { ProcessLogs } from "@/components/process-logs"

interface ForesightReportProps {
  onBack: () => void
}

interface ForesightStatus {
  status: string;
  message: string;
  timestamp: string;
  agent?: string;
  task?: string;
  tools?: string[] | string;
  query?: string;
  subtasks?: string[];
  progress?: number;
  flow_state?: string;
}

const statusColors: Record<string, string> = {
  initializing: "text-blue-400",
  planning: "text-indigo-400",
  researching: "text-purple-400",
  analyzing: "text-violet-400",
  insights: "text-fuchsia-400",
  writing: "text-pink-400",
  editing: "text-rose-400",
  reviewing: "text-orange-400",
  compiling: "text-amber-400",
  complete: "text-green-400",
  error: "text-red-400",
  awaiting_review: "text-yellow-400",
  plan_approved: "text-green-400"
}

const statusProgress: Record<string, number> = {
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
}

const statusIcons: Record<string, React.ReactNode> = {
  initializing: <Loader2 className="h-5 w-5 animate-spin" />,
  planning: <ClipboardList className="h-5 w-5" />,
  awaiting_review: <AlertCircle className="h-5 w-5" />,
  plan_approved: <CheckCircle2 className="h-5 w-5" />,
  researching: <Search className="h-5 w-5" />,
  analyzing: <AlertCircle className="h-5 w-5" />,
  writing: <FileText className="h-5 w-5" />,
  editing: <ClipboardList className="h-5 w-5" />,
  complete: <CheckCircle2 className="h-5 w-5" />,
  error: <XCircle className="h-5 w-5" />,
  cancelled: <XCircle className="h-5 w-5" />
}

export function ForesightReport({ onBack }: ForesightReportProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<{ filename: string; content: string } | null>(null)
  const [cancelling, setCancelling] = useState(false)
  const [status, setStatus] = useState<ForesightStatus | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const [taskHistory, setTaskHistory] = useState<string[]>([])
  const [shouldPoll, setShouldPoll] = useState(true)
  const [showLogs, setShowLogs] = useState(false)
  const [viewMode, setViewMode] = useState<'progress-only' | 'split-view' | 'report-only'>('progress-only')

  // Format a timestamp to a readable format
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  // Format a name by capitalizing each word and removing underscores
  const formatName = (name: string) => {
    return name
      .split(/[_\s]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  // Capitalize the first letter of a string
  const capitalizeFirstLetter = (string: string) => {
    return string.charAt(0).toUpperCase() + string.slice(1)
  }

  // Function to fetch status updates
  const fetchStatus = async () => {
    try {
      const result = await getForesightStatus()
      if (result.success && result.data.success) {
        const newStatus = result.data.data;
        setStatus(newStatus)
        
        // Add to task history if agent or task changed
        if (newStatus.agent && newStatus.task) {
          const statusEntry = `${formatName(newStatus.agent)} - ${formatName(newStatus.task)}`;
          setTaskHistory(prev => {
            // Only add if it's not already the last entry
            if (prev.length === 0 || prev[prev.length - 1] !== statusEntry) {
              // Keep only the last 5 entries
              const updatedHistory = [...prev, statusEntry];
              return updatedHistory.slice(-5);
            }
            return prev;
          });
        }
        
        // Log status updates for debugging
        console.log("Status update:", newStatus.status, "Progress:", newStatus.progress, "Flow state:", newStatus.flow_state);
        
        // Check if process is complete to stop polling status
        if (newStatus.status === 'complete' || newStatus.flow_state === 'complete') {
          setIsComplete(true)
          setShouldPoll(false)
          
          // Trigger an immediate report fetch when status becomes complete
          fetchReport()
        }
      }
    } catch (err) {
      console.error("Error fetching status:", err)
    }
  }

  // Function to fetch the report
  const fetchReport = async () => {
    try {
      const result = await getForesightReport()
      if (result.success && result.data.success) {
        setReport({
          filename: result.data.filename,
          content: result.data.content
        })
        setError(null)
        setLoading(false)
        
        // Only stop polling if we have a final report AND status is complete
        if (status?.status === 'complete' || status?.flow_state === 'complete') {
          setShouldPoll(false)
        }
      } else {
        // Only set error if we don't have a report yet
        if (!report) {
          setError(result.error || result.data?.message || 'Failed to load report')
        }
        // Keep loading state if we're still waiting for a report
        setLoading(!report)
      }
    } catch (err) {
      if (!report) {
        setError('An error occurred while fetching the report')
      }
      console.error(err)
      setLoading(!report)
    }
  }

  const handleCancelProcess = async () => {
    setCancelling(true)
    try {
      const result = await cancelForesightProcess()
      if (result.success && result.data.success) {
        setError('Process cancelled. You can go back and try again.')
      } else {
        setError(`Failed to cancel process: ${result.data?.message || 'Unknown error'}`)
      }
    } catch (err) {
      setError('An error occurred while trying to cancel the process')
      console.error(err)
    } finally {
      setCancelling(false)
      // Stop polling after cancellation
      setShouldPoll(false)
    }
  }

  const handlePlanReviewComplete = () => {
    // Refresh status after plan review is complete
    fetchStatus()
  }

  useEffect(() => {
    // Initial fetch
    fetchReport()
    fetchStatus()
    
    // Set up polling intervals only if we should poll
    let reportInterval: NodeJS.Timeout | null = null;
    let statusInterval: NodeJS.Timeout | null = null;
    
    // Log current status for debugging
    console.log("Current status:", status?.status, "Progress:", status?.progress, "Flow state:", status?.flow_state);
    
    // Only stop polling if complete or if we have a confirmed plan ready for review
    if (status?.status === 'complete' || status?.flow_state === 'complete') {
      setShouldPoll(false);
      console.log("Stopping polling due to completed status");
    }
    
    if (shouldPoll) {
      reportInterval = setInterval(() => {
        if (shouldPoll) {
          fetchReport()
        }
      }, 10000) // Every 10 seconds
      
      statusInterval = setInterval(() => {
        // Continue polling unless complete
        if (!isComplete && shouldPoll) {
          fetchStatus()
        }
      }, 3000)  // Every 3 seconds
    }
    
    return () => {
      if (reportInterval) clearInterval(reportInterval)
      if (statusInterval) clearInterval(statusInterval)
    }
  }, [isComplete, shouldPoll, status?.status, status?.flow_state])

  const handleDownload = () => {
    if (!report) return
    
    const blob = new Blob([report.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = report.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // If status is awaiting_review, show the plan review component
  if (status?.status === 'awaiting_review') {
    console.log("Rendering plan review component for status:", status?.status);
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle>Foresight Plan Review</CardTitle>
          <CardDescription className="text-slate-400">
            Review and edit the plan before proceeding with research
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PlanReview onComplete={handlePlanReviewComplete} />
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={onBack}>
            Back
          </Button>
          <Button 
            variant="destructive" 
            onClick={handleCancelProcess}
            disabled={cancelling}
          >
            {cancelling ? 'Cancelling...' : 'Cancel Process'}
          </Button>
        </CardFooter>
      </Card>
    )
  }

  // Debug output for status
  console.log("Not showing plan review. Current status:", status?.status);

  return (
    <div className="w-full">
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Foresight Report</CardTitle>
              <CardDescription>
                {report ? report.filename : "Generating your report..."}
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={onBack}>
                Back
              </Button>
              {report && (
                <Button variant="outline" size="sm" onClick={() => setViewMode(viewMode === 'report-only' ? 'split-view' : 'report-only')}>
                  {viewMode === 'report-only' ? 'Show Progress' : 'Full Report'}
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className={`flex ${viewMode === 'split-view' ? 'flex-col md:flex-row gap-4' : 'flex-col'}`}>
            {/* Progress and Logs Section */}
            {(viewMode === 'progress-only' || viewMode === 'split-view') && (
              <div className={`${viewMode === 'split-view' ? 'w-full md:w-1/2' : 'w-full'}`}>
                {!isComplete && status ? (
                  <div>
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium">Progress</h3>
                        <span className="text-sm text-slate-400">{capitalizeFirstLetter(status.status)}</span>
                      </div>
                      <Progress value={status.progress || 0} className="h-2" />
                    </div>

                    <div className="bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="p-3 border-b border-slate-700">
                        <h3 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                          <Clock className="h-4 w-4" />
                          Current Activity
                        </h3>
                      </div>
                      <div className="p-3">
                        <p className="text-sm mb-3">{status.message}</p>

                        {status.agent && (
                          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                            <UserCircle className="h-3.5 w-3.5" />
                            <span className="font-medium">Agent:</span> {formatName(status.agent)}
                          </div>
                        )}

                        {status.task && (
                          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                            <Wrench className="h-3.5 w-3.5" />
                            <span className="font-medium">Task:</span> {formatName(status.task)}
                          </div>
                        )}

                        {status.tools && (
                          <div className="flex items-start gap-2 text-xs text-slate-400 mb-1">
                            <div className="mt-0.5">
                              <Search className="h-3.5 w-3.5" />
                            </div>
                            <div>
                              <span className="font-medium">Tools:</span>{" "}
                              {Array.isArray(status.tools)
                                ? status.tools.join(", ")
                                : status.tools}
                            </div>
                          </div>
                        )}

                        <div className="text-xs text-slate-500 mt-3">
                          Updated: {formatTimestamp(status.timestamp)}
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-800/50 rounded-lg border border-slate-700 mt-4">
                      <div className="p-3 border-b border-slate-700">
                        <h3 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                          <ClipboardList className="h-4 w-4" />
                          Task History
                        </h3>
                      </div>
                      <div className="p-3">
                        <ul className="space-y-2">
                          {taskHistory.map((task, index) => (
                            <li key={index} className="text-xs text-slate-400 flex items-center gap-2">
                              <div className="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
                              {task}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    {/* Process logs */}
                    {showLogs && (
                      <div className="bg-slate-800/50 rounded-lg border border-slate-700 mt-4">
                        <div className="p-3 border-b border-slate-700">
                          <h3 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            Process Logs
                          </h3>
                        </div>
                        <div className="p-3">
                          <ProcessLogs />
                        </div>
                      </div>
                    )}
                    
                    <div className="mt-4 flex flex-col">
                      <Button 
                        variant="destructive" 
                        disabled={cancelling} 
                        onClick={handleCancelProcess}
                      >
                        {cancelling ? 'Cancelling...' : 'Cancel Process'}
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        onClick={() => setShowLogs(!showLogs)}
                        className="mt-2"
                      >
                        {showLogs ? 'Hide Logs' : 'Show Logs'}
                      </Button>
                    </div>
                  </div>
                ) : error ? (
                  <div className="flex flex-col items-center justify-center py-6">
                    <XCircle className="h-12 w-12 text-red-500 mb-4" />
                    <h3 className="text-xl font-medium mb-2">Error</h3>
                    <p className="text-slate-400 text-center mb-4">{error}</p>
                    <Button onClick={onBack}>Go Back</Button>
                  </div>
                ) : loading ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
                    <h3 className="text-xl font-medium mb-2">Generating your report</h3>
                    <p className="text-slate-400">This may take several minutes to complete</p>
                  </div>
                ) : null}
              </div>
            )}

            {/* Report Content Section */}
            {report && (viewMode === 'split-view' || viewMode === 'report-only') && (
              <div className={`${viewMode === 'split-view' ? 'w-full md:w-1/2' : 'w-full'} bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 overflow-auto max-h-[800px]`}>
                <div className="prose dark:prose-invert max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeRaw]}
                  >
                    {report.content}
                  </ReactMarkdown>
                </div>
                <div className="mt-4 flex justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      const blob = new Blob([report.content], { type: 'text/markdown' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = report.filename;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
