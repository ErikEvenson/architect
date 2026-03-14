import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { questionsApi } from "../api/client";
import type { Question } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { EmptyState } from "../components/Common/EmptyState";

const CATEGORIES = ["requirements", "security", "scaling", "compliance", "cost", "operations"] as const;

export function QuestionListPage() {
  const { versionId } = useParams<{ clientId: string; projectId: string; versionId: string }>();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [questionText, setQuestionText] = useState("");
  const [category, setCategory] = useState<string>("requirements");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [answeringId, setAnsweringId] = useState<string | null>(null);
  const [answerText, setAnswerText] = useState("");

  useEffect(() => {
    if (!versionId) return;
    const params: { status?: string } = {};
    if (statusFilter) params.status = statusFilter;
    questionsApi.list(versionId, params).then(setQuestions).catch(() => {});
  }, [versionId, statusFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!versionId || !questionText.trim()) return;
    const q = await questionsApi.create(versionId, {
      question_text: questionText.trim(),
      category: category as Question["category"],
    });
    setQuestions((prev) => [...prev, q]);
    setQuestionText("");
    setShowForm(false);
  };

  const handleAnswer = async (questionId: string) => {
    if (!versionId || !answerText.trim()) return;
    const updated = await questionsApi.update(versionId, questionId, {
      answer_text: answerText.trim(),
      status: "answered",
    });
    setQuestions((prev) => prev.map((q) => (q.id === questionId ? updated : q)));
    setAnsweringId(null);
    setAnswerText("");
  };

  const openCount = questions.filter((q) => q.status === "open").length;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Questions</h1>
          {openCount > 0 && (
            <p className="text-sm text-orange-400 mt-1">{openCount} open question{openCount !== 1 ? "s" : ""}</p>
          )}
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          New Question
        </button>
      </div>

      {/* Filter */}
      <div className="mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1"
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="answered">Answered</option>
          <option value="deferred">Deferred</option>
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-3">
          <textarea
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
            placeholder="What needs to be clarified?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-600 rounded bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
            autoFocus
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <div className="flex gap-3">
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-400">Cancel</button>
          </div>
        </form>
      )}

      {questions.length === 0 ? (
        <EmptyState message="No questions yet." />
      ) : (
        <div className="space-y-3">
          {questions.map((q) => (
            <div key={q.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <StatusBadge status={q.status} />
                  <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">{q.category}</span>
                </div>
                {q.status === "open" && (
                  <button
                    onClick={() => { setAnsweringId(q.id); setAnswerText(""); }}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Answer
                  </button>
                )}
              </div>
              <p className="text-gray-100 font-medium">{q.question_text}</p>
              {q.answer_text && (
                <div className="mt-2 pl-3 border-l-2 border-green-700">
                  <p className="text-sm text-gray-700">{q.answer_text}</p>
                </div>
              )}
              {answeringId === q.id && (
                <div className="mt-3 flex gap-2">
                  <input
                    type="text"
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    placeholder="Type answer..."
                    className="flex-1 px-3 py-1.5 border border-gray-600 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                    autoFocus
                  />
                  <button
                    onClick={() => handleAnswer(q.id)}
                    className="px-3 py-1.5 bg-green-700 text-white text-sm rounded hover:bg-green-600"
                  >
                    Submit
                  </button>
                  <button onClick={() => setAnsweringId(null)} className="px-3 py-1.5 text-gray-400 text-sm">
                    Cancel
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
