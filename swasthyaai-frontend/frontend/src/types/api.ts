/**
 * These types are a direct mirror of the backend's Pydantic schemas
 * (backend/app/schemas/*.py). Keep them in sync manually — there are only a
 * handful of endpoints, so a generated client would be more machinery than
 * this project needs; if the API surface grows significantly, generating
 * these from the OpenAPI schema at `/api/v1/openapi.json` would be the next
 * step.
 */

// ---- Common -----------------------------------------------------------

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}

export interface AIExplanation {
  text: string;
  provider: string;
  grounded: boolean;
  disclaimer: string;
}

// ---- Auth ---------------------------------------------------------------

export type StaffRole = "phc_staff" | "district_officer" | "admin";

export interface CurrentStaff {
  id: string;
  email: string;
  full_name: string;
  role: StaffRole;
  phc_id: number | null;
  district_id: number | null;
}

// ---- Module 1: Dashboard --------------------------------------------------

export interface PHCOut {
  id: number;
  name: string;
  district_id: number;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  contact_phone: string | null;
}

export interface StockSummary {
  medicine_id: number;
  medicine_name: string;
  quantity: number;
  reorder_threshold: number;
  unit: string;
  is_low: boolean;
}

export interface BedSummary {
  ward_type: string;
  total_beds: number;
  occupied_beds: number;
  occupancy_rate: number;
}

export interface DoctorAttendanceSummary {
  doctor_id: number;
  doctor_name: string;
  specialization: string;
  status: "present" | "absent" | "leave" | "not_marked";
}

export interface FootfallSummary {
  date: string;
  department: string;
  count: number;
}

export type AlertType = "low_stock" | "bed_full" | "doctor_absent";
export type AlertSeverity = "low" | "medium" | "high" | "critical";

export interface AlertOut {
  id: number;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  resolved: boolean;
  created_at: string;
}

export interface DashboardSnapshot {
  phc: PHCOut;
  medicine_inventory: StockSummary[];
  beds: BedSummary[];
  doctor_attendance_today: DoctorAttendanceSummary[];
  footfall_last_7_days: FootfallSummary[];
  recent_alerts: AlertOut[];
}

// ---- Module 2: Inventory Intelligence -------------------------------------

export interface MedicineForecast {
  medicine_id: number;
  medicine_name: string;
  current_quantity: number;
  reorder_threshold: number;
  avg_daily_consumption: number;
  predicted_days_until_stockout: number | null;
  is_low_stock: boolean;
}

export interface RedistributionSuggestion {
  medicine_id: number;
  medicine_name: string;
  from_phc_id: number;
  from_phc_name: string;
  to_phc_id: number;
  to_phc_name: string;
  suggested_quantity: number;
}

export interface InventoryForecastResponse {
  phc_id: number;
  forecasts: MedicineForecast[];
}

export interface InventoryRecommendationResponse {
  phc_id: number;
  low_stock_forecasts: MedicineForecast[];
  redistribution_suggestions: RedistributionSuggestion[];
  explanation: AIExplanation;
}

export interface ConsumptionLogRequest {
  medicine_id: number;
  quantity_used: number;
}

// ---- Module 3: JanMitra ---------------------------------------------------

export type Gender = "male" | "female" | "other";
export type SocialCategory = "general" | "obc" | "sc" | "st";

export interface PatientProfile {
  age: number;
  gender: Gender;
  annual_income: number;
  social_category: SocialCategory;
  state: string;
  is_bpl_card_holder: boolean;
  is_pregnant: boolean;
  has_disability: boolean;
  occupation?: string | null;
  family_size?: number | null;
}

export interface SchemeDocumentOut {
  document_name: string;
  mandatory: boolean;
}

export type SchemeLevel = "central" | "state";

export interface SchemeOut {
  id: number;
  name: string;
  level: SchemeLevel;
  authority: string;
  description: string;
  benefits_summary: string;
  official_url: string | null;
  documents: SchemeDocumentOut[];
}

export interface ExtractProfileRequest {
  free_text: string;
}

export interface ExtractProfileResponse {
  profile: PatientProfile;
  provider: string;
  extraction_confidence_note: string;
}

export interface EligibilityCheckRequest {
  profile: PatientProfile;
  phc_id?: number | null;
}

export interface SchemeEligibilityResult {
  scheme: SchemeOut;
  is_eligible: boolean;
  matched_rules: string[];
  failed_rules: string[];
}

export interface EligibilityCheckResponse {
  results: SchemeEligibilityResult[];
  explanation: AIExplanation;
}

export type LanguageCode = "en" | "hi";

export interface CitizenQueryRequest {
  question: string;
  language: LanguageCode;
}

export interface CitizenQueryResponse {
  matched_schemes: SchemeOut[];
  explanation: AIExplanation;
}

// ---- Module 4: District Copilot --------------------------------------------

export interface DistrictOut {
  id: number;
  name: string;
  state: string;
}

export interface PHCStatusSummary {
  phc_id: number;
  phc_name: string;
  low_stock_medicine_count: number;
  doctor_absence_rate: number;
  bed_occupancy_rate: number;
  footfall_7day_total: number;
  open_alert_count: number;
  attention_score: number;
}

export interface DistrictSummaryResponse {
  district_id: number;
  district_name: string;
  phc_statuses: PHCStatusSummary[];
}

export interface CopilotQueryRequest {
  question: string;
}

export interface CopilotQueryResponse {
  summary: DistrictSummaryResponse;
  explanation: AIExplanation;
}

// ---- Module 5: Voice --------------------------------------------------------

export type VoiceMode = "citizen_scheme_query" | "inventory_query";

export interface VoiceQueryResponse {
  transcript: string;
  detected_language: string;
  matched_mode: VoiceMode;
  explanation: AIExplanation;
  audio_base64: string | null;
  audio_content_type: string;
}
