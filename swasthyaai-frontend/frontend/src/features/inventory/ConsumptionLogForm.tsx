import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { PackagePlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { MedicineForecast } from "@/types/api";

const consumptionSchema = z.object({
  medicine_id: z.string().min(1, "Select a medicine"),
  quantity_used: z.coerce.number({ invalid_type_error: "Enter a quantity" }).int("Whole numbers only").positive("Must be greater than 0"),
});

type ConsumptionFormValues = z.infer<typeof consumptionSchema>;

interface ConsumptionLogFormProps {
  medicines: MedicineForecast[];
  onSubmit: (values: { medicine_id: number; quantity_used: number }) => Promise<void>;
  isSubmitting?: boolean;
}

export function ConsumptionLogForm({ medicines, onSubmit, isSubmitting }: ConsumptionLogFormProps) {
  const form = useForm<ConsumptionFormValues>({
    resolver: zodResolver(consumptionSchema),
    defaultValues: { medicine_id: "", quantity_used: 1 },
  });

  async function handleSubmit(values: ConsumptionFormValues) {
    await onSubmit({ medicine_id: Number(values.medicine_id), quantity_used: values.quantity_used });
    form.reset({ medicine_id: values.medicine_id, quantity_used: 1 });
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <FormField
          control={form.control}
          name="medicine_id"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormLabel>Medicine dispensed</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a medicine" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {medicines.map((m) => (
                    <SelectItem key={m.medicine_id} value={m.medicine_id.toString()}>
                      {m.medicine_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="quantity_used"
          render={({ field }) => (
            <FormItem className="w-full sm:w-32">
              <FormLabel>Quantity</FormLabel>
              <FormControl>
                <Input type="number" min={1} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isSubmitting} className="shrink-0">
          <PackagePlus className="h-4 w-4" />
          {isSubmitting ? "Logging..." : "Log usage"}
        </Button>
      </form>
    </Form>
  );
}
