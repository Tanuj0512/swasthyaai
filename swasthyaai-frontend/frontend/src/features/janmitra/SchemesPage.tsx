import { useMemo, useState } from "react";
import { Search } from "lucide-react";

import { useSchemes } from "@/hooks/useJanMitra";
import { PageHeader } from "@/components/layout/PageHeader";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CardSkeleton } from "@/components/common/LoadingSkeletons";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { SchemeCard } from "@/features/janmitra/SchemeCard";

type LevelFilter = "all" | "central" | "state";

export function SchemesPage() {
  const { data, isLoading, isError, error, refetch } = useSchemes();
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState<LevelFilter>("all");

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter((scheme) => {
      const matchesLevel = level === "all" || scheme.level === level;
      const matchesSearch =
        search.trim().length === 0 ||
        scheme.name.toLowerCase().includes(search.toLowerCase()) ||
        scheme.description.toLowerCase().includes(search.toLowerCase());
      return matchesLevel && matchesSearch;
    });
  }, [data, search, level]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <PageHeader
        title="All healthcare schemes"
        description="Central government and Maharashtra state schemes currently available"
      />

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search schemes..."
            className="pl-9"
          />
        </div>
        <Tabs value={level} onValueChange={(v) => setLevel(v as LevelFilter)}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="central">Central</TabsTrigger>
            <TabsTrigger value="state">State</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} lines={4} />
          ))}
        </div>
      )}

      {isError && <ErrorState error={error} onRetry={() => refetch()} />}

      {data && filtered.length === 0 && (
        <EmptyState title="No schemes match your search" description="Try a different keyword or clear the filter." />
      )}

      {data && filtered.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((scheme) => (
            <SchemeCard key={scheme.id} scheme={scheme} />
          ))}
        </div>
      )}
    </div>
  );
}
