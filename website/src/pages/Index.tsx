import { useState } from "react";
import { MessageCircle } from "lucide-react";
import LiveKitWidget from "@/components/ai_avatar/LiveKitWidget";

const Index = () => {
  const [showAvatar, setShowAvatar] = useState(false);
  const [token, setToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleTalkToConcierge = async () => {
    setIsLoading(true);
    setError("");
    try {
      const response = await fetch("https://realtime-ai-avatar-jxcp.onrender.com/getToken?name=Guest&room=default-room");
      if (!response.ok) throw new Error("Failed to get token from backend");
      const tokenData = await response.text();
      setToken(tokenData);
      setShowAvatar(true);
    } catch (err) {
      setError("Failed to connect to AI Concierge. Make sure backend is running.");
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = () => {
    setShowAvatar(false);
    setToken("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      {!showAvatar ? (
        <button
          onClick={handleTalkToConcierge}
          disabled={isLoading}
          className="flex items-center gap-3 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-gray-900 px-8 py-4 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="animate-spin">
              <MessageCircle className="w-6 h-6" />
            </div>
          ) : (
            <MessageCircle className="w-6 h-6" />
          )}
          <span>{isLoading ? "Connecting..." : "Talk to AI Concierge"}</span>
        </button>
      ) : (
        <div className="w-full h-screen">
          {token && (
            <LiveKitWidget 
              token={token} 
              serverUrl="wss://livekit.example.com"
              onDisconnect={handleDisconnect}
            />
          )}
        </div>
      )}

      {error && (
        <div className="fixed bottom-4 left-4 right-4 bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg">
          {error}
        </div>
      )}
    </div>
  );
};

export default Index;
