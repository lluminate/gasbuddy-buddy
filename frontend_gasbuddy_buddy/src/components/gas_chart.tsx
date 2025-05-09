"use client";

import {useEffect, useState} from "react";
import {
    ResponsiveContainer,
    LineChart,
    Line,
    CartesianGrid,
    XAxis,
    YAxis,
    Legend
} from "recharts";

const getDailyTicks = (data: any[]) => {
    const seen = new Set();
    const ticks: number[] = [];

    data.forEach((entry) => {
        const date = new Date(entry.last_updated);
        const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime(); // ← number
        if (!seen.has(dayStart)) {
            seen.add(dayStart);
            ticks.push(dayStart);
        }
    });

    return ticks;
};


export default function Gas_chart() {
    const [groupedData, setGroupedData] = useState<Record<string, any[]> | null>(null);
    const [rawData, setRawData] = useState<any[]>([]);

    useEffect(() => {
        fetch("http://192.168.0.102:5003/api/gas_prices")
            .then((response) => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then((data) => {
                setRawData(data);
                // Convert date and group by station
                const transformed = data.map((item: any) => ({
                    ...item,
                    timestamp: new Date(item.last_updated).getTime()
                }));

                const grouped: Record<string, any[]> = {};
                transformed.forEach((item: { station_name: any; }) => {
                    const key = item.station_name; // or item.id if preferred
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(item);
                });

                setGroupedData(grouped);
            })
            .catch((error) => console.error("Error fetching chart data:", error));
    }, []);

    if (!groupedData) {
        return <div>Loading... Come back later.</div>;
    }

    // Custom tick formatter to only show month and day once
    const customTickFormatter = (() => {
        let lastDay = "";
        let lastMonth = -1;
        let lastYear = -1;

        return (value: number) => {
            const date = new Date(value);
            const day = date.getDate();
            const month = date.getMonth();
            const year = date.getFullYear();

            const dateKey = `${year}-${month}-${day}`;

            if (dateKey !== lastDay) {
                const showMonthYear = month !== lastMonth || year !== lastYear;
                lastDay = dateKey;
                lastMonth = month;
                lastYear = year;

                const options: Intl.DateTimeFormatOptions = {
                    month: "short",
                    day: "2-digit",
                };

                if (showMonthYear && year !== new Date().getFullYear()) {
                    options.year = "numeric";
                }

                return date.toLocaleDateString(undefined, options);
            }

            return "";
        };
    })();

    const ticks = getDailyTicks(rawData);

    return (
        <div className={""}>
            <ResponsiveContainer width={"100%"} height={400}>
                <LineChart>
                    <CartesianGrid vertical={false} strokeWidth={1}/>
                    <XAxis
                        type="number"
                        dataKey="timestamp"
                        scale="time"
                        domain={["auto", "auto"]}
                        ticks={ticks}
                        tickFormatter={customTickFormatter}
                        minTickGap={5}
                        tickMargin={12}
                    />
                    <YAxis
                        domain={["auto", "auto"]}
                        tickFormatter={(val) => `${val}¢`}
                    />
                    <Legend/>
                    {Object.entries(groupedData).map(([station, data], index) => (
                        <Line
                            key={station}
                            type="monotone"
                            data={data}
                            dataKey="price"
                            name={station}
                            stroke={["#8884d8", "#82ca9d", "#ff7300", "#ff0000"][index % 4]}
                            dot={false}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
