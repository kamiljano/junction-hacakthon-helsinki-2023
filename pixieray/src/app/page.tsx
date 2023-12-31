'use client';

import {useEffect, useState} from "react";
import {Afe, SSEData} from "./event";
import EyeChart, {EyeData} from "./EyeChart";
import ReactPlayer from "react-player";
import Angel from "./angel";

const MAX_ENTRIES_ON_CHART = 100;

const toEyeData = (afe: Afe): EyeData => ({
  timestamp: afe.i[1],
  position: afe.m[0]
});

export default function Home() {
  const urlParams = new URLSearchParams(window.location.search);
  const angels = urlParams.get('angels');
  const [data, setData] = useState<SSEData[]>([]);
  const [run, setRun] = useState<boolean>(true);
  let [blinks, setBlinks] = useState<number>(0);

  useEffect(() => {
    if (!run) {
      return;
    }
    const eventSource = new EventSource("http://localhost:8000/stream/driving", {
      withCredentials: true,
    });
    eventSource.addEventListener('data', (event) => {
      const record: SSEData = JSON.parse(event.data);

      if (record.raw.labels?.includes('blink') && (!data.length || !data[data.length - 1].raw.labels?.includes('blink'))) {
        setTimeout(() => {
          blinks = blinks + 1;
          setBlinks(blinks);
          console.log(blinks);
        }, 800);
      }

      data.push(record);

      if (data.length > MAX_ENTRIES_ON_CHART) {
        data.shift();
      }

      setData([...data]);
    })
    eventSource.onerror = (err) => {
      console.error(err);
      setRun(false);
    }
    return () => eventSource.close();
  }, [run]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-6">
      { angels && <Angel blinkCount={blinks}/> }
      <div className="grid grid-cols-2 gap-4">
        <div>
          <EyeChart eye="Left" data={data.map(d => toEyeData(d.raw.afe[0]))}/>
        </div>
        <div>
          <EyeChart eye="Right" data={data.map(d => toEyeData(d.raw.afe[1]))}/>
        </div>
        <div>
          <ReactPlayer url="http://localhost:3000/shortened_blinks.mp4" controls={false} width="100%" playing={!!data.length && run} volume={0} />
        </div>
        <div>
          <button className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded' onClick={() => {
            if (run) {
              setRun(false);
            } else {
              setData([]);
              setRun(true);
            }
          }}>Pause/Restart</button>

          <div className='text-4xl'>
            {
              data.length && data[data.length - 1].raw.labels?.join(', ')
            }
          </div>
        </div>
      </div>
    </main>
  )
}
