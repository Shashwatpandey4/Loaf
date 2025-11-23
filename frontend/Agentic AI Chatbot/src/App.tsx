import { useState } from "react";
import { SignUpScreen } from "./components/SignUpScreen";
import { SignUpForm } from "./components/SignUpForm";
import { ChatInterface } from "./components/ChatInterface";
import "./styles/globals.css";

type Screen = "welcome" | "form" | "chat";

interface UserData {
  name: string;
  email: string;
  dietaryConstraints: string[];
  healthConditions: string[];
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("welcome");
  const [userData, setUserData] = useState<UserData | null>(null);

  const handleGetStarted = () => {
    setCurrentScreen("form");
  };

  const handleFormComplete = (data: UserData) => {
    setUserData(data);
    setCurrentScreen("chat");
  };

  return (
    <div className="min-h-screen">
      {currentScreen === "welcome" && (
        <SignUpScreen onGetStarted={handleGetStarted} />
      )}
      
      {currentScreen === "form" && (
        <SignUpForm onComplete={handleFormComplete} />
      )}
      
      {currentScreen === "chat" && userData && (
        <ChatInterface userName={userData.name} />
      )}
    </div>
  );
}
