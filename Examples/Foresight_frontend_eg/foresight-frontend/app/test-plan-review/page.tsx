'use client'

import PlanReview from '@/components/plan-review'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useState } from 'react'

export default function TestPlanReview() {
  const [completed, setCompleted] = useState(false)
  
  const handleComplete = () => {
    setCompleted(true)
  }
  
  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader>
          <CardTitle>Test Plan Review Component</CardTitle>
        </CardHeader>
        <CardContent>
          {completed ? (
            <div className="p-4 bg-green-800/20 border border-green-700 rounded-md">
              <p className="text-green-400">Plan review completed!</p>
              <Button 
                className="mt-4"
                onClick={() => setCompleted(false)}
              >
                Reset
              </Button>
            </div>
          ) : (
            <PlanReview onComplete={handleComplete} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
