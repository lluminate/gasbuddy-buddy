import { LineChart, Line } from 'recharts';
import Gas_chart from "@/app/gas_chart";

export default function Home() {
    return (
        <div>
            <main>
                <Gas_chart />
            </main>
            <footer>test footer</footer>
        </div>
    );
}
