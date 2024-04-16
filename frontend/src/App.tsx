import "./App.css";
import { NavLink, Outlet, Route, Routes } from "react-router-dom";
import Mirror from "./components/Mirror";
import { alphabetChallenges, commonSignsChallenges } from "./challenges";
import Recognizer from "./components/Recognizer";

function Layout() {
  return (
    <div className="p-2">
      <nav className=" flex gap-4 mb-4">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/alphabet">Learn the Alphabet</NavLink>
        <NavLink to="/common-signs">Learn Common Signs</NavLink>
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
          <Route index element={<Welcome />} />
          <Route
            path="alphabet"
            Component={() => (
              <Recognizer dynamic={false} challenges={alphabetChallenges} />
            )}
          />
          <Route
            path="common-signs"
            Component={() => (
              <Recognizer dynamic={true} challenges={commonSignsChallenges} />
            )}
          />
          <Route path="mirror" element={<Mirror />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
