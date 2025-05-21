import { ForesightForm } from "@/components/foresight-form"
import { ForesightHeader } from "@/components/foresight-header"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <ForesightHeader />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Foresight AI</h1>
            <p className="text-slate-300">
              Configure your strategic foresight report by filling out the form below. Our AI agents will analyze the
              data and generate insights based on your specifications.
            </p>
          </div>
          <ForesightForm />
        </div>
      </main>
    </div>
  )
}

