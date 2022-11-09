import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const withNavigateHook = (Component) => {
    return (props) => {
        const navigation = useNavigate();
        const location = useLocation();
        const editableProps = {}
        for(let key in props) {
            editableProps[key] = props[key];
        }
        if(location.state) {
            for(let key in location.state) {
                editableProps[key] = location.state[key];
            }
        }
        return <Component navigation={navigation} {...editableProps} />
    }
}

export default withNavigateHook;