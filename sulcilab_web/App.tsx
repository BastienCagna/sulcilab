import './App.css';
import { Outlet, Link } from "react-router-dom";

function App() {
  return (
    
    <div className="app">
      <Outlet />
      <footer>
        <p>Created by <a href="http://bablab.fr" rel="noreferrer" target="_blank">Bastien Cagna</a></p>
      </footer>
    </div>
  );
}

export default App;
