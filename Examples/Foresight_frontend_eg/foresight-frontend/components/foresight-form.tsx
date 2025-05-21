"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2 } from "lucide-react"
import { submitForesightConfig } from "@/lib/actions"
import { ForesightReport } from "./foresight-report"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"

// Define the form schema using Zod
const formSchema = z.object({
  sector: z.string().min(1, "Sector is required"),
  report_type: z.string().min(1, "Report type is required"),
  topic: z.string().optional(),
  year: z.coerce.number().int().min(2020).max(2100),
  audience_level: z.string().optional(),
  company: z.string().optional(),
  company_short: z.string().optional(),
  geography: z.string().min(1, "Geography is required"),
  specified_sources: z.string().min(1, "At least one source is required"),
})

type FormValues = z.infer<typeof formSchema>

export function ForesightForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasActiveReport, setHasActiveReport] = useState(false)
  const [showReportView, setShowReportView] = useState(false)
  
  // Initialize react-hook-form
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sector: "Mining",
      report_type: "Strategic Foresight Report",
      topic: "Future of Mining",
      year: new Date().getFullYear(),
      audience_level: "Strategic Decision Makers",
      company: "Exxaro Resources Limited",
      company_short: "Exxaro Resources Limited",
      geography: "Global",
      specified_sources: "Harvard Business Review, https://hbr.org, McKinsey Global Institute, Gartner, World Economic Forum, https://ftsg.com/",
    },
  })

  const handleSubmit = async (values: FormValues) => {
    setIsSubmitting(true)
    setError(null)

    try {
      // Format the specified_sources as an array
      const formattedData = {
        ...values,
        specified_sources: values.specified_sources.split(",").map((source) => source.trim()),
      }

      // Call the API to submit the configuration
      const result = await submitForesightConfig(formattedData)

      if (result.success) {
        setIsSubmitted(true)
        setHasActiveReport(true)
        setShowReportView(true)
      } else {
        setError(result.error || "Failed to submit configuration")
      }
    } catch (error) {
      console.error("Error submitting form:", error)
      setError("An unexpected error occurred")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReset = () => {
    setIsSubmitted(false)
    setError(null)
    setShowReportView(false)
    // Note: We don't reset hasActiveReport here
  }

  // If the form was submitted successfully, show the report component
  if (showReportView) {
    return <ForesightReport onBack={handleReset} />
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Configure Foresight Parameters</CardTitle>
            <CardDescription className="text-slate-400">
              Set the parameters for your strategic foresight report
            </CardDescription>
          </div>
          {hasActiveReport && (
            <Button 
              onClick={() => setShowReportView(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              View Report Progress
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {hasActiveReport && (
          <div className="mb-6 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0 pt-0.5">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-400 h-5 w-5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-300">Active Report Generation</h3>
                <div className="mt-1 text-sm text-slate-300">
                  <p>You have a report currently being generated. Would you like to return to the report view?</p>
                </div>
                <div className="mt-3">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setShowReportView(true)}
                    className="bg-blue-800/30 hover:bg-blue-800/50 border-blue-700"
                  >
                    Return to Report
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded-md text-red-300">
            {error}
          </div>
        )}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-slate-700">
                <TabsTrigger value="basic">Basic Info</TabsTrigger>
                <TabsTrigger value="company">Company Details</TabsTrigger>
                <TabsTrigger value="sources">Sources</TabsTrigger>
              </TabsList>
              
              <TabsContent value="basic">
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="sector"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sector</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              className="bg-slate-900 border-slate-700"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="report_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Report Type</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              className="bg-slate-900 border-slate-700"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <FormField
                    control={form.control}
                    name="topic"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Topic</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            className="bg-slate-900 border-slate-700"
                            placeholder="e.g., Future of Mining"
                          />
                        </FormControl>
                        <FormDescription className="text-xs text-slate-400">
                          Optional: Any areas or important themes that should be considered
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="year"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Current Year</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              className="bg-slate-900 border-slate-700"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="geography"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Geography</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              className="bg-slate-900 border-slate-700"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <FormField
                    control={form.control}
                    name="audience_level"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Audience Level</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            className="bg-slate-900 border-slate-700"
                            placeholder="e.g., Strategic Decision Makers"
                          />
                        </FormControl>
                        <FormDescription className="text-xs text-slate-400">
                          Optional: Target audience for the report
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="company">
                <div className="space-y-4 py-4">
                  <FormField
                    control={form.control}
                    name="company"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Name</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            className="bg-slate-900 border-slate-700"
                            placeholder="e.g., Exxaro Resources Limited"
                          />
                        </FormControl>
                        <FormDescription className="text-xs text-slate-400">
                          Optional: Company focus for the report
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="company_short"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Short Name</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            className="bg-slate-900 border-slate-700"
                            placeholder="e.g., Exxaro"
                          />
                        </FormControl>
                        <FormDescription className="text-xs text-slate-400">
                          Optional: Short name used for naming
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="sources">
                <div className="space-y-4 py-4">
                  <FormField
                    control={form.control}
                    name="specified_sources"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Specified Sources</FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            className="bg-slate-900 border-slate-700 min-h-[150px]"
                            placeholder="Enter sources separated by commas (names or URLs)"
                          />
                        </FormControl>
                        <FormDescription className="text-xs text-slate-400">
                          List of required sources to be consulted (can be names or URLs)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </TabsContent>
            </Tabs>
            
            <CardFooter className="flex justify-between border-t border-slate-700 pt-4 px-0">
              <Button 
                type="button"
                variant="outline" 
                className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white"
                onClick={() => form.reset()}
              >
                Reset
              </Button>
              
              <Button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  "Generate Foresight Report"
                )}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
