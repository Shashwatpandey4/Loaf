import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Send, ChefHat } from "lucide-react";
import { MealPlanDisplay } from "./MealPlanDisplay";
import { TaskProgress } from "./TaskProgress";

interface Message {
  role: "user" | "assistant";
  content: string;
  mealPlan?: MealPlan;
  showTaskProgress?: boolean;
}

interface MealPlan {
  title: string;
  days: {
    day: string;
    meals: {
      name: string;
      description: string;
    }[];
  }[];
}

interface ChatInterfaceProps {
  userName: string;
}

export function ChatInterface({
  userName,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsProcessing(true);

    // Simulate AI processing
    setTimeout(() => {
      const mockMealPlan: MealPlan = {
        title: "Your Weekly Meal Plan",
        days: [
          {
            day: "Day 1",
            meals: [
              {
                name: "Creamy Mushroom Pasta",
                description:
                  "Rich and creamy pasta with wild mushrooms",
              }
            ],
          },
          {
            day: "Day 2",
            meals: [
              {
                name: "Olive Tapenade Flatbread",
                description:
                  "If you want to add more lacto ovo vegetarian recipes to your recipe box, Olive Tapenade Flatbread might be a recipe you should try",
              }
            ],
          },
          {
            day: "Day 3",
            meals: [
              {
                name: "Pretzels",
                description:
                  "The perfect salty side to your movies",
              }
            ],
          },
          {
            day: "Day 4",
            meals: [
              {
                name: "Coconut Israeli Couscous Studded With Pomegranate",
                description:
                  "Coconut Israeli Couscous Studded With Pomegranate is a side dish that serves 4",
              }
            ],
          },
          {
            day: "Day 5",
            meals: [
              {
                name: "Broccoli Cheddar Soup, A Panera Bread Co. Copycat",
                description:
                  "Broccoli Cheddar Soup, A Panera Bread Co",
              }
            ],
          },
          {
            day: "Day 6",
            meals: [
              {
                name: "Tapioca Pudding with Pineapple and Coconut",
                description:
                  "Tapioca Pudding with Pineapple and Coconut might be a good recipe to expand your dessert recipe box",
              }
            ],
          },
          {
            day: "Day 7",
            meals: [
              {
                name: "Roasted Beet Hummus",
                description:
                  "Roasted Beet Hummus requires roughly 45 minutes from start to finish",
              }
            ],
          }
        ],
      };

      const assistantMessage: Message = {
        role: "assistant",
        content: `Hi ${userName}! I've created a personalized meal plan for you. Let me take care of everything else.`,
        mealPlan: mockMealPlan,
        showTaskProgress: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsProcessing(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen flex flex-col bg-muted">
      {/* Header */}
      <div className="border-b border-border p-4 bg-white shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="bg-secondary rounded-full p-2">
            <ChefHat className="w-5 h-5 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-foreground">Loaf</h3>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="bg-secondary rounded-full p-8 inline-block mb-6">
                <ChefHat className="w-16 h-16 text-primary" />
              </div>
              <h2 className="mb-3 text-foreground">Hello, {userName}!</h2>
              <p className="text-muted-foreground max-w-md mx-auto text-base">
                Tell me what you'd like to eat this week, and
                I'll create a meal plan, order groceries, and
                schedule everything for you.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl ${
                    message.role === "user"
                      ? "bg-secondary text-secondary-foreground rounded-2xl px-5 py-3 shadow-sm border border-border"
                      : "w-full"
                  }`}
                >
                  {message.role === "user" ? (
                    <p className="text-base">{message.content}</p>
                  ) : (
                    <div className="space-y-4">
                      <p className="text-base">{message.content}</p>
                      {message.mealPlan && (
                        <MealPlanDisplay
                          mealPlan={message.mealPlan}
                        />
                      )}
                      {message.showTaskProgress && (
                        <TaskProgress />
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl px-5 py-3 shadow-sm border border-border">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div
                      className="w-2 h-2 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    Planning your meals...
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border p-4 bg-white">
        <form
          onSubmit={handleSubmit}
          className="max-w-4xl mx-auto"
        >
          <div className="rounded-2xl p-2 flex items-end gap-2 bg-muted border border-border">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your ideal meals for the week..."
              className="flex-1 border-0 bg-transparent resize-none focus-visible:ring-0 min-h-[60px] max-h-[200px] text-base"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <Button
              type="submit"
              size="icon"
              className="bg-primary text-primary-foreground hover:bg-[var(--primary-dark)] rounded-full shadow-md hover:shadow-lg transition-all duration-300 shrink-0"
              disabled={!input.trim() || isProcessing}
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}