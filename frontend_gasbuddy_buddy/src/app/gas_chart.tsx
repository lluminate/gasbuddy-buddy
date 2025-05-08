"use client";

import {useEffect, useState} from "react";

export default function Gas_chart() {
    const [chartData, setChartData] = useState<any[] | undefined>(undefined);

    useEffect(() => {
        fetch("192.168.0.102:5003/api/gas_prices")
            .then((response) => {
                if(!response.ok) {
                    throw new Error (`HTTP error! status: ${response.status}`);
                }
                const contentType = response.headers.get("Content-Type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("Invalid content type");
                }
                return response.json();
            })
            .then((data) => setChartData(data))
            .catch((error) => console.error("Error fetching chart data:", error));
    }, []);

    if (!chartData) {
        return <div>Loading...</div>;
    }
    if (chartData.length === 0) {
        return <div>No data available</div>;
    }

    return (
        <div>
            <h1>Gas Prices</h1>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {chartData.map((data, index) => (
                        <tr key={index}>
                            <td>{data.date}</td>
                            <td>{data.price}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}