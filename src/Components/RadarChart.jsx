import React, { useState, useRef, useEffect } from 'react';
import * as d3 from 'd3';
import rawdata from '..\\data\\features.csv';
import radar from './RadarChart.js';
import { keys } from '@mui/system';

const RadarChart = (props) => {

    const radarSvgRef = useRef();
    const [featureData, setFeatureData] = useState(null);
    var num_samples = 5;
    let rows, columns = 0;
    rows = 2;
    columns = Math.ceil(num_samples / 2);

    // useScript('https://gist.github.com/nbremer/21746a9668ffdf6d8242.js');
    // console.log('Window: ', window);

    useEffect(() => {
        props.toggleLoading(true);
        if (props.selectedSongs != null) {
            // console.log('In first use effect');
            // if (featureData == null) {
                fetch('/features/' + props.genre + '/' + num_samples, {mode: 'no-cors'})
                    .then((res) => {
                        console.log('Response was: ', res);
                        return res.json()
                    })
                    .then((data) => {
                        data = data.data;
                        data = JSON.parse(data);
                        console.log('After parsing: ', data);
                        data = data.map((d) => {
                            var axes_array = new Array();
                            for(var k in d){
                                if( k === 'track_title') continue;
                                if( k === 'track_id') continue;
                                if( k === 'tempo') {
                                    axes_array.push({'axis': k, 'value': d[k]/280});
                                    continue;
                                }
                                axes_array.push({'axis': k, 'value': d[k]});
                            }
                            return {
                                className: d['track_title'] + '|' + d['track_id'],
                                axes: axes_array
                            }
                        })
                        console.log('Feature data after rearranging: ', data);
                        setFeatureData(data);
                    })
            // }
        }
        else {
            setFeatureData(null);
        }
        props.toggleLoading(false);
    }, [props.selectedSongs]);

    useEffect(() => {
        
        const radarSvg = d3.select(radarSvgRef.current);
        radarSvg.select('*').remove();
        radarSvg.select('.legend-group').remove();
        radarSvg.append('g').attr('id', 'mainRadarGroup');

        if(featureData != null) {
            console.log('Building radar chart');
            // console.log('id passed to radar: ', props.id);
            // console.log('Radar parent selection: ', d3.select('#'+props.id));
            let totalHeight = 400 //radarSvg.node().height; //20 for padding
            let totalWidth = 400 //radarSvg.node().width;
            // let root = Math.sqrt(num_samples);
            // let rows = root % 1 === 0 ? root : Math.floor(root)
            // let columns = root % 1 === 0 ? rows: rows + 1;
            let width = 300;// columns;
            let height = 200;//width;
            // console.log('Height and width for radar svg are: ', height, width);
            radarSvg.attr('id', 'panel3');
            var track_names = featureData.map((d) => d['className'].split('|')[0]);
            var track_id_format = d3.format("06d")
            var track_ids = featureData.map((d) => track_id_format(+d['className'].split('|')[1]));
            var radarData = featureData.map((d) => d['axes']);
            console.log('radar data: ', radarData);
            var chartNumber = 0;
            for (let i = 0; i < rows; i++) {
                for (let j = 0; j < columns; j++) {
                    if(chartNumber === radarData.length) {
                        break;
                    }
                    var options = {
                        w: width - 30,
                        h: height - 30,
                        margin: {top: 30, right: 30, bottom: 30, left: 30},
                        maxValue: 1,
                        xCenter: ((j * width) + (width/2 + 50)),
                        yCenter: ((i * height) + (height / 2) + (i % 2 == 0 ? 0 : 80) + 50)
                    }
                // console.log('Radar svg attr: ', radarSvg.attr('id'));
                    radar('panel3', [radarData[chartNumber]], options, radarSvg, track_names, track_ids, props, chartNumber);
                    chartNumber++;
                }
            }
        }
    }, [featureData]);

    return (
        <React.Fragment>
            {props.loading ? 
            <div className='loader-container'> 
                <div className='spinner'></div>
            </div> : <svg ref={radarSvgRef} style={{ height: '100%', width: (50 * columns) + '%' }}>
            </svg>}
        </React.Fragment>
    )
}

export default RadarChart;