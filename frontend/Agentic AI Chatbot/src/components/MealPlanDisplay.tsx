import { Utensils } from "lucide-react";

interface MealPlan {
  title: string;
  days: {
    day: string;
    meals: {
      type: string;
      name: string;
      description: string;
    }[];
  }[];
}

interface MealPlanDisplayProps {
  mealPlan: MealPlan;
}

export function MealPlanDisplay({ mealPlan }: MealPlanDisplayProps) {
  return (
    <div className="bg-white rounded-2xl p-6 mt-4 shadow-md border border-border">
      <h3 className="mb-6 text-lg text-foreground">{mealPlan.title}</h3>
      
      <div className="space-y-6">
        {mealPlan.days.map((day, dayIndex) => (
          <div key={dayIndex} className="space-y-3">
            <h4 className="text-base font-semibold text-primary">{day.day}</h4>
            
            <div className="space-y-2">
              {day.meals.map((meal, mealIndex) => (
                <div
                  key={mealIndex}
                  className="bg-muted rounded-xl p-4 flex gap-3 border border-border"
                >
                  <div className="bg-secondary rounded-lg p-2 h-fit">
                    <Utensils className="w-4 h-4 text-primary" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="text-xs text-muted-foreground uppercase tracking-wide">
                        {meal.type}
                      </span>
                      <span className="text-foreground text-sm font-medium">
                        {meal.name}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {meal.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}