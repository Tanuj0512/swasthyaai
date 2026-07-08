import { config, type SupportedLanguageCode } from "@/config";
import { cn } from "@/lib/utils";

interface LanguageToggleProps {
  value: SupportedLanguageCode;
  onChange: (lang: SupportedLanguageCode) => void;
  className?: string;
}

export function LanguageToggle({ value, onChange, className }: LanguageToggleProps) {
  return (
    <div className={cn("inline-flex items-center rounded-full border border-border bg-secondary p-1", className)} role="group" aria-label="Choose language">
      {config.supportedLanguages.map((lang) => (
        <button
          key={lang.code}
          type="button"
          onClick={() => onChange(lang.code)}
          aria-pressed={value === lang.code}
          className={cn(
            "rounded-full px-3 py-1 text-sm font-medium transition-colors",
            value === lang.code ? "bg-primary-700 text-white shadow-sm" : "text-muted-foreground hover:text-ink-900"
          )}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
