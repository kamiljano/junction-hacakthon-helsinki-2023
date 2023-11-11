'use client';

import {useEffect, useState} from "react";
import { Chart } from "react-google-charts";
import {Afe, SSEData} from "@/app/event";

const MAX_ENTRIES_ON_CHART = 100;

const options = {
  chart: {
    title: "Sensors",
  },
};

const calculateOneEyeSum = (afe: Afe): number => {
  return afe.m[0][0] + afe.m[0][1] + afe.m[0][2] + afe.m[0][3] + afe.m[0][4] + afe.m[0][5];
}

const calculateSum = (afe: [Afe, Afe]): number => calculateOneEyeSum(afe[0]) + calculateOneEyeSum(afe[1]);

export default function Home() {

  const [data, setData] = useState<[number, number][]>([]);

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/stream/driving", {
      withCredentials: true,
    });
    eventSource.addEventListener('data', (event) => {
      const record: SSEData = JSON.parse(event.data);
      console.log(record);
      data.push([record.raw.afe[0].i[1], calculateSum(record.raw.afe)])

      if (data.length > MAX_ENTRIES_ON_CHART) {
        data.shift();
      }

      setData([...data ])
    })
    eventSource.onerror = (err) => {
      console.error(err);
    }
    return () => eventSource.close();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Chart
        chartType="Line"
        width="100%"
        height="400px"
        data={[
          [
            "Timestamp",
            "Sensor sum",
          ],
          ...data
        ]}
        options={options}
      />
    </main>
  )
}
