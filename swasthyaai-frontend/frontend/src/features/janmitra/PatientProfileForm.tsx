import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { PatientProfile } from "@/types/api";

const profileSchema = z.object({
  age: z.coerce.number().int().min(0, "Age can't be negative").max(120, "Enter a realistic age"),
  gender: z.enum(["male", "female", "other"]),
  annual_income: z.coerce.number().min(0, "Income can't be negative"),
  social_category: z.enum(["general", "obc", "sc", "st"]),
  state: z.string().min(2, "State is required"),
  is_bpl_card_holder: z.boolean(),
  is_pregnant: z.boolean(),
  has_disability: z.boolean(),
  occupation: z.string().optional(),
  family_size: z.coerce.number().int().positive().optional().or(z.literal(undefined)),
});

export type PatientProfileFormValues = z.infer<typeof profileSchema>;

interface PatientProfileFormProps {
  defaultValues?: Partial<PatientProfile>;
  onSubmit: (values: PatientProfile) => void;
  isSubmitting?: boolean;
  submitLabel?: string;
}

export function PatientProfileForm({ defaultValues, onSubmit, isSubmitting, submitLabel = "Check eligibility" }: PatientProfileFormProps) {
  const form = useForm<PatientProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      age: defaultValues?.age ?? 30,
      gender: defaultValues?.gender ?? "female",
      annual_income: defaultValues?.annual_income ?? 0,
      social_category: defaultValues?.social_category ?? "general",
      state: defaultValues?.state ?? "Maharashtra",
      is_bpl_card_holder: defaultValues?.is_bpl_card_holder ?? false,
      is_pregnant: defaultValues?.is_pregnant ?? false,
      has_disability: defaultValues?.has_disability ?? false,
      occupation: defaultValues?.occupation ?? undefined,
      family_size: defaultValues?.family_size ?? undefined,
    },
  });

  // When AI extraction produces a new profile after the form has already
  // mounted, reset the form to reflect it — this is what lets "Describe
  // patient" pre-fill the same form that manual entry uses.
  useEffect(() => {
    if (defaultValues) {
      form.reset({
        age: defaultValues.age ?? 30,
        gender: defaultValues.gender ?? "female",
        annual_income: defaultValues.annual_income ?? 0,
        social_category: defaultValues.social_category ?? "general",
        state: defaultValues.state ?? "Maharashtra",
        is_bpl_card_holder: defaultValues.is_bpl_card_holder ?? false,
        is_pregnant: defaultValues.is_pregnant ?? false,
        has_disability: defaultValues.has_disability ?? false,
        occupation: defaultValues.occupation ?? undefined,
        family_size: defaultValues.family_size ?? undefined,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultValues]);

  function handleSubmit(values: PatientProfileFormValues) {
    onSubmit({ ...values, occupation: values.occupation || null, family_size: values.family_size ?? null });
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            control={form.control}
            name="age"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Age</FormLabel>
                <FormControl>
                  <Input type="number" min={0} max={120} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="gender"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Gender</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="annual_income"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Annual household income (₹)</FormLabel>
                <FormControl>
                  <Input type="number" min={0} step={1000} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="social_category"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Social category</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="general">General</SelectItem>
                    <SelectItem value="obc">OBC</SelectItem>
                    <SelectItem value="sc">SC</SelectItem>
                    <SelectItem value="st">ST</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="state"
            render={({ field }) => (
              <FormItem>
                <FormLabel>State</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="family_size"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Family size (optional)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    min={1}
                    value={field.value ?? ""}
                    onChange={(e) => field.onChange(e.target.value === "" ? undefined : Number(e.target.value))}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="occupation"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Occupation (optional)</FormLabel>
              <FormControl>
                <Input value={field.value ?? ""} onChange={field.onChange} placeholder="e.g. Farmer, daily wage labourer" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid gap-4 rounded-md border border-border p-4 sm:grid-cols-3">
          <div className="flex items-center justify-between gap-3">
            <Label htmlFor="bpl-switch" className="text-sm font-normal">BPL card holder</Label>
            <Switch id="bpl-switch" checked={form.watch("is_bpl_card_holder")} onCheckedChange={(v) => form.setValue("is_bpl_card_holder", v)} />
          </div>
          <div className="flex items-center justify-between gap-3">
            <Label htmlFor="pregnant-switch" className="text-sm font-normal">Currently pregnant</Label>
            <Switch id="pregnant-switch" checked={form.watch("is_pregnant")} onCheckedChange={(v) => form.setValue("is_pregnant", v)} />
          </div>
          <div className="flex items-center justify-between gap-3">
            <Label htmlFor="disability-switch" className="text-sm font-normal">Has a disability</Label>
            <Switch id="disability-switch" checked={form.watch("has_disability")} onCheckedChange={(v) => form.setValue("has_disability", v)} />
          </div>
        </div>

        <Button type="submit" disabled={isSubmitting} className="w-full sm:w-auto">
          <ShieldCheck className="h-4 w-4" />
          {isSubmitting ? "Checking..." : submitLabel}
        </Button>
      </form>
    </Form>
  );
}
