import { GlobeIcon } from "lucide-react"

export function ForesightHeader() {
  return (
    <header className="border-b border-slate-700 bg-slate-900">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GlobeIcon className="h-6 w-6 text-blue-400" />
            <span className="text-xl font-bold">Foresight</span>
          </div>
          <nav>
            <ul className="flex items-center gap-6">
              <li>
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  Reports
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  Settings
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  )
}

