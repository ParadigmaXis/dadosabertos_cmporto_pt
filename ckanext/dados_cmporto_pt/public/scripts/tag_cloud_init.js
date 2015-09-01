
$(document).ready(function(){
	$("#tag_cloud").awesomeCloud({
		"size" : {
			"grid" : 16,
			"normalize" : false
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
