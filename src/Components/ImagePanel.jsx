import React, { useState, useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { image } from 'd3';
import listReactFiles from 'list-react-files';

const ImagePanel = (props) => {
    // console.log('Before reading image ref');
    const imageSvgRef = useRef();
    // console.log('After reading image ref', imageSvgRef);
    const [imageData, setImageData] = useState([]);
    const [trackNames, setTrackNames] = useState([]);
    // let trackNames = new Array();
    // console.log('Loaded image panel.', props.selectedConcept);

    useEffect(() => {
        if(props.selectedConcept !== null) {

            let backendData;
            fetch('/' + props.selectedConcept, {mode: 'no-cors'})
                .then((res) => { 
                    let data = res.json(); 
                    // console.log('Data from backend was: ', data);
                    return data;
                })
                .then((data) => {
                    data = data.conceptExamples;
                    // console.log('Before data wrangling: ', data);
                    data.forEach((item, index) => {
                        item = item.split('/').join('\\');
                        let splits = item.split('public');
                        data[index] = '.' + splits[splits.length - 1];
                        // data[index] = item.replace('\\mnt\\f\\', 'f:\\');
                    })
                    // console.log('After data wrangling: ', typeof data);
                    setImageData(data);
                })
        }
        else {
            setImageData([]);
        }
    }, [props.selectedConcept]);

    useEffect(() => {
        if (imageData !== []) {
            let track_ids = '';
            for (let track_path of imageData) {
                let splits = track_path.split('/');
                let baseFile = splits[splits.length-1];
                let track_id = baseFile.split('_').at(-1).split('.')[0];
                // console.log('Current track id is: ', track_id);
                track_ids += track_id + '_';
            }
            // let tracks_ids = track_ids.slice(0, -2);
            // console.log('Track ids: ', track_ids);
            let trackData = new Array();
            fetch('/meta/' + track_ids, {mode: 'no-cors'})
                .then((res) => { return res.json();})
                .then((data) => {
                    data = data.data;
                    // console.log('Before parsing metadata: ', data);
                    data = JSON.parse(data);
                    // console.log('After parsing metadata: ', data);
                    // console.log('Now image data is: ', imageData);
                    imageData.forEach((track_path, index) => {
                        let splits = track_path.split('Music_Dataset');
                        let local_path = '.\\' + splits[splits.length - 1]
                        imageData[index] = local_path;
                        let baseFile = local_path.split('\\');
                        baseFile = baseFile[baseFile.length - 1]
                        // console.log('basefile is: ', baseFile)
                        let track_id = +baseFile.split('_').at(-1).split('.')[0];
                        // console.log('Finding: ', track_id);
                        // console.log('result from find: ', data.find(x => x.track_id === track_id), data.find(x => x.track_id === track_id).track_title);
                        trackData.push(data.find(x => x.track_id === track_id).track_title);
                    })
                    // console.log('Finally track names are: ', trackNames);
                    // console.log('Finally track data is: ', trackData, trackData.length);
                    setTrackNames(trackData);
                    // console.log('Setting track names.');
                })
        }
        else {
            setTrackNames([]);
        }
    }, [imageData]);

    useEffect(() => {

        // console.log('In use effect 3');
        var svg = d3.select(imageSvgRef.current).attr('class', 'imagesSvg');
        svg.selectAll('*').remove();
        if( typeof imageData !== 'undefined' && imageData.length !== 0) {
        // console.log('In use effect 2 if block');
        // console.log('Track names are: ', trackNames, trackNames.length, typeof trackNames);
        var svg_attributes = document.getElementsByClassName('imagesSvg')[0].getBoundingClientRect();
        // console.log('SVG Attributes: ', svg_attributes);
        var imageHeight = (svg_attributes.height-40)/4;
        var imageWidth = imageHeight * 2;
        // console.log('Image Height and  Width vs SVG: ', imageHeight, imageWidth, svg_attributes.height, svg_attributes.width);
        console.log('Image data is: ', imageData);
        svg
            .append('g')
            .selectAll('image').data(imageData)
            .join('image')
            .attr('xlink:href', (d) => `${d}`)
            .attr('width', imageWidth)
            .attr('height', imageHeight)
            .attr('x', (d, i) => {
                let factor = i % 3;
                // if (i % 3 == 0) {
                //     return Math.floor(imageHeight/2) + imageWidth/4;
                // }
                return (factor * ((svg_attributes.width)/3));
            })
            .attr('y', (d, i) => {
                return 30 + (Math.floor((i / 3)) * imageHeight);
            });

        svg
            .append('g')
            .selectAll('imageBorder').data(imageData)
            .enter()
            .insert('rect', 'image')
            // .attr('class', 'imageBorder')
            .attr('width', imageWidth)
            .attr('height', imageHeight)
            .attr('x', (d, i) => {
                let factor = i % 3;
                // if (i % 3 == 0) {
                //     return Math.floor(imageHeight/2) + imageWidth/4;
                // }
                return (factor * ((svg_attributes.width)/3));
            })
            .attr('y', (d, i) => {
                return 30 + (Math.floor((i / 3)) * imageHeight);
            })
            .style('fill', 'none');

        // svg
        //     .append('g')
        //     .attr('class', 'image-labels');
            
        // var imageLabels = d3.selectAll('.image-labels');
        console.log('Tracks data: ', trackNames, trackNames[0]);
        
        svg
            .append('g')
            // .classed('image-labels', true)
            .selectAll('imagelabels')
            .data(trackNames)
            .enter()
            .append('text')
            .attr('x', (d, i) => {
                let factor = i % 3;
                // if (i % 3 == 0) {
                //     return Math.floor(imageHeight/2) + imageWidth/4;
                // }
                return (factor * ((svg_attributes.width)/3)) + 30;
            })
            .attr('y', (d, i) => {
                return 30 + (Math.floor((i / 3) + 1) * imageHeight);
            })
            .style('fill', 'gray')
            .text(function(d) { return d; })
            .style('alignment-baseline', 'middle');

        svg
            .append('g')
            .append('text')
            .text('Concept Patch | Spectrogram')
            .attr('x', 30)
            .attr('y', 30)
            .style('fill', 'gray')
            .style('border', '1px black solid');

        svg
            .append('g')
            .append('text')
            .text('Concept Patch | Spectrogram')
            .attr('x', 30 + svg_attributes.width/3)
            .attr('y', 30)
            .style('fill', 'gray')
            .style('border', '1px black solid');

        svg
            .append('g')
            .append('text')
            .text('Concept Patch | Spectrogram')
            .attr('x', 30 + (2 * svg_attributes.width/3))
            .attr('y', 30)
            .style('fill', 'gray')
            .style('border', '1px black solid');

        props.setSelectedSongs(imageData);

        if(props.hoverSong !== null) {
            console.log('Hover song name is: ', props.hoverSong);
            let selection = svg.selectAll('.imageBorder');
            console.log('Image border selection ', selection);
                
            selection
                // .selectAll('.imageBorder')
                // .data(trackNames)
                .attr('stroke', function(d, i) {
                    let hoverSongName = props.hoverSong.split('|')[0];
                    console.log('Song name extracted is: ', hoverSongName);
                    if(d === hoverSongName) {
                        console.log('Setting stroke yellow.')
                        return 'yellow';
                    }
                    return 'none'
                })
                .attr('stroke-width', 2);
        }
        else {
            console.log('Hover song name now is: ', props.hoverSong);
            svg
                .selectAll('.imageBorder')
                // .data(imageData)
                .style('stroke', 'none')
        }

        }
    }, [trackNames, props.hoverSong]);

    // console.log('Before returning from Image panel.');

    return (
        <React.Fragment>
            <svg ref={imageSvgRef} style={{ height: '100%', width: '100%' }} id={props.id}>
            </svg>
        </React.Fragment>
    )

}

export default ImagePanel;