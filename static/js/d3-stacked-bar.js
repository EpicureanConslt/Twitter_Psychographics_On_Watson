var margin = {top: 20, left: 100, bottom: 30, right:50},
	width = 1000 - margin.left - margin.right,
	height = 350 - margin.top - margin.bottom;
		
var x = d3.scale.ordinal()
	.rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
	.rangeRound([height, 0]);

var color = d3.scale.ordinal()
	.range(["#935347", "#006666", "#1E8BC3", "#cdd422", "#677077", "#cc9900", ]);

var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom");

var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left")
	.tickFormat(d3.format(".2s"));

var div = d3.select("#body1").append("div")	
	.attr("class", "tooltip")				
	.style("opacity", 0);

var svg = d3.select("#body1").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
d3.csv("static/d3input.csv?nocache=" + (new Date()).getTime(), function(error, data) {
	if (error) throw error;

	color.domain(d3.keys(data[0]).filter(function(key) { return key !== "trait"; }));

	data.forEach(function(d) {
			var y0 = 0;
			d.values = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
			d.total = d.values[d.values.length - 1].y1;
	});

	x.domain(data.map(function(d) { return d.trait; }));
	y.domain([0, d3.max(data, function(d) { return d.total; })]);

	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	svg.append("g")
		.attr("class", "y axis")
		.call(yAxis)
		.append("text")
		.attr("y", -15)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("Percentile");

	var trait = svg.selectAll(".trait")
		.data(data)
		.enter().append("g")
		.attr("class", "g")
		.attr("transform", function(d) { return "translate(" + x(d.trait) + ",0)"; });	

	trait.selectAll("rect")
		.data(function(d) { return d.values; })
		.enter().append("rect")
		.attr("width", x.rangeBand())
		.attr("y", function(d) { return y(d.y1); })
		.attr("height", function(d) { return y(d.y0) - y(d.y1); })
		.style("fill", function(d) { return color(d.name); })
		.style("stroke", "black");
			
	trait.each(function(dbar) {
		var bardiv = d3.select(this);
		bardiv.selectAll("rect")
		.on("mouseover", function(drect) { 
			div.transition()		
			   .duration(200)		
			   .style("opacity", .9);
			var stry = d3.select(this).datum().name;
			switch(bardiv.datum().trait+"|"+stry.substr(stry.length-1)) {
				case "Openness|1": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Adventurousness"
					break;
				case "Openness|2": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Artistic Interests"
					break;
				case "Openness|3": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Emotionality"
					break;
				case "Openness|4": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Imagination"
					break;
				case "Openness|5": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Intellect"
					break;	
				case "Openness|6": 
					display_txt = "<i>Characteristic: </i>Openness<br/><i>Attribute: </i>Authority Challenging"
					break;
				case "Conscientiousness|1": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Achievement Striving"
					break;
				case "Conscientiousness|2": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Cautiousness"
					break;
				case "Conscientiousness|3": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Dutifulness"
					break;
				case "Conscientiousness|4": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Orderliness"
					break;
				case "Conscientiousness|5": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Self-Discipline"
					break;	
				case "Conscientiousness|6": 
					display_txt = "<i>Characteristic: </i>Conscientiousness<br/><i>Attribute: </i>Self-Efficacy"
					break;	
				case "Extroversion|1": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Activity Level"
					break;
				case "Extroversion|2": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Assertiveness"
					break;
				case "Extroversion|3": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Cheerfulness"
					break;
				case "Extroversion|4": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Excitement-Seeking"
					break;
				case "Extroversion|5": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Outgoing"
					break;	
				case "Extroversion|6": 
					display_txt = "<i>Characteristic: </i>Extroversion<br/><i>Attribute: </i>Gregariousness"
					break;	
				case "Agreeableness|1": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Altruism"
					break;
				case "Agreeableness|2": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Co-operation"
					break;
				case "Agreeableness|3": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Modesty"
					break;
				case "Agreeableness|4": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Uncompromising"
					break;
				case "Agreeableness|5": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Sympathy"
					break;	
				case "Agreeableness|6": 
					display_txt = "<i>Characteristic: </i>Agreeableness<br/><i>Attribute: </i>Trust"
					break;
				case "Emotional Range|1": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Fiery"
					break;
				case "Emotional Range|2": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Prone To Worry"
					break;
				case "Emotional Range|3": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Melancholy"
					break;
				case "Emotional Range|4": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Immoderation"
					break;
				case "Emotional Range|5": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Self-Consciousness"
					break;	
				case "Emotional Range|6": 
					display_txt = "<i>Characteristic: </i>Emotional Range<br/><i>Attribute: </i>Susceptible To Stress"
					break;									
				default:
					display_txt = "Error"
					break;
			}
			div	.html(display_txt)	
				.style("left", (d3.event.pageX) + "px")		
				.style("top", (d3.event.pageY - 28) + "px");	
		})
		.on("mouseout", function(drect) {		
			div.transition()		
			   .duration(500)		
			   .style("opacity", 0);	
		});
	});
});