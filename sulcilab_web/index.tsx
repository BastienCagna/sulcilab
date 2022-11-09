import ReactDOM from 'react-dom/client';import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";
import './index.css';
import reportWebVitals from './reportWebVitals';
import App from './App';
import Home from './public/home/home';
import Learn from './public/learn/learn';
import Contribute from './protected/contribute/contribute';
import View from './protected/view/view';
import Edit from './protected/edit/edit';
import SignIn from './public/signin/signin';
import SignOut from './public/signout/signout';

import 'normalize.css/normalize.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import '@blueprintjs/popover2/lib/css/blueprint-popover2.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/select/lib/css/blueprint-select.css';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />}>
        <Route path="" element={<Home />} />
        <Route path="learn" element={<Learn />} />
        <Route path="contribute" element={<Contribute />} />
        <Route path="view" element={<View />} />
        <Route path="edit" element={<Edit />} />
        <Route path="signout" element={<SignOut />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
