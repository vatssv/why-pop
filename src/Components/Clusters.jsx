import React, { useState, useRef, useEffect } from 'react';
import * as d3 from 'd3';
import clusterDataPath from '..\\data\\all_concept_clusters.csv';
import { copyFileSync } from 'fs';

const Clusters = (props) => {
    const clusterSvgRef = useRef();
    const [clusterData, setClusterData] = useState(null);
    var selectedConcept = props.selectedConcept;

    useEffect(() => {
        if (clusterData === null) {
            Promise.all([d3.csv(clusterDataPath)])
                    .then(function(values) {
                        const data = values[0];
                        console.log('Cluster data just loaded: ', data);
                        data.forEach((element, index) => {
                            element['concept_cluster'] = +element['concept_cluster'];
                            element['cluster_center_x'] = +element['cluster_center_x'];
                            element['cluster_center_y'] = +element['cluster_center_y'];
                        });
                        // console.log('Cluster data before setter: ', data);
                        setClusterData(data);
                    })
        }
    }, []);

    useEffect(() => {
        if(clusterData != null) {
            console.log('Cluster data: ', clusterData);
            // console.log('distData', distData);
            // console.log('Similarity Data: ', similarityData);
            const clusterSvg = d3.select(clusterSvgRef.current)
                            // .attr('transform', `scale(1.5, 1)`)
                            .on('click', (event) => {
                                d3.selectAll('.circ')
                                        .style('fill', function(d, i) { 
                                            return props.typeColors[d.concept_name.split('_')[0]]; 
                                        });
                                
                                props.setSelectedConcept(null);
                                selectedConcept = null;
                                props.setSelectedSongs(null);
                                props.setSongsList([]);
                                d3.selectAll('#imagePanel').selectAll('*').remove();
                                d3.selectAll('#singleSongPanel').selectAll('*').remove();
                            });
            clusterSvg.attr('class', 'clusterSvg');
            clusterSvg.selectAll('*').remove();
            // svg.attr("class", "beeswarm-svg");
            // let sectors = Array.from(new Set(data.map((d) => d.id)));

            if(d3.select('.tooltip').empty()) {
            var tooltip = d3.select("body")
                        .append("div")
                        .attr('class', 'tooltip')
                        .style("opacity", 0);
            }

            // let sectors = ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock'];
            let width = clusterSvgRef.current.clientWidth;
            let height = clusterSvgRef.current.clientHeight;
            // console.log('Height and width are: ', height, width);
            // let gap = (width * 1.5) / 10;


            let xmin = clusterData.reduce((prev, curr) => prev < curr.cluster_center_x ? prev : curr.cluster_center_x, clusterData[0].cluster_center_x);
            let xmax = clusterData.reduce((prev, curr) => prev > curr.cluster_center_x ? prev : curr.cluster_center_x, clusterData[0].cluster_center_x);
            let ymin = clusterData.reduce((prev, curr) => prev < curr.cluster_center_y ? prev : curr.cluster_center_y, clusterData[0].cluster_center_y);
            let ymax = clusterData.reduce((prev, curr) => prev > curr.cluster_center_y ? prev : curr.cluster_center_y, clusterData[0].cluster_center_y);

            // console.log('ymin and ymax are: ', ymin, ymax);

            ymin = ymin - 50;
            ymax = ymax + 50;
            xmin = xmin - 50;
            xmax = xmax + 50;
            // ymin = ymin < 0.0 ? 0.0 : ymin;
            // ymax = ymax > 1.0 ? 1.0 : ymax;

            let xScale = d3.scaleLinear().domain([xmin, xmax]).range([50, width - 45]);
            let yScale = d3.scaleLinear().domain([ymin, ymax]).range([height - 20, 50]);
            let y_start = 20;
            // let Domain = d3.extent(distData.map((d) => d["tcav_score"]));
            // Domain = Domain.map((d) => d);
            // let size = d3.scaleLinear().domain(Domain).range([2, 8]);
            const yAxis = d3.axisLeft().scale(yScale).ticks(5).tickSize(clusterSvgRef.current.clientWidth - 100);
            const xAxis = d3.axisBottom().scale(xScale).tickPadding(5);
            // let selectedTaskId = data.filter(d => d['_id'] === props.task);
            const xAxisG = clusterSvg.append('g')
                .style("font-size", `1rem`)
                .attr('transform', `translate(20, ${height-55})`);

            const g = clusterSvg
                .append("g")
                .attr("transform", `translate(20, ${0})`); 

            const u = g.append('g')
                .selectAll(".circ")
                .data(clusterData)
                .enter()
                .append("circle")
                .attr("class", "circ")
                .style("fill", function(d, i) { 
                    return props.typeColors[d.concept_name.split('_')[0]]; 
                })
                .attr("r", (d) => 5)
                .attr("cx", (d) => {
                    return xScale(d.cluster_center_x); })
                .attr("cy", (d) => yScale(d.cluster_center_y))
                .on("mouseover", (event, d) => {
                    let tooltip = d3.select('div.tooltip');

                    tooltip.html("Concept Name: " + d.concept_name + " </br> " + "Concept Cluster: " + d.concept_cluster)
                            .style('top', (event.y + 25) + 'px')
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

                const yAxisG = clusterSvg.append('g').attr("transform", `translate(${width - 40}, ${y_start})`);

                // xAxisG.call(xAxis);
                // xAxisG.append('text')
                // .attr('class', 'label')
                // .attr('y', 50)
                // .attr('x', width/2)
                // .attr('text-anchor', 'middle')
                // .text("Genres")
                // .style("fill", "gray");
        
                // xAxisG.call(g => g.selectAll(".tick text")
                //         .attr("color", "gray"))
                //     .call(g => g.selectAll(".tick")
                //         .attr("color", "gray"))
                //     .call(g => g.selectAll(".domain").remove());

                // yAxisG.call(yAxis);
                // yAxisG.append('g')
                // .append('text')
                // .attr('class', 'label')
                // .attr('x', -height/2)
                // .attr('y', -40)
                // .attr('font-size', '16')
                // .attr('transform', `translate(${-clusterSvgRef.current.clientWidth+110}, 0) rotate(-90)`)
                // .attr('text-anchor', 'middle')
                // .text("Concept Importance")
                // .style("fill", "gray");
                
                // yAxisG
                // .call(g => g.select(".domain").remove())
                // .call(g => g.selectAll(".tick:not(:first-of-type) line")
                //     .attr("stroke-capacity", 0.5)
                //     .attr("stroke-dasharray", "5,10")
                //     .attr("stroke", "gray"))
                // .call(g => g.selectAll(".tick:first-of-type line")
                //     .attr("stroke", "gray"))
                // .call(g => g.selectAll(".tick text")
                //     .attr("color", "gray"));

                var  clusterDataCopy = clusterData;
                
                let simulation = d3.forceSimulation(clusterDataCopy)
                    .force('charge', d3.forceManyBody().strength(-1))
                    .force("x", d3.forceX((d) => {
                                // console.log('Pushing d to label center: ', d.label, label_averages[d.label].x);
                                // return width / 2;
                                return xScale(d.cluster_center_x);
                            })
                            .strength(0.3))
                    .force("y", d3.forceY(function (d) {
                                // return (height / 2) - 150;
                                return yScale(d.cluster_center_y);
                            })
                            .strength(0.3))
                    .force('collide', d3.forceCollide().radius(5))
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
    }, [clusterData]);

    return (
        <React.Fragment>
            <svg ref={clusterSvgRef} style={{ height: '98%', width: '98%' }} id={props.id}>
            </svg>
        </React.Fragment>
    )

}

export default Clusters;