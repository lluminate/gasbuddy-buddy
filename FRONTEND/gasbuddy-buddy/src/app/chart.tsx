"use client"

import { TrendingUp } from "lucide-react"
import {Area, AreaChart, CartesianGrid, XAxis, YAxis} from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

import { useState, useEffect } from "react";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig

export function GasChart() {
  const [chartData, setChartData] = useState<any[] | undefined>(undefined);

  // reverse the order of the data
  useEffect(() => {
    fetch("http://192.168.0.102:5003/gas_prices")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new Error("Received non-JSON response");
        }
        return response.json();
      })
      .then((data) => setChartData(data.reverse()))
      .catch((error) => console.error("Error fetching chart data:", error));
  }, []);


    return (
    <Card>
      <CardHeader>
        <CardTitle>Gas Prices</CardTitle>
        <CardDescription>
          Price history for the last 30 days
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 12,
              right: 12,
                bottom: 60,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="last_updated"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) =>
                  new Date(value).toLocaleString("default", {
                    day: "numeric",
                    month: "short",
                    hour: "numeric",
                    minute: "numeric",
                    hour12: true,
                  })
                }
              tick={{ angle: -45, textAnchor: "end" }}
            />
                <YAxis domain={["auto", "auto"]}/>
              <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Area
              dataKey="price" // Replace "price" with the actual key for gas prices in your JSON response
              type="linear"
              fill="var(--color-desktop)"
              fillOpacity={0.4}
              stroke="var(--color-desktop)"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 font-medium leading-none">
              Place holder text <TrendingUp className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 leading-none text-muted-foreground">
              Place holder text
            </div>
          </div>
        </div>
      </CardFooter>
    </Card>
  )
}
