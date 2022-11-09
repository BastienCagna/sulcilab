import React from "react";
import { PSubject } from "../../../api";
import SubjectCard from './subjectcard';
import './subjectlist.css';

export default class SubjectList extends React.Component {
    subjects: PSubject[] = [];

    constructor(props: any) {
        super(props);
        //this.subjects = props.subjects ? props.subjects : [];
    }

    // componentDidUpdate(prevProps) {
    //     if(prevProps)
    // }

    handleSelectSubject = (subject: PSubject) => { 
        if(this.props.onSelectSubject)
            this.props.onSelectSubject(subject);
    };

    render() {
        const subjects = this.props.subjects ? this.props.subjects : [];
        const listItems = subjects.map((subject) => <li className="subject-card-item" key={subject.id}><SubjectCard subject={subject} onClick={this.handleSelectSubject} ></SubjectCard></li> );  
        return ( <ul>{listItems}</ul> );
    }
}
