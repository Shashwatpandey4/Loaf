import { Button } from "./ui/button";
import { ChefHat } from "lucide-react";

interface SignUpScreenProps {
  onGetStarted: () => void;
}

export function SignUpScreen({ onGetStarted }: SignUpScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-muted">
      <div className="bg-white rounded-3xl shadow-xl p-12 max-w-lg w-full text-center">
        <div className="flex justify-center mb-6">
          <div className="bg-secondary rounded-full p-6">
            <ChefHat className="w-12 h-12 text-primary" />
          </div>
        </div>
        
        <h1 className="mb-3 text-foreground">Welcome to Loaf</h1>
        <p className="text-muted-foreground mb-8 leading-relaxed text-base">
          Your personal AI chef that plans meals, orders groceries, and handles everything with a single prompt. 
          Let's make mealtime effortless.
        </p>
        
        <Button 
          onClick={onGetStarted}
          className="bg-primary text-primary-foreground hover:bg-[var(--primary-dark)] rounded-full px-8 py-6 shadow-lg hover:shadow-xl transition-all duration-300 text-base"
        >
          Get Started
        </Button>
      </div>
    </div>
  );
}