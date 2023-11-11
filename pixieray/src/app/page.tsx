'use client';

import {useEffect, useState} from "react";
import {Afe, SSEData} from "./event";
import EyeChart, {EyeData} from "@/app/EyeChart";

const MAX_ENTRIES_ON_CHART = 100;

const toEyeData = (afe: Afe): EyeData => ({
  timestamp: afe.i[1],
  position: afe.m[0]
});

export default function Home() {

  const [data, setData] = useState<SSEData[]>([]);

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/stream/driving", {
      withCredentials: true,
    });
    eventSource.addEventListener('data', (event) => {
      const record: SSEData = JSON.parse(event.data);
      console.log(record);
      data.push(record);

      if (data.length > MAX_ENTRIES_ON_CHART) {
        data.shift();
      }

      setData([...data])
    })
    eventSource.onerror = (err) => {
      console.error(err);
    }
    return () => eventSource.close();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <EyeChart eye="Left" data={data.map(d => toEyeData(d.raw.afe[0]))}/>
        </div>
        <div>
          <EyeChart eye="Right" data={data.map(d => toEyeData(d.raw.afe[1]))}/>
        </div>
      </div>
    </main>
  )
}
