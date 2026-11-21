import { Route, Routes } from "react-router-dom";
import Layout from "./layouts/Layout.jsx";
import Home from "./pages/Home.jsx";
import Resources from "./pages/Resources.jsx";
import ResourceDetail from "./pages/ResourceDetail.jsx";
import Savings from "./pages/Savings.jsx";
import About from "./pages/About.jsx";
import NotFound from "./pages/NotFound.jsx";

// Add new pages here (and in config/navigation.js if they need a menu entry).
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="resources" element={<Resources />} />
        <Route path="resources/:type/:id" element={<ResourceDetail />} />
        <Route path="savings" element={<Savings />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
