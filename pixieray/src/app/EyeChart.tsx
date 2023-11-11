import {EyePosition, TimestampInMicroseconds} from "@/app/event";
import {Chart} from "react-google-charts";

export interface EyeData {
  timestamp: TimestampInMicroseconds;
  position: EyePosition;
}

interface EyeChartProps {
  eye: 'Left' | 'Right' | 'Both';
  data: EyeData[];
}

const calculateOneEyeSum = (pos: EyePosition): number => {
  let sum = 0;
  for (let i = 0; i < 6; i++) {
    sum += pos[i];
  }
  return sum;
}

export default function EyeChart(props: EyeChartProps) {
  return <Chart
    chartType="Line"
    width="100%"
    height="400px"
    data={[
      [
        "Timestamp",
        "Sensor sum",
      ],
      ...props.data.map(data => [Math.round(data.timestamp / 1000), calculateOneEyeSum(data.position)])
    ]}
    options={{
      chart: {
        title: props.eye === 'Both' ? 'Both eyes' : `${props.eye} eye`,
      },
    }}
  />
}
