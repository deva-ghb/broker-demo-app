import { createBrowserRouter } from "react-router";
import JourneyPage from "./pages/JourneyPage";
import ChatPage from "./pages/ChatPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: JourneyPage,
  },
  {
    path: "/chat",
    Component: ChatPage,
  },
]);
