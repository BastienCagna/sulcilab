import { Outlet, Link } from "react-router-dom";
import image from '../../assets/images/404.webp'

function PageNotFound() {
  return (
    <div className="404">
        <img src={image} height="300px" width="auto" />
      <h1>Page not found</h1>
      <p>The page that you are requesting do not exist.</p>
    </div>
  );
}

export default PageNotFound;
