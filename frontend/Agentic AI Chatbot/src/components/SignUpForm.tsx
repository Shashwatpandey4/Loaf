import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { ChefHat } from "lucide-react";

interface SignUpFormProps {
  onComplete: (data: {
    name: string;
    email: string;
    dietaryConstraints: string[];
    healthConditions: string[];
  }) => void;
}

const dietaryOptions = [
  "Vegetarian",
  "Pescatarian",
  "Vegan",
  "Keto",
  "Paleo",
  "Halal",
];

const healthOptions = [
  "Diabetes",
  "Blood Pressure",
  "Gluten Allergy",
  "Lactose Intolerant",
  "Nut Allergy",
  "Shellfish Allergy",
];

export function SignUpForm({ onComplete }: SignUpFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [dietaryConstraints, setDietaryConstraints] = useState<string[]>([]);
  const [healthConditions, setHealthConditions] = useState<string[]>([]);

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (value && !validateEmail(value)) {
      setEmailError("Please enter a valid email address");
    } else {
      setEmailError("");
    }
  };

  const toggleOption = (option: string, list: string[], setter: (list: string[]) => void) => {
    if (list.includes(option)) {
      setter(list.filter((item) => item !== option));
    } else {
      setter([...list, option]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !email) {
      return;
    }
    
    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address");
      return;
    }

    onComplete({
      name,
      email,
      dietaryConstraints,
      healthConditions,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-muted">
      <div className="bg-white rounded-3xl shadow-xl p-8 max-w-2xl w-full">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-secondary rounded-full p-2">
            <ChefHat className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-2xl font-semibold text-foreground" style={{ fontFamily: 'var(--font-body)' }}>Create your profile</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-foreground">Name</Label>
            <Input
              id="name"
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-xl border border-border bg-input-background px-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-foreground">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => handleEmailChange(e.target.value)}
              className={`rounded-xl border bg-input-background px-4 py-3 transition-all ${
                emailError ? "border-destructive ring-2 ring-destructive" : "border-border focus:ring-2 focus:ring-primary focus:border-transparent"
              }`}
              required
            />
            {emailError && (
              <p className="text-destructive text-sm mt-1">{emailError}</p>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <Label className="mb-3 block text-foreground">Dietary Constraints</Label>
              <div className="flex flex-wrap gap-2">
                {dietaryOptions.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() =>
                      toggleOption(option, dietaryConstraints, setDietaryConstraints)
                    }
                    className={`px-4 py-2 rounded-full text-sm transition-all duration-200 ${
                      dietaryConstraints.includes(option)
                        ? "bg-primary text-primary-foreground shadow-md"
                        : "bg-secondary text-secondary-foreground border border-border hover:border-primary hover:shadow-sm"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label className="mb-3 block text-foreground">Health Conditions</Label>
              <div className="flex flex-wrap gap-2">
                {healthOptions.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() =>
                      toggleOption(option, healthConditions, setHealthConditions)
                    }
                    className={`px-4 py-2 rounded-full text-sm transition-all duration-200 ${
                      healthConditions.includes(option)
                        ? "bg-primary text-primary-foreground shadow-md"
                        : "bg-secondary text-secondary-foreground border border-border hover:border-primary hover:shadow-sm"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full bg-primary text-primary-foreground hover:bg-[var(--primary-dark)] rounded-full py-6 shadow-lg hover:shadow-xl transition-all duration-300 mt-8 text-base"
            disabled={!name || !email || !!emailError}
          >
            Continue to Chat
          </Button>
        </form>
      </div>
    </div>
  );
}