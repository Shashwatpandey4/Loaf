import { useState, useEffect } from "react";
import { ShoppingCart, CreditCard, Calendar, Check, Loader2 } from "lucide-react";

interface Task {
  id: string;
  label: string;
  icon: React.ReactNode;
  status: "pending" | "processing" | "complete";
}

export function TaskProgress() {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: "groceries",
      label: "Adding groceries to cart",
      icon: <ShoppingCart className="w-5 h-5" />,
      status: "pending",
    },
    {
      id: "payment",
      label: "Processing payment via Stripe",
      icon: <CreditCard className="w-5 h-5" />,
      status: "pending",
    },
    {
      id: "calendar",
      label: "Creating Google Calendar events",
      icon: <Calendar className="w-5 h-5" />,
      status: "pending",
    },
  ]);

  const [allComplete, setAllComplete] = useState(false);

  useEffect(() => {
    // Simulate parallel task processing
    const timers: NodeJS.Timeout[] = [];

    // Start all tasks after a brief delay
    const startDelay = setTimeout(() => {
      setTasks((prev) =>
        prev.map((task) => ({ ...task, status: "processing" as const }))
      );

      // Complete tasks at different times (simulating parallel processing)
      const taskTimings = [2000, 2500, 2200]; // Different completion times

      taskTimings.forEach((timing, index) => {
        const timer = setTimeout(() => {
          setTasks((prev) =>
            prev.map((task, i) =>
              i === index ? { ...task, status: "complete" as const } : task
            )
          );
        }, timing);
        timers.push(timer);
      });

      // Check if all complete
      const checkComplete = setTimeout(() => {
        setAllComplete(true);
      }, Math.max(...taskTimings) + 500);
      timers.push(checkComplete);
    }, 1000);

    timers.push(startDelay);

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, []);

  return (
    <div className="bg-white rounded-2xl p-6 mt-4 shadow-md border border-border">
      <h4 className="mb-4 text-base font-semibold text-foreground">Processing Your Request</h4>
      
      <div className="space-y-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="bg-muted rounded-xl p-4 flex items-center gap-3 border border-border"
          >
            <div
              className={`rounded-lg p-2 transition-all duration-300 ${
                task.status === "complete"
                  ? "bg-success text-success-foreground"
                  : task.status === "processing"
                  ? "bg-info text-info-foreground"
                  : "bg-secondary text-muted-foreground"
              }`}
            >
              {task.status === "complete" ? (
                <Check className="w-4 h-4" />
              ) : task.status === "processing" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                task.icon
              )}
            </div>
            
            <span
              className={`flex-1 text-sm transition-colors duration-300 ${
                task.status === "complete"
                  ? "text-foreground"
                  : "text-muted-foreground"
              }`}
            >
              {task.label}
            </span>
            
            {task.status === "complete" && (
              <span className="text-xs text-success font-medium">Complete</span>
            )}
            {task.status === "processing" && (
              <span className="text-xs text-info font-medium">Processing...</span>
            )}
          </div>
        ))}
      </div>

      {allComplete && (
        <div className="mt-6 rounded-xl p-4 bg-success/10 border-2 border-success/30">
          <div className="flex items-center gap-3">
            <div className="rounded-full p-2 bg-success text-success-foreground">
              <Check className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <p className="text-success font-medium text-sm">All set!</p>
              <p className="text-xs text-muted-foreground">
                Your meal plan is ready, groceries are ordered, and calendar events are created.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}