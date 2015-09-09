
$(document).ready(function(){
	$("#tag_cloud").awesomeCloud({
		"size" : {
			"grid" : 8,
			"factor" : 2,
			"normalize" : true
		},
		"options" : {
			"color" : "random-dark",
			"rotationRatio" : 0,
			"printMultiplier" : 3,
			"sort" : "highest"
		},
		"font" : "'Open Sans', 'Helvetica Neue', 'Helvetica', sans-serif",
		"shape" : "square"
	});
});
