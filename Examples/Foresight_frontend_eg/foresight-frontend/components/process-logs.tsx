'use client';

import { useState, useEffect } from 'react';
import { formatLogs } from '@/lib/log-formatter';
import { Button } from '@/components/ui/button';
import { ReloadIcon } from '@radix-ui/react-icons';

export function ProcessLogs() {
  const [logs, setLogs] = useState<string>('');
  const [formattedLines, setFormattedLines] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showFormatted, setShowFormatted] = useState<boolean>(true);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  const fetchLogs = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/foresight/logs');
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch logs');
      }
      
      const data = await response.json();
      
      if (data.logs) {
        setLogs(data.logs);
        // Process logs to ensure proper formatting
        const formatted = formatLogs(data.logs);
        setFormattedLines(formatted);
        setError(null);
      } else {
        setLogs('');
        setFormattedLines('');
        setError('No logs available');
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    
    // Cleanup function
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000); // Refresh every 5 seconds
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [autoRefresh]);

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
        <h2 className="text-2xl font-bold">Process Logs</h2>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={toggleAutoRefresh}
            className={autoRefresh ? "bg-blue-600/20 text-blue-500 border-blue-500" : ""}
          >
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh} 
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Refresh Logs"
            )}
          </Button>
        </div>
      </div>

      <div className="format-toggle flex space-x-2 mb-4">
        <Button
          variant={showFormatted ? "default" : "outline"}
          size="sm"
          onClick={() => setShowFormatted(true)}
        >
          Enhanced View
        </Button>
        <Button
          variant={!showFormatted ? "default" : "outline"}
          size="sm"
          onClick={() => setShowFormatted(false)}
        >
          Raw Logs
        </Button>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 p-4 rounded-md">
          {error}
        </div>
      )}

      {isLoading && !logs ? (
        <div className="flex items-center justify-center p-8 border rounded-md bg-slate-700/30">
          <ReloadIcon className="mr-2 h-6 w-6 animate-spin" />
          <span>Loading logs...</span>
        </div>
      ) : logs ? (
        <div className="border border-slate-700 rounded-md overflow-hidden">
          <div className="bg-slate-800 overflow-auto max-h-[70vh]">
            {showFormatted ? (
              <div className="log-content p-4 space-y-2" dangerouslySetInnerHTML={{ __html: formattedLines }} />
            ) : (
              <pre className="font-mono text-sm p-4 whitespace-pre-wrap">{logs}</pre>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center p-8 border rounded-md bg-slate-700/30">
          No logs available
        </div>
      )}
    </div>
  );
}

// Default export for backwards compatibility
export default ProcessLogs;
