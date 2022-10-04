import { Outlet, Link } from "react-router-dom";

import image from '../../assets/images/404.webp'
import {Callout} from '@blueprintjs/core';

function UnderConstruction() {
  return (
    <Callout title="This element is under construction" intent="danger">
    </Callout>
  );
}

export default UnderConstruction;
