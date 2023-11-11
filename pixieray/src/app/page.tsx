'use client';

import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/stream/driving", {
      withCredentials: true,
    });
    eventSource.addEventListener('data', (event) => {
      console.log(JSON.parse(event.data));
    })
    eventSource.onerror = (err) => {
      console.error(err);
    }
    return () => eventSource.close();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">

    </main>
  )
}
