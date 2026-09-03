import React, { useState, useRef, useEffect } from 'react';
import * as d3 from 'd3';
import cavData from '..\\data\\concepts_data.csv';
import neighbourData from '..\\data\\all_concept_clusters.csv';

const Concepts = (props) => {
    const svgRef = useRef();
    const [distData, setDistData] = useState(null);
    const [similarityData, setSimilarityData] = useState(null);
    var max_X = 0, max_Y = 0;
    var selectedConcept = null;
    // let data_array = new Array();

    // console.log('Data: ', distData, typeof distData, (typeof distData == 'undefined' || typeof distData == null));

    useEffect(() => {
        if (distData == null) {
            Promise.all([d3.csv(cavData), d3.csv(neighbourData)])
                .then(function(values) {
                    const data = values[0];
                    const neighbourData = values[1];
                    data.forEach((element, index) => {
                        element['tcav_score'] = +element['tcav_score'];

                    });
                    neighbourData.forEach((element, index) => {
                        element['concept_cluster'] = +element['concept_cluster'];
                    });
                    let mergedData = data.map((item, index) => {
                        neighbourData.forEach((item2, index) => {
                            if (item.concept_name === item2.concept_name) {
                                item['concept_cluster'] = item2['concept_cluster'];
                            }
                        });
                        return item;
                    })
                    setDistData(mergedData);
                    // setSimilarityData(neighbourData);
                })
        }
    });

    useEffect(() => {
        if(distData != null) {
            // console.log('distData', distData);
            // console.log('Similarity Data: ', similarityData);
            const svg = d3.select(svgRef.current)
                            // .attr('transform', `scale(1.5, 1)`)
                            .on('click', (event) => {
                                d3.selectAll('.circ')
                                        .style('fill', function(d, i) { 
                                            return props.typeColors[d.concept_name.split('_')[0]]; 
                                        });
                                
                                props.setSelectedConcept(null);
                                props.setSongsList([]);
                                selectedConcept = null;
                                props.setSelectedSongs(null);
                                d3.selectAll('#imagePanel').selectAll('*').remove();
                                d3.selectAll('#singleSongPanel').selectAll('*').remove();
                            });
            svg.attr('class', 'conceptSvg');
            svg.selectAll('*').remove();
            // svg.attr("class", "beeswarm-svg");
            // let sectors = Array.from(new Set(data.map((d) => d.id)));

            if(d3.select('.tooltip').empty()) {
            var tooltip = d3.select("body")
                        .append("div")
                        .attr('class', 'tooltip')
                        .style("opacity", 0);
            }

            let sectors = ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock'];
            let width = svgRef.current.clientWidth;
            let height = svgRef.current.clientHeight;
            // console.log('Height and width are: ', height, width);
            let gap = (width) / 10;
            let ymin = distData.reduce((prev, curr) => prev < curr.tcav_score ? prev : curr.tcav_score, distData[0].tcav_score);
            let ymax = distData.reduce((prev, curr) => prev > curr.tcav_score ? prev : curr.tcav_score, distData[0].tcav_score);

            ymin = ymin - 0.02;
            ymax = ymax + 0.02;
            ymin = ymin < 0.0 ? 0.0 : ymin;
            ymax = ymax > 1.0 ? 1.0 : ymax;

            let xCoords = sectors.map((d, i) => gap + i * gap);
            let xScale = d3.scaleOrdinal().domain(sectors).range(xCoords);
            let yScale = d3.scaleLinear().domain([ymin, ymax]).range([height - 45, 50]);
            let y_start = 20;
            let Domain = d3.extent(distData.map((d) => d["tcav_score"]));
            Domain = Domain.map((d) => d);
            let size = d3.scaleLinear().domain(Domain).range([2, 8]);
            const yAxis = d3.axisLeft().scale(yScale).ticks(5).tickSize(svgRef.current.clientWidth - 100);
            const xAxis = d3.axisBottom().scale(xScale).tickPadding(5);
            // let selectedTaskId = data.filter(d => d['_id'] === props.task);
            const xAxisG = svg.append('g')
                .style("font-size", `1rem`)
                .attr('transform', `translate(20, ${height-65})`);

            const g = svg
                .append("g")
                .attr("transform", `translate(20, ${y_start})`); 

            const u = g.append('g')
                .selectAll(".circ")
                .data(distData)
                .enter()
                .append("circle")
                .attr("class", "circ")
                .style("fill", function(d, i) { 
                    return props.typeColors[d.concept_name.split('_')[0]]; 
                })
                .attr("r", (d) => size(d["tcav_score"]))
                .attr("cx", (d) => {
                    return xScale(d.concept_name.split('_')[0]); })
                .attr("cy", (d) => yScale(d.tcav_score))
                .on("mouseover", (event, d) => {
                    let tooltip = d3.select('div.tooltip');

                    tooltip.html("Concept Name: " + d.concept_name + " </br> " + "TCAV Score: " + d.tcav_score
                            + " </br> " + "Concept Cluster: " + d.concept_cluster)
                            .style('top', (event.y - 100) + 'px')
                            .style('left', (event.x + 25) + 'px')
                            .style('position', 'fixed')
                            .style('fill', 'gray');

                    tooltip.transition()
                        .duration(50)
                        .style("opacity", 1);

                    if (selectedConcept === null) {
                        d3.selectAll('.circ')
                            .style('fill', function(c, i) {
                                if(c.concept_cluster === d.concept_cluster) {
                                    return props.typeColors[c.concept_name.split('_')[0]];
                                }
                                return 'gray';
                            })
                    }
                })
                .on("mouseleave", (event) =>{
                    let tooltip = d3.select('div.tooltip');
                    // d3.select(event.currentTarget).style("opacity", 1);
                    tooltip.transition().duration(50).style("opacity", 0);

                    if (selectedConcept === null) {
                        d3.selectAll('.circ')
                            .style('fill', function(d, i) { 
                                return props.typeColors[d.concept_name.split('_')[0]]; 
                            });
                    }
                })
                .on('click', function(event, d) {

                    d3.selectAll('.circ')
                        .style('fill', function(c, i) {
                            if(c.concept_name === d.concept_name) {
                                return props.typeColors[c.concept_name.split('_')[0]];
                            }
                            return 'gray';
                    })

                    selectedConcept = d.concept_name;

                    console.log('Clicked ', d.concept_name, typeof d.concept_name);
                    props.setSelectedConcept(d.concept_name);
                    console.log('Setting genre ', d.concept_name.split('_')[0]);
                    props.setSelectedGenre(d.concept_name.split('_')[0])
                    event.stopPropagation();
                    // props.imageToggle(true);
                });

                const yAxisG = svg.append('g').attr("transform", `translate(${width - 40}, ${y_start})`);

                xAxisG.call(xAxis);
                xAxisG.append('text')
                .attr('class', 'label')
                .attr('y', 50)
                .attr('x', width/2)
                .attr('text-anchor', 'middle')
                .text("Genres")
                .style("fill", "gray");
        
                xAxisG.call(g => g.selectAll(".tick text")
                        .attr("color", "gray"))
                    .call(g => g.selectAll(".tick")
                        .attr("color", "gray"))
                    .call(g => g.selectAll(".domain").remove());

                yAxisG.call(yAxis);
                yAxisG.append('g')
                .append('text')
                .attr('class', 'label')
                .attr('x', -height/2)
                .attr('y', -40)
                .attr('font-size', '16')
                .attr('transform', `translate(${-svgRef.current.clientWidth+110}, 0) rotate(-90)`)
                .attr('text-anchor', 'middle')
                .text("Concept Importance")
                .style("fill", "gray");
                
                yAxisG
                .call(g => g.select(".domain").remove())
                .call(g => g.selectAll(".tick:not(:first-of-type) line")
                    .attr("stroke-capacity", 0.5)
                    .attr("stroke-dasharray", "5,10")
                    .attr("stroke", "gray"))
                .call(g => g.selectAll(".tick:first-of-type line")
                    .attr("stroke", "gray"))
                .call(g => g.selectAll(".tick text")
                    .attr("color", "gray"));

                var distDataCopy = distData;
                
                let simulation = d3.forceSimulation(distDataCopy)
                    .force('charge', d3.forceManyBody().strength(-1))
                    .force("x", d3.forceX((d) => {
                                // console.log('Pushing d to label center: ', d.label, label_averages[d.label].x);
                                // return width / 2;
                                return xScale(d.concept_name.split('_')[0]);
                            })
                            .strength(0.1))
                    .force("y", d3.forceY(function (d) {
                                // return (height / 2) - 150;
                                return yScale(d.tcav_score);
                            })
                            .strength(0.3))
                    .force('collide', d3.forceCollide().radius(7))
                    // .stop()
                    // .force('center', d3.forceCenter(innerWidth / 2, (innerHeight - padding) / 2))
                    .alphaDecay(0)
                    .alpha(0.3)
                    .on('tick', () => {
                        u.
                            attr('cx', d => d.x)
                            .attr('cy', d => d.y);
                    });

                let init_decay = setTimeout(function () {
                    simulation.alphaDecay(0.1);
                }, 3000);
        }
    }, [distData]);

    return (
        <React.Fragment>
            <svg ref={svgRef} style={{ height: '98%', width: '170%' }} id={props.id}>
            </svg>
        </React.Fragment>
    )

}
//     useEffect(() => {
//         // console.log('In first use effect');
//         if (distData == null) {
//             // console.log('Now executing if block');
//             // const reader = new FileReader();
//             // console.log('Current location: ', $dirname);
//             Promise.all([d3.csv(data)])
//                     .then(function(values) {
//                         const data = values[0];
//                         // console.log('Data loaded from csv is: ', data);
//                         data.forEach((item, index) => {
//                             item['comp-1'] = +item['comp-1'];
//                             item['comp-2'] = +item['comp-2'];
//                             item['label'] = +item['label'];
//                             max_X = Math.max(max_X, item['comp-1']);
//                             max_Y = Math.max(max_X, item['comp-2']);
//                             // console.log('Now item is: ', item);
//                             // data_array.push(item);
//                         })
//                         setDistData(data.slice(0, 80));
//                     })
//             // setData(actual_data)});
//             // props.toggleChanger(false);
//         }
//     });   

//     useEffect(() => {
//         if (distData != null) {

//             // console.log('Data has changed');
//             // console.log('Data changed: ', distData);

//             const svg = d3.select(svgRef.current);
//             // svg.selectChild('g'). remove();
//             // svg.selectChild('circle').remove();
//             svg.selectAll('g').remove();

//             let coords = document.querySelector('svg').getBoundingClientRect();
//             // console.log('Svg coordinates are: ', coords);

//             let height = svgRef.current.clientHeight; //40 for padding
//             let width = svgRef.current.clientWidth; // 40 for padding
//             // console.log('Svg attributes are: ', height, width);
//             let padding = 40;
//             let innerHeight = height - (2 * padding);
//             let innerWidth = width - (2 * padding);
//             // console.log('Inner height and width are: ', innerHeight, innerWidth);

//             const g = svg.append('g').attr('class', 'dataContainer')
//                                         .attr('transform', `translate(${coords['x']}, ${20})`);
//             // console.log('svg is: ', svg);

//             let max_X = Number.NEGATIVE_INFINITY, max_Y = Number.NEGATIVE_INFINITY;
//             let min_X = Number.POSITIVE_INFINITY, min_Y = Number.POSITIVE_INFINITY;

//             let labels_reduced = {};

//             let data_array = new Array();
//             distData.forEach((item, index) => {
//                 max_X = Math.max(max_X, item['comp-1']);
//                 max_Y = Math.max(max_Y, item['comp-2']);
//                 min_X = Math.min(min_X, item['comp-1']);
//                 min_Y = Math.min(min_Y, item['comp-2']);
//                 // console.log('Item is: ', item);
//                 data_array.push(item);

//                 if(labels_reduced.hasOwnProperty(item.label)) {
//                     labels_reduced[item.label].comp_1.push(item['comp-1']);
//                     labels_reduced[item.label].comp_2.push(item['comp-2']);
//                 }
//                 else {
//                     labels_reduced[item.label] = {'comp_1': [item['comp-1']], 'comp_2': [item['comp-2']]};
//                 }
//             })

//             // console.log('Reduced to labels: ', labels_reduced);

//             let label_averages = {}

//             for(var l in labels_reduced){
//                 let c1 = labels_reduced[l].comp_1, c2 = labels_reduced[l].comp_2;
//                 // console.log('l, c1, c2: ', l, c1, c2);
//                 label_averages[l] = {'x': 0, 'y': 0};
//                 label_averages[l].x = c1.reduce((a, b) => a + b) / c1.length;
//                 label_averages[l].y = c2.reduce((a, b) => a + b) / c2.length;
//             }

//             // console.log('Class concept centers: ', label_averages);

//             // console.log('Data Array is: ', distData);

//             const xScale = d3.scaleLinear()
//                         .domain([min_X, max_X])
//                         .range([coords['x'] + padding, innerWidth]);

//             const yScale = d3.scaleLinear()
//                         .domain([min_Y, max_Y])
//                         .range([coords['x'] + innerWidth, - (2 * padding)]);

//             const yAxis = d3.axisLeft().scale(yScale).ticks(5).tickSize(svgRef.current.clientWidth - 100);
//             const xAxis = d3.axisBottom().scale(xScale).tickPadding(5);

//             const xG = svg.append('g')
//                         .attr('transform', `translate(${coords['x'] + padding - 30}, ${coords['y'] - padding + innerHeight - 30})`)
//                         .attr('class', 'xScale');
//             // xG.call(X);
//             // xG.call(xAxis)
//             //     .call(g => g.selectAll(".tick text")
//             //             .attr("color", "gray"))
//             //         .call(g => g.selectAll(".tick")
//             //             .attr("color", "gray"))
//             //         .call(g => g.selectAll(".domain")
//             //             .attr("color", "gray")
//             //             .attr("stroke", "gray"));

//             const yG = svg.append('g')
//                         .attr('transform', `translate(${coords['x'] + innerWidth}, ${0})`)
//                         .attr('class', 'yScale');
//             // yG.call(Y);
//             // yG.call(yAxis)
//             //     .call(g => g.select(".domain").remove())
//             //     .call(g => g.selectAll(".tick:not(:first-of-type) line")
//             //         .attr("stroke-capacity", 0.5)
//             //         .attr("stroke-dasharray", "5,10")
//             //         .attr("stroke", "gray"))
//             //     .call(g => g.selectAll(".tick:first-of-type line")
//             //         .attr("stroke", "gray"))
//             //     .call(g => g.selectAll(".tick text")
//             //         .attr("color", "gray"));

                
//             console.log('Maxes are: ', max_X, max_Y);
//             console.log('Mins are: ', min_X, min_Y);
//             // console.log('Data type: ', typeof distData, Object.keys(distData));

//             const u = g
//                     .selectAll('circle')
//                     .data(distData, (d, i) => {
//                         return d, i;
//                     })
//                     .enter()
//                     .append('circle')
//                     .classed("node", true)
//                     // .join('circle')
//                     .attr('r', 8)
//                     .attr('cx', (d) => {
//                         return xScale(d['comp-1']);
//                     })
//                     .attr('cy', (d) => {
//                         return yScale(d['comp-2']);
//                     })
//                     .attr('fill', (d) => { return props.taskColors[d.label]; })
//                     .attr('id', (d, i) => {return i;});

//             // let nodes = svg.selectAll(".node")
//             //                 .data(function(d, i) {
//             //                     return d;
//             //                 })
//             //                 .attr('id', i);
//             // console.log('u i is: ', u._groups[0]);

//             let simulation = d3.forceSimulation(data_array)
//                                 .force('charge', d3.forceManyBody().strength(-20))
//                                 .force("x", d3.forceX((d) => {
//                                             // console.log('Pushing d to label center: ', d.label, label_averages[d.label].x);
//                                             // return width / 2;
//                                             return xScale(label_averages[d.label].x);
//                                         })
//                                         .strength(0.05))
//                                 .force("y", d3.forceY(function (d) {
//                                             // return (height / 2) - 150;
//                                             return yScale(label_averages[d.label].y);
//                                         })
//                                         .strength(0.05))
//                                 .force('collide', d3.forceCollide().radius(9))
//                                 // .stop()
//                                 // .force('center', d3.forceCenter(innerWidth / 2, (innerHeight - padding) / 2))
//                                 .alphaDecay(0)
//                                 .alpha(0.3)
//                                 .on('tick', () => {
//                                     u.
//                                         attr('cx', d => d.x)
//                                         .attr('cy', d => d.y);
//                                 });

//             let init_decay = setTimeout(function () {
//                 simulation.alphaDecay(0.1);
//             }, 3000);
            

//             // const radius = 150 / Math.sqrt(10 + data)
//         }
//     }, [distData])

//     return (
//         <React.Fragment>
//             <svg ref={svgRef} style={{ height: '100%', width: '100%' }} id={props.id}>
//             </svg>
//         </React.Fragment>
//     )
// }

export default Concepts;