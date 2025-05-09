"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Ellipsis } from "lucide-react";

export default ({period, setPeriod}: {
  period: string;
  setPeriod: (value: string) => void;
}) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
            size="icon"
            variant="outline"
            className="rounded-full border-border/80 bg-background hover:bg-background text-muted-foreground/80 hover:text-foreground aria-expanded:text-foreground"
            aria-label="Open edit menu"
        >
          <Ellipsis className="size-4.5" size={18} aria-hidden="true"/>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-fit min-w-28">
        <DropdownMenuRadioGroup value={period} onValueChange={setPeriod}>
          <DropdownMenuRadioItem value="7">1 week</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="30">1 month</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="365">1 year</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
)