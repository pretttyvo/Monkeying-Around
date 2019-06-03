// Create color palette array
var colors = ['#FFDAB9', '#FFB533', '#AFEEEE', '#778899', '#B0C4DE'];

// Create function to pull data
async function live_trends(inputValue){ 

    // Retrieve data
    const live_trends_url = `/live_trends/${inputValue}`
    const live_trends_data = await d3.json(live_trends_url);

    // Print data
    console.log('return from py:',live_trends_data);

    return(live_trends_data)
}

// Select the submit button
var submit = d3.select("#submit");

submit.on("click", async function() {

    // Prevent the page from refreshing
    d3.event.preventDefault();

    // Select the input element and get the raw HTML node
    const inputElement = d3.select("#keywords");
    console.log(inputElement)
    // Get the value property of the input element
    const inputValue = inputElement.property("value");
    const mass_data_url = `/mass_data/${inputValue}`;
    // Retrieve data
    const time_data_url = `/live_trends/${inputValue}`;
    // const mass_product_url = `/mass_product/${inputValue}`;
    // const mass_revenue_url = `/mass_revenue/${inputValue}`;
    // const local_product_url = `/local_product/${inputValue}`;
    
    const time_data = await d3.json(time_data_url);
    console.log(time_data);
    
    const mass_data = await d3.json(mass_data_url);
    console.log(mass_data);
    
    // const mass_product_data = await d3.json(mass_product_url);
    // console.log(mass_product_data);
    // const mass_revenue_data = await d3.json(mass_revenue_url);
    // console.log(mass_revenue_data);
    // const local_product_data = await d3.json(local_product_url);
    // console.log(local_product_data);

    // Format date data
    const parseTime = d3.timeParse("%a, %d %b %Y 00:00:00 GMT");

    // Format date data
    var i;
    for (i = 0; i < time_data.date.length; i++) {
        time_data.date[i] = parseTime(time_data.date[i]);
    };
    
    // Create usable arrays for looping
    var input_array = inputValue.split(",");
    
    var chart_data = [];

// ---------------------------------------------------------------------------- //
// -------------------------------Google Trends-------------------------------- //
    // Create interest-over-time graph
    (function time_series(){
        for (i = 0; i < input_array.length; i++) {
            let trace_i = {
                type: "scatter",
                mode: "lines",
                name: input_array[i],
                y: time_data[input_array[i]],
                x: time_data.date,
                line: {color: colors[i]}
            };
            chart_data.push(trace_i);
        };

        let data = chart_data;

        let layout = {
            showlegend: false,
            autosize: true,
            height: 600,
            margin: {l: 25},
            yaxis: {
                range: [0, 100],
                showticklabels: true,
            }
        };

        Plotly.newPlot('time', data, layout);
    })();
    
    (function avg_plot(){
        let mean_data = [];
        let color_array = [];

        for (i=0; i < input_array.length; i++) {
            mean_i = d3.mean(time_data[input_array[i]]);
            mean_data.push(mean_i);
            color_array.push(colors[i]);
        };

        let data = [
            {
                x: input_array,
                y: mean_data,
                marker:{
                    color: color_array
                },
                type: "bar"
            }
        ];

        let layout = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, 100]
            }
        };

        Plotly.newPlot('avg', data, layout);
    })();
    // Plotly.purge("time");
    // Plotly.purge("avg");
    Plotly.purge("revenue");
    Plotly.purge("monthly");
    Plotly.purge("monthly_rev");
    Plotly.purge("monthly_unit");
    Plotly.purge("loc");
    Plotly.purge("glob");
    if (document.getElementById("table-area1").classList.contains('d-none')) {}
    else{
    document.getElementById("table-area1").classList.add('d-none'),
    document.getElementById("table-area2").classList.add('d-none');
    };
});
// ---------------------------------------------------------------------------- //
// ---------------------------------Global Trends------------------------------- //
// Create revenue graph
var globe = d3.select("#global");
globe.on("click", async function() {
    d3.event.preventDefault();

    // Select the input element and get the raw HTML node
    const inputElement = d3.select("#keywords");

    // Get the value property of the input element
    const inputValue = inputElement.property("value");
    var search_array = inputValue.split(",");
    search_array = search_array.map(x => x.trim())
    // pull in data
    const mass_data_url = `/mass_data/${inputValue}`;
    const mass_data = await d3.json(mass_data_url);
    console.log(mass_data);

    // pull in dataframe from scraped data
    let totalRevenueData = mass_data[1]
    var revenue_data = [];
    // let color_array = [];
    (function revenue_plot(){
        // let 
        
        for (i = 0; i < search_array.length; i++) {
            let sliceStart = (5*(i+1))-5;
            let sliceEnd = 5*(i+1);
            let trace_i = {
                type: "bar",
                name: search_array[i],
                y: totalRevenueData.revenue_value.slice(sliceStart, sliceEnd),
                x: totalRevenueData.revenue_specs.slice(sliceStart, sliceEnd),
                marker:{
                color: colors[i]
                },
            };
            revenue_data.push(trace_i);
        };

        let data = revenue_data;

        let layout = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, 100]
            },
            showlegend: true
        };
    Plotly.purge("time");
    Plotly.purge("avg");
    // Plotly.purge("revenue");
    Plotly.purge("monthly");
    Plotly.purge("monthly_rev");
    Plotly.purge("monthly_unit");
    Plotly.purge("loc");
    Plotly.purge("glob");
    if (document.getElementById("table-area1").classList.contains('d-none')) {}
    else{
    document.getElementById("table-area1").classList.add('d-none'),
    document.getElementById("table-area2").classList.add('d-none');
    };
        Plotly.newPlot('revenue', data, layout);
    })();
});

// ---------------------------------------------------------------------------- //
// ---------------------------------Monthly Global Trends------------------------------- //
// Create revenue graph
var mon_glo = d3.select("#monthly_global");
const place = ['1st', '2nd', '3rd', '4th', '5th'];
mon_glo.on("click", async function() {
    d3.event.preventDefault();

    // Select the input element and get the raw HTML node
    const inputElement = d3.select("#keywords");

    // Get the value property of the input element
    const inputValue = inputElement.property("value");
    var search_array = inputValue.split(",");
    search_array = search_array.map(x => x.trim())
    // pull in data
    const mass_data_url = `/mass_data/${inputValue}`;
    const mass_data = await d3.json(mass_data_url);
    console.log(mass_data);

    // pull in dataframe from scraped data
    let monthlyRevenue = mass_data[2]
    var monthRevenue_data = [];
    // let color_array = [];
    (function revenue_plot(){
        // let 
        // price
        for (i = 0; i < search_array.length; i++) {
            let sliceStart = (5*(i+1))-5;
            let sliceEnd = 5*(i+1);
            let trace_i = {
                type: "bar",
                name: search_array[i],
                y: monthlyRevenue.monthly_price.slice(sliceStart, sliceEnd),
                x: place,
                marker:{
                color: colors[i]
                },
            };
            monthRevenue_data.push(trace_i);
        };

        let data = monthRevenue_data;
        let maxPrice = Math.max(monthlyRevenue.monthly_price)
        let layout = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, maxPrice],
                title: "Price"
            },
            showlegend: true, 
            title: "Top Products",
            xaxis: {
                showgrid: true,
                showticklabels: false,
                title: "Top 5 Products"
            },
        };
        
        Plotly.purge("time"),
        Plotly.purge("avg"),
        Plotly.newPlot('monthly', data, layout);
    // revenue
    let month_rev = [];
    for (i = 0; i < search_array.length; i++) {
        let sliceStart = (5*(i+1))-5;
        let sliceEnd = 5*(i+1);
        let trace_i = {
            type: "bar",
            name: search_array[i],
            y: monthlyRevenue.monthly_revenue.slice(sliceStart, sliceEnd),
            x: place,
            marker:{
            color: colors[i]
            },
        };
        month_rev.push(trace_i);
    };

    let data1 = month_rev;
    let maxRev = Math.max(monthlyRevenue.monthly_revenue)
    let layout1 = {
        height: 600,
        margin: {r: 0},
        yaxis: {
            showgrid: true,
            showticklabels: false,
            range: [0, maxRev],
            title: "Revenue"
        },
        showlegend: true, 
        title: "Top Monthly Revenue",
        xaxis: {
            showgrid: true,
            showticklabels: false,
            title: "Top 5 Products"
        },
    };
    
    Plotly.purge("time"),
    Plotly.purge("avg"),
    Plotly.newPlot('monthly_rev', data1, layout1);
    
    let sales = []
    for (i = 0; i < search_array.length; i++) {
        let sliceStart = (5*(i+1))-5;
        let sliceEnd = 5*(i+1);
        let trace_i = {
            type: "bar",
            name: search_array[i],
            y: monthlyRevenue.monthly_sales.slice(sliceStart, sliceEnd),
            x: place,
            marker:{
            color: colors[i]
            }
        };
        sales.push(trace_i);
    };

    let data2 = sales;
    let maxUnits = Math.max(monthlyRevenue.monthly_sales)
    let layout2 = {
        height: 600,
        margin: {r: 0},
        yaxis: {
            showgrid: true,
            showticklabels: false,
            range: [0, maxUnits],
            title: "Units Sold"
        },
        showlegend: true, 
        title: "Top Sellers",
        xaxis: {
            showgrid: true,
            showticklabels: false,
            title: "Top 5 Products"
        },
    };
    
    Plotly.purge("time");
    Plotly.purge("avg");
    Plotly.purge("revenue");
    // Plotly.purge("monthly");
    // Plotly.purge("monthly_rev");
    // Plotly.purge("monthly_unit");
    Plotly.purge("loc");
    Plotly.purge("glob");
    if (document.getElementById("table-area1").classList.contains('d-none')) {}
    else{
    document.getElementById("table-area1").classList.add('d-none'),
    document.getElementById("table-area2").classList.add('d-none');
    };
    Plotly.newPlot('monthly_unit', data2, layout2);
    })();

});

// document.getElementById("table-area1").classList.add('d-none')
// ---------------------------------------------------------------------------- //
// ---------------------------------Comparison Trends------------------------------- //
// Create revenue graph
var local = d3.select("#comparison");

local.on("click", async function() {
    d3.event.preventDefault();

    // Select the input element and get the raw HTML node
    const inputElement = d3.select("#keywords");

    // Get the value property of the input element
    const inputValue = inputElement.property("value");
    var search_array = inputValue.split(",");
    search_array = search_array.map(x => x.trim())
    // pull in data
    const mass_data_url = `/mass_data/${inputValue}`;
    const mass_data = await d3.json(mass_data_url);
    console.log(mass_data);

    // pull in dataframe from scraped data
    let globalProd = mass_data[0]
    let localProd = mass_data[3]
    var loc_data = [];
    var glo_data = [];
    // let color_array = [];
    // function for local data
    const products_showing = ['First', 'Second', 'Third', 'Fourth', 'Fifth'];
    (function products_plot(){
        
        // local
        for (i = 0; i < search_array.length; i++) {
            let sliceStart = (5*(i+1))-5;
            let sliceEnd = 5*(i+1);
            let trace_i = {
                type: "bar",
                name: `${search_array[i]} local`,
                x: products_showing,
                y: localProd.product_price.slice(sliceStart, sliceEnd),
                marker:{
                color: colors[i]
                },
            };
            loc_data.push(trace_i);
        };
        // global
        for (i = 0; i < search_array.length; i++) {
            let sliceStart = (10*(i+1))-10;
            let sliceEnd = (10*(i+1))-5;
            let trace_i = {
                type: "bar",
                name: `${search_array[i]} global`,
                x: products_showing,
                y: globalProd.product_price.slice(sliceStart, sliceEnd),
                marker:{
                color: colors[i]
                },
            };
            glo_data.push(trace_i);
        };

        let data1 = loc_data;
        let data2 = glo_data;

        let maxPrice = Math.max(globalProd.product_price)

        let layout1 = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, maxPrice],
                title: "Price"
            },
            showlegend: true, 
            title: "Products Made Locally",
            xaxis: {
                showgrid: true,
                showticklabels: false,
                title: "Order of Products on Site"
            },
        };
        let layout2 = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, maxPrice],
                title: "Price"
            },
            showlegend: true, 
            title: "Products Made in Mass",
            xaxis: {
                showgrid: true,
                showticklabels: false,
                title: "Order of Products on Site"
            },
        };
        Plotly.purge("time"),
        Plotly.purge("avg")
        Plotly.newPlot('loc', data1, layout1);
        Plotly.newPlot('glob', data2, layout2);
    });
    
// let globalProd = mass_data[0]
// let localProd = mass_data[3]

// read data into the table
    var global_arrays = []
    for (i = 0; i < globalProd.product_name.length; i++) {
        global_array = [];
        global_array.push(globalProd.product_name[i]);
        global_array.push(globalProd.product_price[i]);
        global_array.push(globalProd.search_term[i]);
        console.log(globalProd.search_term[i]);
        global_arrays.push(global_array);
    };
    console.log(global_arrays);
    console.log("testing");
    const tbody = d3.select("#global_tbody");

    //  append to the table using a function to loop through all data
    global_arrays.forEach((product) =>{
        row = tbody.append("tr");
        for (key in product){
            const cell = tbody.append("td");
            cell.text(product[key]);
        };
    });
    document.getElementById("table-area1").classList.remove('d-none');
    document.getElementById("table-area2").classList.remove('d-none');
    var local_arrays = []
    for (i = 0; i < localProd.product_name.length; i++) {
        local_array = [];
        local_array.push(localProd.product_name[i]);
        local_array.push(localProd.product_price[i]);
        local_array.push(localProd.search_term[i]);
        console.log(localProd.search_term[i]);
        local_arrays.push(local_array);
    };
    console.log(local_arrays);
    console.log("testing");
    const tbody2 = d3.select("#local_tbody");

    //  append to the table using a function to loop through all data
    local_arrays.forEach((product) =>{
        row = tbody2.append("tr");
        for (key in product){
            const cell = tbody2.append("td");
            cell.text(product[key]);
        }
    })
    Plotly.purge("time");
    Plotly.purge("avg");
    Plotly.purge("revenue");
    Plotly.purge("monthly");
    Plotly.purge("monthly_rev");
    Plotly.purge("monthly_unit");
    // Plotly.purge("loc");
    // Plotly.purge("glob");
    // if (document.getElementById("table-area1").classList.contains('d-none')) {}
    // else{
    // document.getElementById("table-area1").classList.add('d-none'),
    // document.getElementById("table-area2").classList.add('d-none');
    // };
});

// -------------------------------------------------------------------------------- //
// ------------------Create function to call upon page load------------------------ //
(async function init(){

    // Retrieve data
    const time_data_url = '/init';
    const time_data = await d3.json(time_data_url);
    console.log(time_data);

    // Create a function to parse date and time
    const parseTime = d3.timeParse("%Y-%m-%d");

    // Format date data
    var i;
    for (i = 0; i < time_data.date.length; i++) {
        time_data.date[i] = parseTime(time_data.date[i]);
    };

    // Create inerest-over-time graph
    (function time_series(){
        let taco_trace = {
            type: "scatter",
            mode: "lines",
            name: 'Tacos',
            y: time_data.taco,
            x: time_data.date,
            line: {color: colors[0]}
        };

        let sandwich_trace = {
            type: "scatter",
            mode: "lines",
            name: 'Sandwiches',
            y: time_data.sandwich,
            x: time_data.date,
            line: {color: colors[1]}
        };

        let kebab_trace = {
            type: "scatter",
            mode: "lines",
            name: 'Kebabs',
            y: time_data.kebab,
            x: time_data.date,
            line: {color: colors[2]}
        };

        let data = [taco_trace, sandwich_trace, kebab_trace];

        let layout = {
            showlegend: false,
            autosize: true,
            height: 600,
            margin: {l: 25},
            yaxis: {
                range: [0, 100],
                showticklabels: true,
            }
        };

        Plotly.newPlot('time', data, layout);
    })();

    // Create average-interest graph
    (function avg_plot(){
        let data = [
            {
                x: ["Tacos", "Sandwiches", "Kebabs"],
                y: [d3.mean(time_data.taco),
                    d3.mean(time_data.sandwich),
                    d3.mean(time_data.kebab)],
                marker:{
                    color: [colors[0], colors[1], colors[2]]
                },
                type: "bar"
            }
        ];

        let layout = {
            height: 600,
            margin: {r: 0},
            yaxis: {
                showgrid: true,
                showticklabels: false,
                range: [0, 100]
            }
        };

        Plotly.newPlot('avg', data, layout);
    })();
})()