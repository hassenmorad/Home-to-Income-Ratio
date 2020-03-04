def chart_theme():
    font = "Lato"
    fontsize = 16
    padding = 40
    return {
        "width": 600,
        "height": 400,
        "background": "white",
        "config": {
            "title": {
                "fontSize": 24,
		"anchor": "start",
		"font": font,
		"offset": 5
            },
	    "axisX": {
		"grid": False,
                "labelFont": font,
                "labelFontSize": fontsize,
		"labelAngle": 0,
		"labelPadding": 10,
                "ticks": False,
		"tickSize":5,
		"title": None, 
                "titleFont": font,
                "titleFontSize": fontsize,
		"titleFontWeight": "normal",
		"titleY": 30,
		"titleX": 280,
            },
            "axisY": {
		"grid": True,
		"gridOpacity": 1,
                "labelFont": font,
                "labelFontSize": fontsize,
                "labelLimit": 100,
		"labelAlign": "left",
		"labelPadding": 20,
                "ticks": False,
		"title": None,
                "titleFont": font,
                "titleFontWeight": "normal",
                "titleFontSize": fontsize,
                "titleAlign":"left",
                "titleAngle": 0, 
                "titleY": -20,
		"titleX": -20,
		"domainWidth": 0,
            },
            "view":{"strokeOpacity": 0,
            },
        }
    }

import altair as alt
alt.themes.register("chart_theme", chart_theme)
alt.themes.enable("chart_theme")