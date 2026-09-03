import React, { useState, useRef, useEffect } from 'react';
import * as d3 from 'd3';
import importanceData from '..\\data\\iris.csv';
import { range } from 'd3';

const ConceptImportance = (props) => {
    const ParallelSvgRef = useRef();
    const [imageURL, setImageUrl] = useState(null);

    console.log('Props: ', props);

    useEffect(() => {
        if (props.genre !== null && props.song !== null) {
            let track_id = +props.song.split('|')[1];
            console.log('Selected track and genre: ', track_id, props.genre);
            fetch('/one_song/' + props.genre + '_' + track_id)
                .then(res => res.blob())
                .then(image => {
                    console.log('Response from server: ' + image);
                    setImageUrl(URL.createObjectURL(image));
                })
        }
    }, [props.song]);

    useEffect(() => {
        const songSVG = d3.select(ParallelSvgRef.current);
        songSVG.selectAll('*').remove();
        songSVG
            .append('g')
            .append('image')
            .attr('width', '400px')
            .attr('height', '400px')
            .attr('x', '130')
            .attr('y', '50')
            .attr('xlink:href', imageURL);
            // .attr('transform', 'scale(1.85, 1)');

    }, [imageURL])

    return (
        <React.Fragment>
            <svg ref={ParallelSvgRef} style={{ height: '100%', width: '100%' }} id={props.id}>
            </svg>
        </React.Fragment>
    )
}

export default ConceptImportance;