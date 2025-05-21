'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, CheckCircle2, Edit3, Plus, Trash2 } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/components/ui/use-toast'

interface Section {
  section_number: number
  subtitle: string
  high_level_goal: string
  why_important: string
  sources: string[]
  content_outline: string[]
}

interface Plan {
  sections: Section[]
}

interface PlanReviewProps {
  onComplete?: () => void
}

export default function PlanReview({ onComplete }: PlanReviewProps) {
  const [plan, setPlan] = useState<Plan | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const { toast } = useToast()

  useEffect(() => {
    fetchPlan()
  }, [])

  const fetchPlan = async () => {
    try {
      setLoading(true)
      console.log("PlanReview: Fetching plan...")
      const response = await fetch('/api/foresight/plan')
      
      console.log("PlanReview: Fetch response status:", response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        console.error("PlanReview: Error response:", errorData)
        throw new Error(errorData.message || 'Failed to fetch plan')
      }

      const data = await response.json()
      console.log("PlanReview: Plan data received:", data)
      setPlan(data.data)
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred'
      console.error('PlanReview: Error fetching plan:', errorMessage, err)
      setError(errorMessage)
      toast({
        title: "Error fetching plan",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!plan) return

    try {
      setSubmitting(true)
      const response = await fetch('/api/foresight/plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan }),
      })

      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to submit plan')
      }

      // Call the continue API to restart the flow after plan approval
      try {
        const continueResponse = await fetch('/api/foresight/continue', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        const continueData = await continueResponse.json();
        console.log("Flow continuation response:", continueData);
      } catch (continueErr) {
        console.error("Error restarting flow:", continueErr);
        // Don't throw here, we still want to show success for plan approval
      }

      toast({
        title: 'Plan approved',
        description: 'Your plan has been approved and the research process has begun.',
        variant: 'default',
      })

      if (onComplete) {
        onComplete()
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'An unknown error occurred',
        variant: 'destructive',
      })
      console.error('Error submitting plan:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const updateSection = (index: number, field: keyof Section, value: any) => {
    if (!plan) return

    const updatedPlan = { ...plan }
    const updatedSections = [...updatedPlan.sections]
    
    updatedSections[index] = {
      ...updatedSections[index],
      [field]: value,
    }

    updatedPlan.sections = updatedSections
    setPlan(updatedPlan)
  }

  const addSection = () => {
    if (!plan) return

    const newSectionNumber = plan.sections.length > 0 
      ? Math.max(...plan.sections.map(s => s.section_number)) + 1 
      : 1

    const newSection: Section = {
      section_number: newSectionNumber,
      subtitle: `New Section ${newSectionNumber}`,
      high_level_goal: '',
      why_important: '',
      sources: [],
      content_outline: [],
    }

    setPlan({
      ...plan,
      sections: [...plan.sections, newSection],
    })
  }

  const removeSection = (index: number) => {
    if (!plan) return

    const updatedSections = [...plan.sections]
    updatedSections.splice(index, 1)

    // Renumber sections
    const renumberedSections = updatedSections.map((section, idx) => ({
      ...section,
      section_number: idx + 1,
    }))

    setPlan({
      ...plan,
      sections: renumberedSections,
    })
  }

  const addListItem = (sectionIndex: number, field: 'sources' | 'content_outline', value: string) => {
    if (!plan || !value.trim()) return

    const updatedPlan = { ...plan }
    const updatedSections = [...updatedPlan.sections]
    const section = { ...updatedSections[sectionIndex] }
    
    section[field] = [...section[field], value.trim()]
    updatedSections[sectionIndex] = section
    updatedPlan.sections = updatedSections
    
    setPlan(updatedPlan)
  }

  const removeListItem = (sectionIndex: number, field: 'sources' | 'content_outline', itemIndex: number) => {
    if (!plan) return

    const updatedPlan = { ...plan }
    const updatedSections = [...updatedPlan.sections]
    const section = { ...updatedSections[sectionIndex] }
    
    section[field] = section[field].filter((_, idx) => idx !== itemIndex)
    updatedSections[sectionIndex] = section
    updatedPlan.sections = updatedSections
    
    setPlan(updatedPlan)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading plan...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!plan) {
    return (
      <Alert className="mb-6">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Plan Available</AlertTitle>
        <AlertDescription>There is no plan available for review at this time.</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Review & Edit Research Plan</h1>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={fetchPlan}
            disabled={submitting}
          >
            Refresh
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Approving...' : 'Approve Plan & Start Research'}
          </Button>
        </div>
      </div>

      <Alert className="mb-6">
        <CheckCircle2 className="h-4 w-4" />
        <AlertTitle>Plan Ready for Review</AlertTitle>
        <AlertDescription>
          Review and edit the research plan below before approving. You can modify section details, 
          add or remove sections, and adjust the content outline for each section.
        </AlertDescription>
      </Alert>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          {plan.sections.map((section, index) => (
            <TabsTrigger key={index} value={`section-${index}`}>
              Section {section.section_number}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Plan Overview</CardTitle>
              <CardDescription>
                This plan contains {plan.sections.length} sections. Review the sections below or use the tabs to edit each section in detail.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {plan.sections.map((section, index) => (
                  <Card key={index} className="overflow-hidden">
                    <CardHeader className="bg-muted/50 py-3">
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-lg">
                          {section.section_number}. {section.subtitle}
                        </CardTitle>
                        <div className="flex gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => setActiveTab(`section-${index}`)}
                          >
                            <Edit3 className="h-4 w-4 mr-1" /> Edit
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => removeSection(index)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="py-3">
                      <p className="text-sm font-medium mb-1">Goal:</p>
                      <p className="text-sm text-muted-foreground mb-2">{section.high_level_goal}</p>
                      
                      <p className="text-sm font-medium mb-1">Why Important:</p>
                      <p className="text-sm text-muted-foreground mb-2">{section.why_important}</p>
                      
                      <p className="text-sm font-medium mb-1">Content Outline:</p>
                      <ul className="text-sm text-muted-foreground list-disc pl-5">
                        {section.content_outline.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={addSection} className="w-full">
                <Plus className="h-4 w-4 mr-2" /> Add New Section
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {plan.sections.map((section, index) => (
          <TabsContent key={index} value={`section-${index}`} className="mt-4">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Section {section.section_number}</CardTitle>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => removeSection(index)}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-1" /> Remove Section
                  </Button>
                </div>
                <CardDescription>
                  Edit the details for this section of the research plan.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Section Title</label>
                    <Input 
                      value={section.subtitle} 
                      onChange={(e) => updateSection(index, 'subtitle', e.target.value)}
                      placeholder="Enter section title"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium mb-1 block">High-Level Goal</label>
                    <Textarea 
                      value={section.high_level_goal} 
                      onChange={(e) => updateSection(index, 'high_level_goal', e.target.value)}
                      placeholder="What is the main goal of this section?"
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium mb-1 block">Why Important</label>
                    <Textarea 
                      value={section.why_important} 
                      onChange={(e) => updateSection(index, 'why_important', e.target.value)}
                      placeholder="Why is this section important for the report?"
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium mb-1 block">Sources</label>
                    <div className="space-y-2">
                      {section.sources.map((source, sourceIndex) => (
                        <div key={sourceIndex} className="flex gap-2">
                          <Input 
                            value={source} 
                            onChange={(e) => {
                              const updatedSources = [...section.sources]
                              updatedSources[sourceIndex] = e.target.value
                              updateSection(index, 'sources', updatedSources)
                            }}
                          />
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => removeListItem(index, 'sources', sourceIndex)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      
                      <div className="flex gap-2">
                        <Input 
                          placeholder="Add a new source"
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              addListItem(index, 'sources', e.currentTarget.value)
                              e.currentTarget.value = ''
                            }
                          }}
                        />
                        <Button 
                          variant="outline" 
                          onClick={(e) => {
                            const input = e.currentTarget.previousElementSibling as HTMLInputElement
                            addListItem(index, 'sources', input.value)
                            input.value = ''
                          }}
                        >
                          Add
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium mb-1 block">Content Outline</label>
                    <div className="space-y-2">
                      {section.content_outline.map((item, itemIndex) => (
                        <div key={itemIndex} className="flex gap-2">
                          <Input 
                            value={item} 
                            onChange={(e) => {
                              const updatedOutline = [...section.content_outline]
                              updatedOutline[itemIndex] = e.target.value
                              updateSection(index, 'content_outline', updatedOutline)
                            }}
                          />
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => removeListItem(index, 'content_outline', itemIndex)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      
                      <div className="flex gap-2">
                        <Input 
                          placeholder="Add a new content outline item"
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              addListItem(index, 'content_outline', e.currentTarget.value)
                              e.currentTarget.value = ''
                            }
                          }}
                        />
                        <Button 
                          variant="outline" 
                          onClick={(e) => {
                            const input = e.currentTarget.previousElementSibling as HTMLInputElement
                            addListItem(index, 'content_outline', input.value)
                            input.value = ''
                          }}
                        >
                          Add
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      <div className="flex justify-end mt-6">
        <Button 
          onClick={handleSubmit}
          disabled={submitting}
          size="lg"
        >
          {submitting ? 'Approving...' : 'Approve Plan & Start Research'}
        </Button>
      </div>
    </div>
  )
}
