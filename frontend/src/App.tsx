import "./App.css";
import { NavLink, Outlet, Route, Routes } from "react-router-dom";
import LetterRecognizer from "./components/LetterRecognizer";
import Mirror from "./components/Mirror";

function Layout() {
  return (
    <div className="p-2">
      <nav className=" flex gap-4 mb-4">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/alphabet">Learning</NavLink>
        <NavLink to="/mirror">Mirror</NavLink>

      </nav>

      <Outlet />
    </div>
  );
}

function Welcome() {
  return (
    <div className="flex justify-center">
      <h1 className="text-9xl">Welcome</h1>
    </div>
  );
}

function App() {
  return (
    <div className="p-2">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Welcome />}/>
          <Route path="alphabet" element={<LetterRecognizer />} />
          <Route path="mirror" element={<Mirror />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
