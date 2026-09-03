/////////////////////////////////////////////////////////
/////////////// The Radar Chart Function ////////////////
/////////////// Written by Nadieh Bremer ////////////////
////////////////// VisualCinnamon.com ///////////////////
/////////// Inspired by the code of alangrafu ///////////
/////////////////////////////////////////////////////////

import * as d3 from 'd3';
// import event as d3event from 'd3';
	
const radar = function(id, data, options, svg, track_names, track_ids, props, songNumber) {
	// console.log('Data passed to radar chart is: ', data);
	if(Object.keys(data).length != 0) {
	var cfg = {
	 w: 300,				//Width of the circle
	 h: 200,				//Height of the circle
	 margin: {top: 20, right: 20, bottom: 20, left: 20}, //The margins of the SVG
	 levels: 3,				//How many levels or inner circles should there be drawn
	 maxValue: 0, 			//What is the value that the biggest circle will represent
	 labelFactor: 1.25, 	//How much farther than the radius of the outer circle should the labels be placed
	 wrapWidth: 60, 		//The number of pixels after which a label needs to be given a new line
	 opacityArea: 0.35, 	//The opacity of the area of the blob
	 dotRadius: 4, 			//The size of the colored circles of each blog
	 opacityCircles: 0.1, 	//The opacity of the circles of each blob
	 strokeWidth: 2, 		//The width of the stroke around each blob
	 roundStrokes: true,	//If true the area and stroke will follow a round path (cardinal-closed)
	 color: ['#00F5D4', '#355070', '#9b2226'],
	 xCenter: 300,
	 yCenter: 300
	};
	
	//Put all of the options into a variable called cfg
	if('undefined' !== typeof options){
	  for(var i in options){
		if('undefined' !== typeof options[i]){ cfg[i] = options[i]; }
	  }//for i
	}//if
	
	//If the supplied maxValue is smaller than the actual one, replace by the max in the data
	var maxValue = Math.max(cfg.maxValue, d3.max(data, function(i){return d3.max(i.map(function(o){return o.value;}));}));

	// console.log('Config options are: ', cfg);
		
	var allAxis = (data[0].map(function(i, j){return i.axis})),	//Names of each axis
		total = allAxis.length,					//The number of different axes
		radius = Math.min(cfg.w/2, cfg.h/2), 	//Radius of the outermost circle
		Format = d3.format('.1%'),			 	//Percentage formatting
		angleSlice = Math.PI * 2 / total;		//The width in radians of each "slice"
	
	//Scale for the radius
	var rScale = d3.scaleLinear()
		.range([cfg.margin.left + 10, radius])
		.domain([0, maxValue]);
		
	/////////////////////////////////////////////////////////
	//////////// Create the container SVG and g /////////////
	/////////////////////////////////////////////////////////

	//Remove whatever chart with the same id/class was present before
	// d3.select(id).select("svg").remove();
	
	//Initiate the radar chart SVG
	// var svg = d3.select(id)
	var mainGroup = svg
						.selectAll('#mainRadarGroup');
			// .attr("width",  cfg.w + cfg.margin.left + cfg.margin.right)
			// .attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
			// .attr("class", "radar"+id);

	// var el = document.getElementsByClassName('radar'+id);
	// console.log('El is: ', el[0]);
	// var boundaryRect = el[0].getBoundingClientRect();
	var xCenter = cfg.xCenter;
	var yCenter = cfg.yCenter;

	// console.log('Selected svg: ', svg);
	// console.log('w and h are: ', cfg.w/2, cfg.h/2, cfg.margin.left, cfg.margin.right);
	//Append a g element		
	var g = mainGroup.append("g")
			// .attr("transform", `translate(${cfg.w/2 + cfg.margin.left + cfg.margin.right}, ${cfg.h/2 + cfg.margin.top + cfg.margin.bottom})`);
			.attr("transform", `translate(${xCenter}, ${yCenter - 20})`);

	g.attr('id', 'radarChartGroup');
	
	/////////////////////////////////////////////////////////
	////////// Glow filter for some extra pizzazz ///////////
	/////////////////////////////////////////////////////////
	
	//Filter for the outside glow
	var filter = g.append('defs').append('filter').attr('id','glow'),
		feGaussianBlur = filter.append('feGaussianBlur').attr('stdDeviation','2.5').attr('result','coloredBlur'),
		feMerge = filter.append('feMerge'),
		feMergeNode_1 = feMerge.append('feMergeNode').attr('in','coloredBlur'),
		feMergeNode_2 = feMerge.append('feMergeNode').attr('in','SourceGraphic');

	/////////////////////////////////////////////////////////
	/////////////// Draw the Circular grid //////////////////
	/////////////////////////////////////////////////////////
	
	//Wrapper for the grid & axes
	var axisGrid = g.append("g").attr("class", "axisWrapper");
	
	//Draw the background circles
	axisGrid.selectAll(".levels")
	   .data(d3.range(1,(cfg.levels+1)).reverse())
	   .enter()
		.append("circle")
		.attr("class", "gridCircle")
		.attr("r", function(d, i){return radius/cfg.levels*d;})
		.style("fill", "#CDCDCD")
		.style("stroke", "#CDCDCD")
		.style("fill-opacity", cfg.opacityCircles)
		.style("filter" , "url(#glow)");

	//Text indicating at what % each level is
	// axisGrid.selectAll(".axisLabel")
	//    .data(d3.range(1,(cfg.levels+1)).reverse())
	//    .enter().append("text")
	//    .attr("class", "axisLabel")
	//    .attr("x", 4)
	//    .attr("y", function(d){return -d*radius/cfg.levels;})
	//    .attr("dy", "0.4em")
	//    .style("font-size", "10px")
	//    .attr("fill", "#737373")
	//    .text(function(d,i) { return Format(maxValue * d/cfg.levels); });

	/////////////////////////////////////////////////////////
	//////////////////// Draw the axes //////////////////////
	/////////////////////////////////////////////////////////
	
	//Create the straight lines radiating outward from the center
	var axis = axisGrid.selectAll(".axis")
		.data(allAxis)
		.enter()
		.append("g")
		.attr("class", "axis");
	//Append the lines
	axis.append("line")
		.attr("x1", 0)
		.attr("y1", 0)
		.attr("x2", function(d, i){ return rScale(maxValue*1.1) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("y2", function(d, i){ return rScale(maxValue*1.1) * Math.sin(angleSlice*i - Math.PI/2); })
		.attr("class", "line")
		.style("stroke", "white")
		.style("stroke-width", "2px");

	//Append the labels at each axis
	axis.append("text")
		.attr("class", "legend")
		.style("font-size", "11px")
		.attr("text-anchor", "middle")
		.attr("dy", "0.35em")
		.attr("x", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("y", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.sin(angleSlice*i - Math.PI/2); })
		.text(function(d){return d})
		.call(wrap, cfg.wrapWidth);

	/////////////////////////////////////////////////////////
	///////////// Draw the radar chart blobs ////////////////
	/////////////////////////////////////////////////////////
	
	//The radial line function
	var radarLine = d3.lineRadial()
		.curve(d3.curveBasisClosed)
		.radius(function(d) { return rScale(d.value); })
		.angle(function(d,i) {	return i*angleSlice; });
		
	if(cfg.roundStrokes) {
		radarLine.curve(d3.curveCardinalClosed);
	}
				
	//Create a wrapper for the blobs	
	var blobWrapper = g.selectAll(".radarWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarWrapper")
		.attr("id", function(d, i) { return 'song_' + String(songNumber); });
			
	//Append the backgrounds	
	blobWrapper
		.append("path")
		.attr("class", "radarArea")
		.attr("d", function(d,i) { return radarLine(d); })
		.style("fill", function(d,i) { let id = d3.select(this).node().parentNode.id.split('_')[1]; return cfg.color[id]; })
		.style("fill-opacity", cfg.opacityArea)
		.on('mouseover', function (event, d,i){
			//Dim all blobs
			d3.selectAll(".radarArea")
				.transition().duration(200)
				.style("fill-opacity", 0.1); 
			//Bring back the hovered over blob
			d3.select(this)
				.transition().duration(200)
				.style("fill-opacity", 0.7);

			let tooltip = d3.select('div.tooltip');

			// let selection = d3.select(this);

			// console.log('track names: ', track_names, typeof this);

			let id = d3.select(this).node().parentNode.id.split('_')[1];

			tooltip.html("Song Name: " + track_names[songNumber])
					.style('top', (event.y + 25) + 'px')
					.style('left', (event.x + 25) + 'px')
					.style('position', 'fixed')
					.style('fill', 'gray');

			tooltip.transition()
				.duration(50)
				.style("opacity", 1);

			props.toggleHoverSong(track_names[id] + '|' + track_ids[id])
		})
		.on('mouseout', function(){
			//Bring back all blobs
			d3.selectAll(".radarArea")
				.transition().duration(200)
				.style("fill-opacity", cfg.opacityArea);

			let tooltip = d3.select('div.tooltip');
			// d3.select(event.currentTarget).style("opacity", 1);
			tooltip.transition().duration(50).style("opacity", 0);
			props.toggleHoverSong(null);
		})
		.on('click', function(event, d, i) {
			let id = d3.select(this).node().parentNode.id.split('_')[1];
			props.setSong(track_names[id] + '|' + track_ids[id]);
			console.log('Setting selector value as: ', track_names[id] + '|' + +track_ids[id].toString());
			document.getElementById('songSelector').value = track_names[id] + '|' + +track_ids[id].toString();
			// console.log('Clicked on track id and song: ', track_ids[id], track_names[id]);
		});
		
	//Create the outlines	
	blobWrapper.append("path")
		.attr("class", "radarStroke")
		.attr("d", function(d,i) { return radarLine(d); })
		.style("stroke-width", cfg.strokeWidth + "px")
		.style("stroke", function(d,i) { let id = d3.select(this).node().parentNode.id.split('_')[1]; return cfg.color[id]; })
		.style("fill", "none")
		.style("filter" , "url(#glow)");		
	
	//Append the circles
	// console.log('Blob wrapper is a: ', blobWrapper, typeof blobWrapper);
	blobWrapper.selectAll(".radarCircle")
		.data(function(d,i) { return d; })
		.enter().append("circle")
		.attr("class", "radarCircle")
		.attr("r", cfg.dotRadius)
		.attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
		.style("fill", function(d,i,j) { let id = d3.select(this).node().parentNode.id.split('_')[1]; return cfg.color[id]; })
		.style("fill-opacity", 0.8);

	/////////////////////////////////////////////////////////
	//////// Append invisible circles for tooltip ///////////
	/////////////////////////////////////////////////////////
	
	//Wrapper for the invisible circles on top
	var blobCircleWrapper = g.selectAll(".radarCircleWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarCircleWrapper")
		.attr("id", function(d, i) { return 'circle_' + String(i); });
		
	//Append a set of invisible circles on top for the mouseover pop-up
	blobCircleWrapper.selectAll(".radarInvisibleCircle")
		.data(function(d,i) { return d; })
		.enter().append("circle")
		.attr("class", "radarInvisibleCircle")
		.attr("r", cfg.dotRadius*1.5)
		.attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
		.style("fill", "none")
		.style("pointer-events", "all")
		.on("mouseover", function(event, d,i) {
			var newX =  parseFloat(d3.select(this).attr('cx')) - 10;
			var newY =  parseFloat(d3.select(this).attr('cy')) - 10;

			var data = d3.select(this).data()
			console.log('This data: ', d3.select(this).data());
					
			let id = blobCircleWrapper.node().id.split('_')[1];
			// console.log('Id is: ', id);
			let tooltip = d3.select('div.tooltip');
			tooltip
				.style('top', (event.y + 25) + 'px')
				.style('left', (event.x + 25) + 'px')
				.text(Format(track_names[songNumber].value))
				.style('position', 'fixed')
				.style('fill', 'gray');

			tooltip.transition()
				.duration(50)
				.style("opacity", 1);
		})
		.on("mouseout", function(){
			let tooltip = d3.select('div.tooltip');
			tooltip.transition().duration(50)
				.style("opacity", 0);
		});

	console.log('Centers passed: ', cfg.xCenter, cfg.yCenter);
	blobCircleWrapper.append('text')
		.attr('x', 0)
		.attr('y', cfg.h/2 + 40)
		.text(track_names[songNumber])
		.style('fill', 'gray')
		.style('text-anchor', 'middle'); 
		
	// Add legend for radar chart

	// var size = 20;
	// svg.append('g')
	// 	.attr("transform", `translate(${20}, ${boundaryRect.height - boundaryRect.top - 20})`)
	// 	.attr('class', 'legend-group');

	// var legendGroup = d3.selectAll('.legend-group');

	// // console.log('Selection is: ', legendGroup);
	
	// legendGroup.selectAll('dots')
	// 	.data(track_names)
	// 	.enter()
	// 	.append('rect')
	// 	.attr('x', 0)
	// 	.attr('y', function(d, i) { return i*(size + 5)})
	// 	.attr('width', size)
	// 	.attr('height', size)
	// 	.style('fill', function(d, i) { return cfg.color[i]; });

	// legendGroup.selectAll('labels')
	// 	.data(track_names)
	// 	.enter()
	// 	.append('text')
	// 	.attr('x', size + 5)
	// 	.attr('y', function(d, i) { return 9 + i*(size + 5)})
	// 	.style('fill', 'gray')
	// 	.text(function(d) { return d; })
	// 	.style('alignment-baseline', 'middle');
	
	/////////////////////////////////////////////////////////
	/////////////////// Helper Function /////////////////////
	/////////////////////////////////////////////////////////

	//Taken from http://bl.ocks.org/mbostock/7555321
	//Wraps SVG text	
	function wrap(text, width) {
	  text.each(function() {
		var text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
			word,
			line = [],
			lineNumber = 0,
			lineHeight = 1.4, // ems
			y = text.attr("y"),
			x = text.attr("x"),
			dy = parseFloat(text.attr("dy")),
			tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
			
		while (word = words.pop()) {
		  line.push(word);
		  tspan.text(line.join(" "));
		  if (tspan.node().getComputedTextLength() > width) {
			line.pop();
			tspan.text(line.join(" "));
			line = [word];
			tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
		  }
		}
	  });
	}//wrap	
	}
	
}//RadarChart;

export default radar;