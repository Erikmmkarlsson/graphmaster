import { Component } from "react";
import Chart from "react-apexcharts";
import './Graphs.scss';
import { authFetch } from "../auth";

export default class Graphs extends Component {
  constructor(props) {
    super(props);

    get_data("temperature", "temperature");
/* Returns:
{
  "series": [
    {
      "columns": [
        "time",
        "temperature"
      ],
      "name": "temperature",
      "values": [
        [
          "2021-07-05T19:28:25.316467Z",
          24
        ],
        [
          "2021-07-05T19:28:28.839730Z",
          25
        ],
        [
          "2021-07-05T19:28:32.032686Z",
          27
        ]
      ]
    }
  ]
}

*/
    this.state = {
      options: {
        chart: {
          id: "basic-bar"
        },
        xaxis: {
          time: [1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998]
        }
      },
      series: [
        {
          name: "series-1",
          data: [30, 40, 45, 50, 49, 60, 70, 91]
        }
      ]
    };
  }

  render() {
    return (
      <div className="app">
        <div className="row">
          <div className="mixed-chart">
            <Chart
              options={this.state.options}
              series={this.state.series}
              type="line"
              width="500"
            />
          </div>
          <div className="mixed-chart">
          <Chart
              options={this.state.options}
              series={this.state.series}
              type="bar"
              width="500"
            /></div>
        </div>
      </div>
    );
  }
}

async function get_data(measurement, field){
  
  let opts = {
    'measurement': measurement,
    'field': field
}
  
  const requestOptions = {
    method: 'POST',
    body: JSON.stringify(opts)
  };

  const data = await authFetch("api/fetch", requestOptions);

  return data;
}
/*
async function send_data(){
  const requestOptions = {
    method: 'GET'
  };

  const response = await fetch("/api/writedata", requestOptions);


}*/

