import React from "react";
import SubjectCard from './subjectcard';
import './subjectlist.css';

export default class SubjectList extends React.Component {
    render() {
        const listItems = this.props.subjects.map((subject) => <li className="subject-card-item" key={subject.id}><SubjectCard subject={subject} ></SubjectCard></li> );  
        return ( <ul className="subject-list">{listItems}</ul> );
    }
}
