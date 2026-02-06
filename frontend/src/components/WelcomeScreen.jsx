import React from "react";
import { Sparkles, Database, Code, CheckCircle, Shield } from "lucide-react";

const WelcomeScreen = ({ onExampleClick }) => {
  const examples = [
    {
      icon: Database,
      text: "Show me all customers who placed orders in 2024",
      category: "Query Generation"
    },
    {
      icon: Database,
      text: "List the top 5 products by sales revenue",
      category: "Aggregation"
    },
    {
      icon: Database,
      text: "Find users who haven't logged in for 30 days",
      category: "Filtering"
    },
    {
      icon: Database,
      text: "Calculate average order value by customer segment",
      category: "Analytics"
    }
  ];

  const features = [
    {
      icon: Code,
      title: "Natural Language to SQL",
      description: "Convert plain English questions into optimized SQL queries"
    },
    {
      icon: Shield,
      title: "Safety First",
      description: "Automatic validation blocks dangerous operations"
    },
    {
      icon: CheckCircle,
      title: "Syntax Validated",
      description: "All queries are checked for correctness before display"
    }
  ];

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-12 animate-fade-in">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Database size={32} className="text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
            SQL Agent
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Your AI-powered SQL query assistant. Define your database schema and ask questions in plain English to generate accurate SQL queries instantly.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="p-4 bg-slate-800/30 border border-slate-700 rounded-xl hover:border-emerald-500/50 transition-all group"
              >
                <div className="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-emerald-500/30 transition-colors">
                  <Icon size={20} className="text-emerald-400" />
                </div>
                <h3 className="font-semibold text-slate-200 mb-1">{feature.title}</h3>
                <p className="text-sm text-slate-400">{feature.description}</p>
              </div>
            );
          })}
        </div>

        {/* Example Prompts */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Sparkles size={16} className="text-emerald-400" />
            <span>Try these example questions:</span>
          </div>
          <div className="grid md:grid-cols-2 gap-3">
            {examples.map((example, index) => {
              const Icon = example.icon;
              return (
                <button
                  key={index}
                  onClick={() => onExampleClick(example.text)}
                  className="group p-4 bg-slate-800/30 border border-slate-700 rounded-xl hover:border-emerald-500 hover:bg-slate-800/50 transition-all text-left"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-slate-700 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-emerald-500/20 transition-colors">
                      <Icon size={16} className="text-slate-400 group-hover:text-emerald-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-xs text-emerald-400 font-medium">{example.category}</span>
                      <p className="text-sm text-slate-300 group-hover:text-slate-200 transition-colors mt-1">
                        "{example.text}"
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Getting Started */}
        <div className="p-5 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-xl">
          <h3 className="font-semibold text-emerald-400 mb-2">🚀 Getting Started</h3>
          <ol className="text-sm text-slate-300 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-semibold">1.</span>
              <span>Define your database schema above (or load the example)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-semibold">2.</span>
              <span>Ask your question in plain English</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-semibold">3.</span>
              <span>Get a validated SQL query instantly</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
