import {Table, TableBody, TableCell, TableRow} from "@/components/ui/table";
import {Button} from "@/components/ui/button";
import {useEffect, useState} from "react";
import {TrashIcon, MapPin, CircleAlertIcon} from "lucide-react";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"


export default function StationList({setMarker}: {setMarker: (value:[number,number]) => void}) {
    const [stations, setStations] = useState<any[]>([]);
    const [stationTableKey, setStationTableKey] = useState(0);


    function handleDelete(stationId: number) {
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: stationId
            }),
        };
        fetch("http://192.168.0.102:5003/api/stations/remove", requestOptions)
            .then((response) => response.json())
            .then(data => {
                console.log(data);
            })
            .catch((error) => console.error("Error deleting station:", error));
        if (stationTableKey === 0) {
            setStationTableKey(1);
        } else {
            setStationTableKey(0);
        }
    }

    function handleLocate(latitude: number, longitude: number) {
        setMarker([latitude, longitude]);
    }

    useEffect(() => {
        fetch("http://192.168.0.102:5003/api/stations")
            .then(response => response.json())
            .then(data => {
                setStations(data);
                console.log("Fetched stations:", data);
            })
            .catch(error => console.error("Error fetching stations:", error));
    }, []);

    return (
        <div className="bg-background overflow-hidden rounded-md border">
            <Table key={stationTableKey}>
                <TableBody>
                    {stations.map((station) => (
                        <TableRow
                            key={station.id}
                            className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                            <TableCell className="bg-muted/50 py-2 font-medium">
                                <Button onClick={() => handleLocate(station.latitude, station.longitude)} variant={"ghost"}>
                                    {station.name}
                                </Button>
                            </TableCell>
                            <TableCell className="py-2 flex gap-2 items-center justify-end">
                                <div className={"flex w-full justify-center"}>
                                    <a href={`https://www.gasbuddy.com/station/${station.id}`} target="_blank" rel="noopener noreferrer">
                                        <Button variant={"link"}>{station.id}</Button>
                                    </a>
                                </div>

                                <AlertDialog>
                                    <AlertDialogTrigger asChild>
                                        <Button variant="destructive">
                                            <TrashIcon size={16}/>
                                        </Button>
                                    </AlertDialogTrigger>
                                    <AlertDialogContent>
                                        <div className="flex flex-col gap-2 max-sm:items-center sm:flex-row sm:gap-4">
                                            <div
                                                className="flex size-9 shrink-0 items-center justify-center rounded-full border"
                                                aria-hidden="true"
                                            >
                                                <CircleAlertIcon className="opacity-80" size={16}/>
                                            </div>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                                                <AlertDialogDescription>
                                                    Are you sure you want to delete {station.name}? All {station.name} price data will
                                                    be removed.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>
                                        </div>
                                        <AlertDialogFooter>
                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                            <AlertDialogAction onClick={() => {
                                                handleDelete(station.id)
                                            }}>Confirm</AlertDialogAction>
                                        </AlertDialogFooter>
                                    </AlertDialogContent>
                                </AlertDialog>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}