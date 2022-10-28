import React from "react";
import { PSubject } from "../../../api";
import SubjectCard from './subjectcard';
import './subjectlist.css';

export default class SubjectList extends React.Component {
    subjects: PSubject[] = [];

    constructor(props: any) {
        super(props);
        this.subjects = props.subjects ? props.subjects : [];
    }

    render() {
        const listItems = this.subjects.map((subject) => <li className="subject-card-item" key={subject.id}><SubjectCard subject={subject} ></SubjectCard></li> );  
        return ( <ul className="subject-list">{listItems}</ul> );
    }
}
