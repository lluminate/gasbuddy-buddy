"use client"
import Gas_chart from "@/components/gas_chart";
import {Card, CardContent} from "@/components/ui/card";
import ThemeToggle from "@/components/theme-toggle";
import PeriodSelector from "@/components/period-selector";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import L from "leaflet";
import {useState, useEffect} from "react"
import {MapContainer, TileLayer, Marker, useMapEvents, useMap} from "react-leaflet"
import "leaflet/dist/leaflet.css"
import "leaflet-control-geocoder/dist/Control.Geocoder.css"
import "leaflet-control-geocoder"
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table"
import StationList from "@/components/station-list";

type GeocoderControlProps = {
    setMarker: React.Dispatch<React.SetStateAction<[number, number] | null>>;
};

const emojiIcon = new L.DivIcon({
    html: `<div style="font-size: 24px;">⛽️</div>`,
    className: "", // prevent default Leaflet styles
    iconSize: [24, 24],
    iconAnchor: [12, 24], // center the icon
});

function ClickToAddMarker({setMarker}: GeocoderControlProps) {
    useMapEvents({
        click(e) {
            setMarker([e.latlng.lat, e.latlng.lng]);
        },
    });
    return null;
}

// Helper function to map period to label
const getPeriodLabel = (period: string) => {
    switch (period) {
        case "7":
            return "1 week";
        case "30":
            return "1 month";
        case "365":
            return "1 year";
        default:
            return "Custom period"; // Default in case the period isn't one of the predefined ones
    }
};



export default function Home() {

    const [marker, setMarker] = useState<[number, number] | null>(null);
    const [period, setPeriod] = useState("7");
    const [newStationName, setNewStationName] = useState("");

    function handleAddStation() {
        if (marker && newStationName) {
            const requestOptions = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: newStationName.trim(),
                    latitude: marker[0],
                    longitude: marker[1],
                }),
            };
            console.log(requestOptions);
            fetch("http://192.168.0.102:5003/api/stations/add", requestOptions)
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error("Error adding station:", error));
            // Reset marker and station name after adding
            setNewStationName(" ");
        }
    }

    function GeocoderControl() {
        const map = useMap();

        useEffect(() => {
            if (!map) return;

            const geocoder = L.Control.geocoder({
                defaultMarkGeocode: false,
            })
                .on("markgeocode", function (e) {
                    const {center} = e.geocode;
                    setMarker([center.lat, center.lng]);
                    map.setView(center, 15);
                })
                .addTo(map);

            return () => {
                map.removeControl(geocoder);
            };
        }, [map]);

        return null;
    }

    return (
        <div className="px-6 py-20 min-h-svh flex flex-col justify-center bg-zinc-100 dark:bg-zinc-950">
            <div className="fixed top-4 right-4">
                <ThemeToggle/>
            </div>
            <div className="w-full max-w-6xl mx-auto">
                <div className="flex flex-col gap-6">
                    {/* Chart Area */}
                    <div className="flex-1 @container">
                        <Card className="shadow-2xl rounded-3xl border-transparent dark:border-border/64">
                            <CardContent>
                                {/* Header */}
                                <div className={"flex flex-col @xl:flex-row @xl:items-center gap-3 mb-6"}>
                                    {/* Left side */}
                                    <div className={"flex-1 flex gap-3"}>
                                        <div className="flex flex-col gap-0.5">
                                            <div className="text-xl font-semibold">
                                                GAS PRICES <span className="text-muted-foreground">:</span> REGULAR
                                            </div>
                                            <div className="text-[13px] text-muted-foreground/72 dark:text-muted-foreground/64 uppercase font-medium">
                                                {getPeriodLabel(period)}{" "}
                                                <span className="text-muted-foreground/40">·</span> PRC{" "}
                                                <span className="text-emerald-500"> 1,970.84 (+4.37%) </span>
                                                {/*TODO: remove PRC and add highest and lowest for period*/}
                                            </div>
                                        </div>
                                    </div>
                                    {/* Right side */}
                                    <div className={"flex items-center justify-between gap-2"}>
                                        <div className={"flex items-center gap-2"}>
                                        </div>
                                        <PeriodSelector period={period} setPeriod={setPeriod}/>
                                        {/*TODO: implement period changing*/}
                                    </div>
                                </div>
                                <Gas_chart/>
                            </CardContent>
                        </Card>
                    </div>
                    {/* Add Station Area */}
                    <div className={"flex-1 @container"}>
                        <div className={"flex flex-row gap-6"}>
                            <Card className="shadow-2xl rounded-3xl p-0 w-2/3">
                                <CardContent className={"p-0 z-5"}>
                                    <MapContainer
                                        center={[49.281922853936955, -123.12045878399663]}
                                        zoom={10}
                                        style={{height: "600px", width: "100%"}}
                                        className={"rounded-3xl border-transparent dark:border-border/64"}
                                    >
                                        <TileLayer
                                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                            url={'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'}
                                            className={"map-tiles"}
                                        />
                                        <ClickToAddMarker setMarker={setMarker}/>
                                        <GeocoderControl/>
                                        {marker && <Marker position={marker} icon={emojiIcon}/>}
                                    </MapContainer>
                                </CardContent>
                            </Card>
                            <Card className="shadow-2xl rounded-3xl w-1/3 border-transparent dark:border-border/64">
                                <CardContent>
                                    <div>
                                        <div className="*:not-first:mt-2">
                                            <h1 className="text-xl font-semibold">Add a New Station</h1>
                                            {marker ? (
                                                <div className="bg-background overflow-hidden rounded-md border">
                                                    <Table className={"text-center"}>
                                                        <TableBody>
                                                            <TableRow
                                                                className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                                                                <TableCell className="bg-muted/50 py-2 font-medium w-1/2">
                                                                    Latitude
                                                                </TableCell>
                                                                <TableCell className="py-2">
                                                                    {marker[0].toFixed(6)}
                                                                </TableCell>
                                                            </TableRow>
                                                            <TableRow
                                                                className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                                                                <TableCell className="bg-muted/50 py-2 font-medium w-1/2">
                                                                    Longitude
                                                                </TableCell>
                                                                <TableCell className="py-2">
                                                                    {marker[1].toFixed(6)}
                                                                </TableCell>
                                                            </TableRow>
                                                        </TableBody>
                                                    </Table>
                                                </div>
                                            ) : (
                                                <div className="bg-muted/50 rounded-md p-2 text-center border">
                                                    <p className="text-sm text-muted-foreground">
                                                        Click on the map to add a marker
                                                    </p>
                                                </div>
                                            )}
                                            <Label>Station Name<span className="text-destructive">*</span></Label>
                                            <div className="flex gap-2">
                                                <Input className="flex-1" placeholder="Fuel Station" type="text" required value={newStationName} onChange={(e) => setNewStationName(e.target.value)}/>
                                                <Button variant="outline" onClick={handleAddStation}>Add</Button>
                                            </div>
                                            <div className={"z-1000"}>
                                                <StationList setMarker={setMarker}/>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
