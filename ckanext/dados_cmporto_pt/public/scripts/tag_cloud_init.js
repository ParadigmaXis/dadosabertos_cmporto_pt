
$(document).ready(function(){
	$("#tag_cloud").awesomeCloud({
		"size" : {
			"grid" : 10,
			"factor" : 0,
			"normalize" : true
		},
		"options" : {
			"color" : "random-dark",
			"rotationRatio" : 0,
			"printMultiplier" : 1,
			"sort" : "highest"
		},
		"font" : "'Open Sans', 'Helvetica Neue', 'Helvetica', sans-serif",
		"shape" : "circle"
	});
});
