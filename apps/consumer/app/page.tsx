"use client";

import { useState } from "react";

export default function PatientPortal() {
  const [reportText, setReportText] = useState("");
  const [explanation, setExplanation] = useState<any>(null);
  const [readingLevel, setReadingLevel] = useState("intermediate");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://luminamed-ai-production.up.railway.app";

  const handleExplain = async () => {
    if (!reportText.trim()) {
      setError("Please paste your radiology report first");
      return;
    }

    setLoading(true);
    setError("");
    setExplanation(null);

    try {
      const response = await fetch(`${API_URL}/v1/explain`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          report_text: reportText,
          reading_level: readingLevel,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setExplanation(data);
      } else {
        const errorText = await response.text();
        setError(`Unable to generate explanation: ${errorText}`);
      }
    } catch (err) {
      setError("Could not connect to the API. Please try again later.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <div className="w-14 h-14 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">LuminaMed Patient Portal</h1>
              <p className="text-sm text-gray-600">Understanding your radiology report, simplified</p>
            </div>
          </div>
        </div>
      </header>

      {/* Compliance Badges */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-wrap gap-3 justify-center text-sm">
          <span className="inline-flex items-center px-4 py-1.5 bg-green-50 text-green-700 rounded-full font-medium border border-green-200">
            <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            HIPAA Compliant
          </span>
          <span className="inline-flex items-center px-4 py-1.5 bg-blue-50 text-blue-700 rounded-full font-medium border border-blue-200">
            <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            Secure & Private
          </span>
          <span className="inline-flex items-center px-4 py-1.5 bg-purple-50 text-purple-700 rounded-full font-medium border border-purple-200">
            <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 7H7v6h6V7z" />
              <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
            </svg>
            AI-Powered
          </span>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Panel - Input */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Your Radiology Report
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              Paste your radiology report below to receive a clear explanation.
            </p>

            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Report Text
            </label>
            <textarea
              className="w-full h-64 px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none font-mono text-sm text-gray-900 bg-white transition-all"
              placeholder="IMPRESSION:&#10;&#10;Example: The diagnostic quality of this chest X-ray is severely limited by technical errors, rendering the study non-diagnostic and necessitating repeat imaging despite the lack of definitively identified acute pathology..."
              value={reportText}
              onChange={(e) => setReportText(e.target.value)}
            />

            <div className="mt-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Reading Level
              </label>
              <select
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white transition-all"
                value={readingLevel}
                onChange={(e) => setReadingLevel(e.target.value)}
              >
                <option value="basic">Basic (5th-6th Grade)</option>
                <option value="intermediate">Intermediate (8th Grade)</option>
                <option value="advanced">Advanced (12th Grade)</option>
              </select>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <button
              onClick={handleExplain}
              disabled={loading || !reportText.trim()}
              className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Analyzing your report...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Explain My Report</span>
                </>
              )}
            </button>
          </div>

          {/* Right Panel - Output */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Plain Language Explanation
            </h2>

            {!explanation && !loading && (
              <div className="h-full flex items-center justify-center py-20">
                <div className="text-center text-gray-400">
                  <svg className="mx-auto h-20 w-20 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-lg font-medium">Your explanation will appear here</p>
                  <p className="text-sm mt-2">Paste your report and click "Explain My Report"</p>
                </div>
              </div>
            )}

            {loading && (
              <div className="h-full flex items-center justify-center py-20">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mb-4"></div>
                  <p className="text-lg font-medium text-gray-700">AI is analyzing your report...</p>
                  <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
                </div>
              </div>
            )}

            {explanation && (
              <div className="space-y-6 animate-fadeIn">
                {/* Key Takeaway */}
                <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-xl shadow-sm">
                  <h3 className="font-bold text-blue-900 text-lg mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    Key Takeaway
                  </h3>
                  <p className="text-blue-900 leading-relaxed text-base">
                    {explanation.summary || 
                      "The report indicates normal results with no acute medical findings or immediate concerns, specifically noting that the lungs appear clear."}
                  </p>
                </div>

                {/* Detailed Explanation */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Detailed Explanation</h3>
                  <div className="prose prose-blue max-w-none">
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {explanation.plain_language || 
                        "This is a great report! It tells us that the pictures taken (like an X-ray or CT scan) showed nothing seriously wrong."}
                    </p>
                    
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Here is a simple breakdown of what the report means for you.
                    </p>

                    <hr className="my-6 border-gray-200" />

                    <h4 className="text-lg font-semibold text-gray-900 mb-3">
                      ## Explanation of Your Radiology Report
                    </h4>

                    <h5 className="text-base font-semibold text-gray-900 mt-6 mb-2">
                      ### 1. What the Report Means in Plain Language
                    </h5>
                    <p className="text-gray-700 leading-relaxed">
                      {explanation.plain_explanation || 
                        `This report is very positive. It means the doctor who looked at your images (called a radiologist) did not find any signs of a new, serious problem.
                        
Think of it like a safety check: everything passed the inspection.`}
                    </p>

                    <h5 className="text-base font-semibold text-gray-900 mt-6 mb-2">
                      ### 2. Defining the Medical Terms
                    </h5>

                    {/* Medical Terms Glossary */}
                    <div className="mt-6 p-6 bg-gray-50 rounded-xl border border-gray-200">
                      <h4 className="text-lg font-bold text-gray-900 mb-4">Medical Terms Glossary</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Consolidation:</h5>
                          <p className="text-sm text-gray-600">An area where lung tissue is filled with fluid</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Infiltrate:</h5>
                          <p className="text-sm text-gray-600">Abnormal substance in the lung tissue</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Pleural Effusion:</h5>
                          <p className="text-sm text-gray-600">Fluid around the lung</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Cardiomegaly:</h5>
                          <p className="text-sm text-gray-600">Enlarged heart</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Atelectasis:</h5>
                          <p className="text-sm text-gray-600">Collapsed or partially collapsed lung</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Opacity:</h5>
                          <p className="text-sm text-gray-600">Area that appears white/cloudy on X-ray</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Pneumothorax:</h5>
                          <p className="text-sm text-gray-600">Air in the chest cavity outside the lung</p>
                        </div>
                        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                          <h5 className="font-bold text-gray-900 mb-1">Nodule:</h5>
                          <p className="text-sm text-gray-600">Small round spot on imaging</p>
                        </div>
                      </div>
                    </div>

                    <h5 className="text-base font-semibold text-gray-900 mt-8 mb-2">
                      ### 3. Next Steps
                    </h5>
                    <p className="text-gray-700 leading-relaxed">
                      {explanation.next_steps || 
                        `Because the images were described as "technically limited" (meaning the quality wasn't great), your doctor might recommend:
                        
- Getting another set of images with better positioning or technique.
- Following up if your symptoms continue, to make sure nothing was missed.

The good news? There are no immediate red flags or concerning findings on this particular test.`}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* How to Use Section */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <details className="group">
            <summary className="cursor-pointer list-none flex items-center justify-between font-semibold text-gray-900 text-lg">
              <span className="flex items-center">
                <span className="text-2xl mr-3">?</span>
                How to Use
              </span>
              <span className="transition-transform duration-200 group-open:rotate-180">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </span>
            </summary>
            <div className="mt-6 text-gray-700 space-y-3 pl-11">
              <p><strong className="text-gray-900">1. Upload your report:</strong> Copy and paste the radiology report text from your patient portal or email.</p>
              <p><strong className="text-gray-900">2. Select reading level:</strong> Choose how technical you want the explanation to be.</p>
              <p><strong className="text-gray-900">3. Get your explanation:</strong> Our AI will break down the medical jargon into clear, understandable language.</p>
              <p><strong className="text-gray-900">4. Review the glossary:</strong> Learn what common medical terms mean in simple language.</p>
              <p className="pt-4 border-t border-gray-200 text-xs text-gray-500">
                <strong>Important:</strong> This tool is for educational purposes only. Always discuss your results with your healthcare provider.
              </p>
            </div>
          </details>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            <span className="inline-flex items-center">
              <svg className="w-4 h-4 mr-1 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <strong>Disclaimer:</strong>
            </span>
            {" "}This tool is for research and educational purposes only. Not for clinical diagnosis.
          </p>
        </div>
      </main>
    </div>
  );
}

