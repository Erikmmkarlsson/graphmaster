import { Component } from "react";
import Chart from "react-apexcharts";
import './Graphs.scss';
import { authFetch } from "../auth";

export default class Graphs extends Component {
  constructor(props) {
    super(props);

    
    this.state = {
      options: {
        chart: {
          id: "basic-bar"
        },
        xaxis: {
          categories: [1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999]
        }
      },
      series: [
        {
          name: "series-1",
          data: [30, 40, 45, 50, 49, 60, 70, 91]
        }
      ]
    };

    
    get_data("temperature", "temperature")
    .then(state => {this.setState({
      options: state.options,
      series: state.series
    })
    });


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
  };



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
        </div>
      </div>
    );
  }
}



async function get_data(measurement, field) {

  let opts = {
    'measurement': measurement,
    'field': field
  }

  const requestOptions = {
    method: 'POST',
    body: JSON.stringify(opts)
  };

  const times = [];
  const values = [];

  await authFetch("api/fetch", requestOptions)
    .then(response => response.json())
    .then(data => {
      const timeseries = data.series[0].values;

      console.log(timeseries);
      for (const value of timeseries) {
        
        times.push(value[0]);
        values.push(value[1]);
      }

      console.log(times);
    });


  let state = {
    options: {
      chart: {
        id: measurement
      },
      xaxis: {
        categories: times
      }
    },

    series: [
      {
        name: field,
        data: values
      }
    ]
  };

  return state;
};



/*
async function send_data(){
  const requestOptions = {
    method: 'POST'
  };

  const response = await fetch("/api/writedata", requestOptions);


}*/

